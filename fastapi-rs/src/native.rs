//! Python-free FastAPI service composition for Rust applications.
//!
//! This initial native surface registers Rust endpoint closures, delegates
//! route matching and parameter conversion to Starlette-RS's shared route
//! table, and exposes a Tower service for a Rust server. It is a deliberately
//! small Rust API; it does not claim parity with Python FastAPI's complete
//! validation, dependency-injection, Pydantic, or OpenAPI behavior.

use std::{
    convert::Infallible,
    error::Error,
    fmt::{self, Display, Formatter},
    future::Future,
    pin::Pin,
    str::FromStr,
    sync::Arc,
    task::{Context, Poll},
};

use bytes::Bytes;
use http::{
    HeaderMap, HeaderValue, Method, Request, Response, StatusCode, Uri, Version,
    header::{ALLOW, CONTENT_TYPE},
    request::Parts,
};
use http_body::Body;
use http_body_util::{BodyExt, Full, combinators::UnsyncBoxBody};
use serde::{Serialize, de::DeserializeOwned};
use starlette_rs::RouteError;
use tower_service::Service;

use crate::operation::{FastApiOperationMatch, FastApiOperationRouter};

/// A boxed error carried by a native request or response body.
pub type NativeBodyError = Box<dyn Error + Send + Sync + 'static>;

/// A pull-based request body delivered to a native Rust endpoint.
pub type NativeRequestBody = UnsyncBoxBody<Bytes, NativeBodyError>;

/// A pull-based response body returned from a native Rust endpoint.
pub type NativeResponseBody = UnsyncBoxBody<Bytes, NativeBodyError>;

/// An HTTP response returned by the native FastAPI service.
pub type NativeHttpResponse = Response<NativeResponseBody>;

/// The boxed future returned from [`Service::call`] by [`NativeApplication`].
pub type NativeServiceFuture =
    Pin<Box<dyn Future<Output = Result<NativeHttpResponse, Infallible>> + Send + 'static>>;

type EndpointFuture = Pin<Box<dyn Future<Output = NativeHttpResponse> + Send + 'static>>;
type Endpoint = dyn Fn(NativeRequest) -> EndpointFuture + Send + Sync + 'static;

struct PendingRoute {
    path: String,
    methods: Vec<String>,
    allow_header: Option<HeaderValue>,
    endpoint: Arc<Endpoint>,
}

/// Ordered registration for a Python-free Rust FastAPI service.
#[derive(Default)]
pub struct FastApiNativeBuilder {
    routes: Vec<PendingRoute>,
}

impl FastApiNativeBuilder {
    /// Creates a builder with no native routes.
    #[must_use]
    pub const fn new() -> Self {
        Self { routes: Vec::new() }
    }

    /// Registers a Rust endpoint for an ordered set of HTTP methods.
    ///
    /// Method names are normalized to uppercase. Route syntax, precedence,
    /// and captured path parameters use Starlette-RS's `RouteTable` through
    /// [`FastApiOperationRouter`]. The handler receives a streaming request;
    /// its body is not polled until the handler asks for frames.
    #[must_use]
    pub fn route<P, M, S, F, Fut>(mut self, path: P, methods: M, handler: F) -> Self
    where
        P: Into<String>,
        M: IntoIterator<Item = S>,
        S: AsRef<str>,
        F: Fn(NativeRequest) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = Result<NativeHttpResponse, NativeRequestError>> + Send + 'static,
    {
        let methods = methods
            .into_iter()
            .map(|method| method.as_ref().to_ascii_uppercase())
            .collect::<Vec<_>>();
        let allow_header = if methods.is_empty() {
            None
        } else {
            let allow = methods.join(", ");
            HeaderValue::from_str(&allow).ok()
        };
        let endpoint = Arc::new(move |request| {
            let future = handler(request);
            Box::pin(async move {
                match future.await {
                    Ok(response) => response,
                    Err(error) => error.into_response(),
                }
            }) as EndpointFuture
        });

        self.routes.push(PendingRoute {
            path: path.into(),
            methods,
            allow_header,
            endpoint,
        });
        self
    }

    /// Builds the server-neutral Tower service.
    ///
    /// Route paths and method declarations are validated during this call.
    /// The service creates no runtime or listener; the application supplies
    /// those through its chosen Rust server.
    ///
    /// # Errors
    ///
    /// Returns a route-registration error for an invalid Starlette path or an
    /// invalid HTTP method declaration.
    pub fn build(self) -> Result<NativeApplication, NativeApplicationError> {
        let mut router = FastApiOperationRouter::new();
        let mut endpoints = Vec::with_capacity(self.routes.len());
        let mut allow_headers = Vec::with_capacity(self.routes.len());

        for route in self.routes {
            for method in &route.methods {
                Method::from_bytes(method.as_bytes())
                    .map_err(|_| NativeApplicationError::InvalidMethod(method.clone()))?;
            }
            if !route.methods.is_empty() && route.allow_header.is_none() {
                return Err(NativeApplicationError::InvalidAllowHeader);
            }
            router
                .add_operation_with_methods(&route.path, &route.methods, None)
                .map_err(NativeApplicationError::RouteRegistration)?;
            endpoints.push(route.endpoint);
            allow_headers.push(route.allow_header);
        }

        Ok(NativeApplication {
            router,
            endpoints,
            allow_headers,
        })
    }
}

/// A route-registration failure returned while building a native service.
#[derive(Clone, Debug, Eq, PartialEq)]
pub enum NativeApplicationError {
    /// Starlette-RS rejected the path template.
    RouteRegistration(RouteError),
    /// The route declared a method that is not a valid HTTP method token.
    InvalidMethod(String),
    /// The registered methods could not be represented by an `Allow` header.
    InvalidAllowHeader,
}

impl Display for NativeApplicationError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        match self {
            Self::RouteRegistration(error) => Display::fmt(error, formatter),
            Self::InvalidMethod(method) => write!(formatter, "invalid HTTP method {method:?}"),
            Self::InvalidAllowHeader => formatter.write_str("invalid HTTP Allow header value"),
        }
    }
}

impl Error for NativeApplicationError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::RouteRegistration(error) => Some(error),
            Self::InvalidMethod(_) | Self::InvalidAllowHeader => None,
        }
    }
}

/// A native HTTP request with Starlette-RS route parameters and a streaming body.
pub struct NativeRequest {
    parts: Parts,
    body: NativeRequestBody,
    path_params: Vec<(String, String)>,
}

impl NativeRequest {
    /// Returns the request method.
    #[must_use]
    pub fn method(&self) -> &Method {
        &self.parts.method
    }

    /// Returns the original request URI, including its query string.
    #[must_use]
    pub fn uri(&self) -> &Uri {
        &self.parts.uri
    }

    /// Returns the request URI path used by route matching.
    #[must_use]
    pub fn path(&self) -> &str {
        self.parts.uri.path()
    }

    /// Returns the query component without its leading question mark.
    #[must_use]
    pub fn query(&self) -> Option<&str> {
        self.parts.uri.query()
    }

    /// Returns the HTTP version selected by the transport.
    #[must_use]
    pub const fn version(&self) -> Version {
        self.parts.version
    }

    /// Returns request headers while preserving duplicate values.
    #[must_use]
    pub fn headers(&self) -> &HeaderMap {
        &self.parts.headers
    }

    /// Returns request extensions supplied by the server or middleware.
    #[must_use]
    pub fn extensions(&self) -> &http::Extensions {
        &self.parts.extensions
    }

    /// Returns mutable request extensions for endpoint-owned metadata.
    pub fn extensions_mut(&mut self) -> &mut http::Extensions {
        &mut self.parts.extensions
    }

    /// Returns captured route parameters in declaration order.
    #[must_use]
    pub fn path_params(&self) -> &[(String, String)] {
        &self.path_params
    }

    /// Returns the request body for incremental, pull-based polling.
    pub fn body_mut(&mut self) -> &mut NativeRequestBody {
        &mut self.body
    }

    /// Splits the request head, body stream, and captured path parameters.
    #[must_use]
    pub fn into_parts(self) -> (Parts, NativeRequestBody, Vec<(String, String)>) {
        (self.parts, self.body, self.path_params)
    }
}

/// A native application backed by FastAPI-owned operation metadata and the
/// Starlette-RS route table.
#[derive(Clone)]
pub struct NativeApplication {
    router: FastApiOperationRouter,
    endpoints: Vec<Arc<Endpoint>>,
    allow_headers: Vec<Option<HeaderValue>>,
}

impl<B> Service<Request<B>> for NativeApplication
where
    B: Body<Data = Bytes> + Send + 'static,
    B::Error: Error + Send + Sync + 'static,
{
    type Response = NativeHttpResponse;
    type Error = Infallible;
    type Future = NativeServiceFuture;

    fn poll_ready(&mut self, _context: &mut Context<'_>) -> Poll<Result<(), Self::Error>> {
        Poll::Ready(Ok(()))
    }

    fn call(&mut self, request: Request<B>) -> Self::Future {
        let (parts, body) = request.into_parts();
        let route_match = self
            .router
            .matches(parts.uri.path(), "", parts.method.as_str());
        match route_match {
            FastApiOperationMatch::Matched {
                operation_index,
                path_params,
            } => {
                let Some(endpoint) = self.endpoints.get(operation_index).cloned() else {
                    return Box::pin(async {
                        Ok(detail_response(
                            StatusCode::INTERNAL_SERVER_ERROR,
                            "native route table and endpoint list diverged",
                        ))
                    });
                };
                let request = NativeRequest {
                    parts,
                    body: box_native_body(body),
                    path_params,
                };
                Box::pin(async move { Ok(endpoint(request).await) })
            }
            FastApiOperationMatch::MethodNotAllowed {
                operation_index,
                allowed_methods: _,
                path_params: _,
            } => {
                let mut response =
                    detail_response(StatusCode::METHOD_NOT_ALLOWED, "Method Not Allowed");
                if let Some(Some(allow)) = self.allow_headers.get(operation_index) {
                    response.headers_mut().insert(ALLOW, allow.clone());
                }
                Box::pin(async move { Ok(response) })
            }
            FastApiOperationMatch::NotFound => {
                Box::pin(async { Ok(detail_response(StatusCode::NOT_FOUND, "Not Found")) })
            }
        }
    }
}

/// Boxes a body at the route-handler boundary without polling or collecting it.
pub fn box_native_body<B>(body: B) -> NativeResponseBody
where
    B: Body<Data = Bytes> + Send + 'static,
    B::Error: Error + Send + Sync + 'static,
{
    body.map_err(|error| Box::new(error) as NativeBodyError)
        .boxed_unsync()
}

/// Creates a single-frame response body from bytes.
#[must_use]
pub fn native_body(bytes: impl Into<Bytes>) -> NativeResponseBody {
    box_native_body(Full::new(bytes.into()))
}

/// An endpoint error converted into an HTTP response by [`FastApiNativeBuilder`].
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct NativeRequestError {
    status: StatusCode,
    message: String,
}

impl NativeRequestError {
    /// Creates an endpoint error with the response status and JSON detail body.
    #[must_use]
    pub fn new(status: StatusCode, message: impl Into<String>) -> Self {
        Self {
            status,
            message: message.into(),
        }
    }

    /// Returns the HTTP status carried by the error.
    #[must_use]
    pub const fn status(&self) -> StatusCode {
        self.status
    }

    /// Returns the plain-text message carried by the error.
    #[must_use]
    pub fn message(&self) -> &str {
        &self.message
    }

    fn into_response(self) -> NativeHttpResponse {
        detail_response(self.status, &self.message)
    }
}

impl Display for NativeRequestError {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> fmt::Result {
        formatter.write_str(&self.message)
    }
}

impl Error for NativeRequestError {}

/// Extracts and parses one captured path parameter.
///
/// # Errors
///
/// Returns a `400 Bad Request` endpoint error when the parameter is absent or
/// cannot be parsed as `T`.
pub fn path_parameter<T>(request: &NativeRequest, name: &str) -> Result<T, NativeRequestError>
where
    T: FromStr,
{
    let value = request
        .path_params()
        .iter()
        .find(|(parameter, _)| parameter == name)
        .map(|(_, value)| value)
        .ok_or_else(|| {
            NativeRequestError::new(
                StatusCode::BAD_REQUEST,
                format!("missing path parameter {name:?}"),
            )
        })?;
    value.parse().map_err(|_| {
        NativeRequestError::new(
            StatusCode::BAD_REQUEST,
            format!("invalid path parameter {name:?}"),
        )
    })
}

/// Reads the final query value for a key and parses it when present.
///
/// Repeated-key decoding and scalar selection use Starlette-RS
/// [`starlette_rs::QueryParams`].
///
/// # Errors
///
/// Returns a `400 Bad Request` endpoint error when a present value cannot be
/// parsed as `T`.
pub fn optional_query_parameter<T>(
    request: &NativeRequest,
    name: &str,
) -> Result<Option<T>, NativeRequestError>
where
    T: FromStr,
{
    let query = starlette_rs::QueryParams::parse_str(request.query().unwrap_or_default());
    query
        .get(name)
        .map(|value| {
            value.parse().map_err(|_| {
                NativeRequestError::new(
                    StatusCode::BAD_REQUEST,
                    format!("invalid query parameter {name:?}"),
                )
            })
        })
        .transpose()
}

/// Collects a streaming request body up to `maximum_bytes` and decodes JSON.
///
/// Endpoints that need incremental upload handling can poll
/// [`NativeRequest::body_mut`] directly and avoid this body buffer.
///
/// # Errors
///
/// Returns `400 Bad Request` for a body-stream or JSON decoding error, and
/// `413 Payload Too Large` when the cumulative data exceeds the limit.
pub async fn json_body<T>(
    request: &mut NativeRequest,
    maximum_bytes: usize,
) -> Result<T, NativeRequestError>
where
    T: DeserializeOwned,
{
    let mut body = Vec::new();
    while let Some(frame) = request.body_mut().frame().await {
        let frame = frame.map_err(|error| {
            NativeRequestError::new(
                StatusCode::BAD_REQUEST,
                format!("request body stream failed: {error}"),
            )
        })?;
        let Ok(data) = frame.into_data() else {
            continue;
        };
        let Some(total_bytes) = body.len().checked_add(data.len()) else {
            return Err(NativeRequestError::new(
                StatusCode::PAYLOAD_TOO_LARGE,
                "request body size overflowed",
            ));
        };
        if total_bytes > maximum_bytes {
            return Err(NativeRequestError::new(
                StatusCode::PAYLOAD_TOO_LARGE,
                "request body exceeds the configured limit",
            ));
        }
        body.extend_from_slice(&data);
    }

    serde_json::from_slice(&body).map_err(|error| {
        NativeRequestError::new(
            StatusCode::BAD_REQUEST,
            format!("invalid JSON request body: {error}"),
        )
    })
}

/// Serializes a Rust value into a JSON response.
///
/// The encoded vector allocation moves into `Bytes`; this helper does not make
/// a second payload copy.
///
/// # Errors
///
/// Returns an endpoint error with status `500 Internal Server Error` when the
/// value cannot be serialized.
pub fn json_response<T: Serialize>(
    value: &T,
    status: StatusCode,
) -> Result<NativeHttpResponse, NativeRequestError> {
    let encoded = serde_json::to_vec(value).map_err(|error| {
        NativeRequestError::new(
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("JSON response serialization failed: {error}"),
        )
    })?;
    let mut response = Response::new(native_body(Bytes::from(encoded)));
    *response.status_mut() = status;
    response
        .headers_mut()
        .insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
    Ok(response)
}

/// Wraps a streaming Rust body as a response without collecting frames.
///
/// The server polls the body on demand. Dropping the response body drops its
/// source, allowing cancellation and backpressure to reach the producer.
#[must_use]
pub fn streaming_response<B>(status: StatusCode, body: B) -> NativeHttpResponse
where
    B: Body<Data = Bytes> + Send + 'static,
    B::Error: Error + Send + Sync + 'static,
{
    let mut response = Response::new(box_native_body(body));
    *response.status_mut() = status;
    response
}

#[derive(Serialize)]
struct ErrorDetail<'a> {
    detail: &'a str,
}

fn detail_response(status: StatusCode, message: &str) -> NativeHttpResponse {
    let body = serde_json::to_vec(&ErrorDetail { detail: message })
        .map(Bytes::from)
        .unwrap_or_else(|_| Bytes::from_static(b"{\"detail\":\"Internal Server Error\"}"));
    let mut response = Response::new(native_body(body));
    *response.status_mut() = status;
    response
        .headers_mut()
        .insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
    response
}
