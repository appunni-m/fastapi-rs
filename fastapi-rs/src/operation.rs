//! FastAPI-owned operation registration layered over Starlette-RS routing.

use starlette_rs::{
    Cookies, DetailedRouteMatch, QueryParams, RequestHeaders, RouteError, RouteTable,
};

// FastAPI's APIRoute uses an exact method set. Hide GET from RouteTable's
// generic GET-to-HEAD expansion while keeping normal GET matching here.
const INTERNAL_GET_METHOD: &str = "\0FASTAPI_GET";

/// The source location FastAPI uses to obtain one endpoint argument.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum FastApiInputLocation {
    /// A captured path parameter.
    Path,
    /// A decoded query parameter.
    Query,
    /// A case-insensitive HTTP header.
    Header,
    /// A request cookie.
    Cookie,
    /// The complete request body.
    Body,
}

impl FastApiInputLocation {
    /// Returns the stable source identifier used at the Python boundary.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Path => "path",
            Self::Query => "query",
            Self::Header => "header",
            Self::Cookie => "cookie",
            Self::Body => "body",
        }
    }
}

/// One endpoint argument's FastAPI extraction metadata.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FastApiInputParameter {
    /// The Python endpoint argument name.
    pub name: String,
    /// The external name used in a path, query string, header, or cookie.
    pub alias: String,
    /// The request component from which the value is extracted.
    pub location: FastApiInputLocation,
    /// Whether the request must provide a value when no default exists.
    pub required: bool,
}

/// An extracted, still-unvalidated endpoint argument value.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FastApiInputValue {
    /// The Python endpoint argument name.
    pub name: String,
    /// The request component that supplied the value.
    pub location: FastApiInputLocation,
    /// Decoded UTF-8 text or raw header/body bytes before Pydantic validation.
    pub value: Option<Vec<u8>>,
}

/// Metadata FastAPI owns for one registered path operation.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FastApiOperation {
    /// The original FastAPI path template.
    pub path: String,
    /// The normalized HTTP methods registered for the operation.
    pub methods: Vec<String>,
    /// The response status explicitly selected by the operation decorator.
    pub status_code: Option<u16>,
    /// FastAPI-owned endpoint input declarations.
    pub parameters: Vec<FastApiInputParameter>,
}

/// The result of selecting a FastAPI operation through Starlette-RS routing.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum FastApiOperationMatch {
    /// A path and method selected one registered operation.
    Matched {
        /// The stable operation index returned by [`FastApiOperationRouter::add_operation`].
        operation_index: usize,
        /// Captured path parameters in template order.
        path_params: Vec<(String, String)>,
    },
    /// A path matched, but its method was not registered.
    MethodNotAllowed {
        /// The stable index of the first operation with this path.
        operation_index: usize,
        /// Methods accepted by the matching FastAPI path operation.
        allowed_methods: Vec<String>,
        /// Captured path parameters in template order.
        path_params: Vec<(String, String)>,
    },
    /// No operation path matched the request path.
    NotFound,
}

/// An operation selection paired with extracted request input values.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FastApiRequestMatch {
    /// The route selection made by Starlette-RS.
    pub route: FastApiOperationMatch,
    /// Extracted input values for the selected operation, in declaration order.
    pub inputs: Vec<FastApiInputValue>,
}

/// FastAPI operation metadata backed by Starlette-RS's canonical route table.
///
/// FastAPI owns operation metadata and exact method semantics; Starlette-RS
/// owns path parsing, parameter capture, route precedence, and `root_path`
/// handling.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct FastApiOperationRouter {
    route_table: RouteTable,
    operations: Vec<FastApiOperation>,
}

impl FastApiOperationRouter {
    /// Creates an empty operation router.
    #[must_use]
    pub const fn new() -> Self {
        Self {
            route_table: RouteTable::new(),
            operations: Vec::new(),
        }
    }

    /// Registers one path operation and returns its stable insertion index.
    ///
    /// The route table performs path validation and path matching. FastAPI
    /// preserves the operation's exact method set and selected response status.
    ///
    /// # Errors
    ///
    /// Returns a [`RouteError`] if Starlette-RS rejects the path template.
    pub fn add_operation(
        &mut self,
        path: impl Into<String>,
        method: impl AsRef<str>,
        status_code: Option<u16>,
    ) -> Result<usize, RouteError> {
        let path = path.into();
        let method = method.as_ref().to_ascii_uppercase();
        let route_method = if method == "GET" {
            INTERNAL_GET_METHOD
        } else {
            method.as_str()
        };
        let operation_index = self.route_table.add_route(path.clone(), [route_method])?;
        self.operations.push(FastApiOperation {
            path,
            methods: vec![method],
            status_code,
            parameters: Vec::new(),
        });
        Ok(operation_index)
    }

    /// Replaces the endpoint input plan for one registered operation.
    ///
    /// # Errors
    ///
    /// Returns `None` when the operation index does not exist.
    pub fn set_parameters(
        &mut self,
        index: usize,
        parameters: Vec<FastApiInputParameter>,
    ) -> Option<()> {
        let operation = self.operations.get_mut(index)?;
        operation.parameters = parameters;
        Some(())
    }

    /// Matches the request and extracts raw endpoint arguments.
    ///
    /// Path matching, query decoding, header lookup, and cookie parsing are
    /// delegated to Starlette-RS. Values remain unvalidated so the Python
    /// binding can pass them through the same Pydantic boundary as the public
    /// runtime.
    #[must_use]
    pub fn resolve_inputs(
        &self,
        path: &str,
        root_path: &str,
        method: &str,
        raw_query: &[u8],
        headers: impl IntoIterator<Item = (Vec<u8>, Vec<u8>)>,
        body: &[u8],
    ) -> FastApiRequestMatch {
        let route = self.matches(path, root_path, method);
        let FastApiOperationMatch::Matched {
            operation_index,
            ref path_params,
        } = route
        else {
            return FastApiRequestMatch {
                route,
                inputs: Vec::new(),
            };
        };

        let path_values: std::collections::HashMap<&str, &str> = path_params
            .iter()
            .map(|(name, value)| (name.as_str(), value.as_str()))
            .collect();
        let query = QueryParams::parse(raw_query);
        let headers = RequestHeaders::new(headers);
        let cookies = Cookies::from_headers(&headers);
        let parameters = self
            .operations
            .get(operation_index)
            .map_or(&[][..], |operation| operation.parameters.as_slice());
        let inputs = parameters
            .iter()
            .map(|parameter| {
                let value = match parameter.location {
                    FastApiInputLocation::Path => path_values
                        .get(parameter.alias.as_str())
                        .map(|value| value.as_bytes().to_vec()),
                    FastApiInputLocation::Query => query
                        .get(&parameter.alias)
                        .map(|value| value.as_bytes().to_vec()),
                    FastApiInputLocation::Header => {
                        headers.get(parameter.alias.as_bytes()).map(<[u8]>::to_vec)
                    }
                    FastApiInputLocation::Cookie => cookies
                        .get(&parameter.alias)
                        .map(|value| value.as_bytes().to_vec()),
                    FastApiInputLocation::Body => Some(body.to_vec()),
                };
                FastApiInputValue {
                    name: parameter.name.clone(),
                    location: parameter.location,
                    value,
                }
            })
            .collect();
        FastApiRequestMatch { route, inputs }
    }

    /// Selects an operation using FastAPI method semantics and Starlette-RS
    /// path and root-path rules.
    #[must_use]
    pub fn matches(&self, path: &str, root_path: &str, method: &str) -> FastApiOperationMatch {
        let route_method = if method == "GET" {
            INTERNAL_GET_METHOD
        } else {
            method
        };
        match self
            .route_table
            .matches_detailed_with_root_path(path, root_path, route_method)
        {
            DetailedRouteMatch::Matched {
                route_index,
                path_params,
            } => FastApiOperationMatch::Matched {
                operation_index: route_index,
                path_params,
            },
            DetailedRouteMatch::MethodNotAllowed {
                route_index,
                allowed_methods,
                path_params,
            } => FastApiOperationMatch::MethodNotAllowed {
                operation_index: route_index,
                allowed_methods: allowed_methods
                    .into_iter()
                    .map(|method| {
                        if method == INTERNAL_GET_METHOD {
                            String::from("GET")
                        } else {
                            method
                        }
                    })
                    .collect(),
                path_params,
            },
            DetailedRouteMatch::NotFound => FastApiOperationMatch::NotFound,
        }
    }

    /// Returns operation metadata by its stable insertion index.
    #[must_use]
    pub fn operation(&self, index: usize) -> Option<&FastApiOperation> {
        self.operations.get(index)
    }

    /// Returns the number of registered operations.
    #[must_use]
    pub fn len(&self) -> usize {
        self.operations.len()
    }

    /// Returns whether the router has no operations.
    #[must_use]
    pub fn is_empty(&self) -> bool {
        self.operations.is_empty()
    }
}
