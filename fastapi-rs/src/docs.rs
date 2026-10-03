//! Rust-owned HTML for FastAPI's default documentation routes.
//!
//! The templates follow FastAPI 0.141.1's built-in openapi.docs helpers.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyModule, PyString, PyTuple};

const GOOGLE_FONTS_URL: &str =
    "https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700";

/// Builds the default Swagger UI page.
pub(crate) fn swagger_ui_html(openapi_url: &str, oauth2_redirect_url: &str, title: &str) -> String {
    let mut html = String::from(
        "\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <link type=\"text/css\" rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css\">\n    <link rel=\"shortcut icon\" href=\"https://fastapi.tiangolo.com/img/favicon.png\">\n    <title>",
    );
    html.push_str(title);
    html.push_str(
        "</title>\n    </head>\n    <body>\n    <div id=\"swagger-ui\">\n    </div>\n    <script src=\"https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>\n    <!-- `SwaggerUIBundle` is now available on the page -->\n    <script>\n    const ui = SwaggerUIBundle({\n        url: '",
    );
    html.push_str(openapi_url);
    html.push_str(
        "',\n    \"dom_id\": \"#swagger-ui\",\n\"layout\": \"BaseLayout\",\n\"deepLinking\": true,\n\"showExtensions\": true,\n\"showCommonExtensions\": true,\noauth2RedirectUrl: window.location.origin + '",
    );
    html.push_str(oauth2_redirect_url);
    html.push_str(
        "',\n    presets: [\n        SwaggerUIBundle.presets.apis,\n        SwaggerUIBundle.SwaggerUIStandalonePreset\n        ],\n    })\n    </script>\n    </body>\n    </html>\n    ",
    );
    html
}

/// Adds FastAPI's optional Swagger UI OAuth initialization to the default page.
pub(crate) fn swagger_ui_html_with_init_oauth(
    py: Python<'_>,
    openapi_url: &str,
    oauth2_redirect_url: &str,
    title: &str,
    init_oauth: Option<&Bound<'_, PyAny>>,
) -> PyResult<String> {
    let mut html = swagger_ui_html(openapi_url, oauth2_redirect_url, title);
    if let Some(init_oauth) = init_oauth {
        if init_oauth.is_truthy()? {
            let oauth_configuration = html_safe_encoded_json(py, init_oauth)?;
            let script_end = html.rfind("\n    </script>").ok_or_else(|| {
                PyRuntimeError::new_err("default Swagger UI HTML has no closing script tag")
            })?;
            let mut initialization = String::from("\n        ui.initOAuth(");
            initialization.push_str(&oauth_configuration);
            initialization.push_str(")\n        ");
            html.insert_str(script_end, &initialization);
        }
    }
    Ok(html)
}

/// Builds the default ReDoc page.
pub(crate) fn redoc_html(openapi_url: &str, title: &str) -> String {
    let mut html = String::from("\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <title>");
    html.push_str(title);
    html.push_str(
        "</title>\n    <!-- needed for adaptive design -->\n    <meta charset=\"utf-8\"/>\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n    \n    <link href=\"https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700\" rel=\"stylesheet\">\n    \n    <link rel=\"shortcut icon\" href=\"https://fastapi.tiangolo.com/img/favicon.png\">\n    <!--\n    ReDoc doesn't change outer page styles\n    -->\n    <style>\n      body {\n        margin: 0;\n        padding: 0;\n      }\n    </style>\n    </head>\n    <body>\n    <noscript>\n        ReDoc requires Javascript to function. Please enable it to browse the documentation.\n    </noscript>\n    <redoc spec-url=\"",
    );
    html.push_str(openapi_url);
    html.push_str(
        "\"></redoc>\n    <script src=\"https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js\"> </script>\n    </body>\n    </html>\n    ",
    );
    html
}

/// Returns the default Swagger UI OAuth2 callback page.
pub(crate) const fn oauth2_redirect_html() -> &'static str {
    "\n    <!doctype html>\n    <html lang=\"en-US\">\n    <head>\n        <title>Swagger UI: OAuth2 Redirect</title>\n    </head>\n    <body>\n    <script>\n        'use strict';\n        function run () {\n            var oauth2 = window.opener.swaggerUIRedirectOauth2;\n            var sentState = oauth2.state;\n            var redirectUrl = oauth2.redirectUrl;\n            var isValid, qp, arr;\n\n            if (/code|token|error/.test(window.location.hash)) {\n                qp = window.location.hash.substring(1).replace('?', '&');\n            } else {\n                qp = location.search.substring(1);\n            }\n\n            arr = qp.split(\"&\");\n            arr.forEach(function (v,i,_arr) { _arr[i] = '\"' + v.replace('=', '\":\"') + '\"';});\n            qp = qp ? JSON.parse('{' + arr.join() + '}',\n                    function (key, value) {\n                        return key === \"\" ? value : decodeURIComponent(value);\n                    }\n            ) : {};\n\n            isValid = qp.state === sentState;\n\n            if ((\n              oauth2.auth.schema.get(\"flow\") === \"accessCode\" ||\n              oauth2.auth.schema.get(\"flow\") === \"authorizationCode\" ||\n              oauth2.auth.schema.get(\"flow\") === \"authorization_code\"\n            ) && !oauth2.auth.code) {\n                if (!isValid) {\n                    oauth2.errCb({\n                        authId: oauth2.auth.name,\n                        source: \"auth\",\n                        level: \"warning\",\n                        message: \"Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server.\"\n                    });\n                }\n\n                if (qp.code) {\n                    delete oauth2.state;\n                    oauth2.auth.code = qp.code;\n                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});\n                } else {\n                    let oauthErrorMsg;\n                    if (qp.error) {\n                        oauthErrorMsg = \"[\"+qp.error+\"]: \" +\n                            (qp.error_description ? qp.error_description+ \". \" : \"no accessCode received from the server. \") +\n                            (qp.error_uri ? \"More info: \"+qp.error_uri : \"\");\n                    }\n\n                    oauth2.errCb({\n                        authId: oauth2.auth.name,\n                        source: \"auth\",\n                        level: \"error\",\n                        message: oauthErrorMsg || \"[Authorization failed]: no accessCode received from the server.\"\n                    });\n                }\n            } else {\n                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});\n            }\n            window.close();\n        }\n\n        if (document.readyState !== 'loading') {\n            run();\n        } else {\n            document.addEventListener('DOMContentLoaded', function () {\n                run();\n            });\n        }\n    </script>\n    </body>\n    </html>\n        "
}

/// Create the FastAPI Swagger UI default configuration dictionary.
fn default_swagger_ui_parameters<'py>(py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
    let parameters = PyDict::new(py);
    parameters.set_item("dom_id", "#swagger-ui")?;
    parameters.set_item("layout", "BaseLayout")?;
    parameters.set_item("deepLinking", true)?;
    parameters.set_item("showExtensions", true)?;
    parameters.set_item("showCommonExtensions", true)?;
    Ok(parameters)
}

/// Serialize JSON with HTML-significant characters escaped for an inline script.
fn html_safe_json(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<String> {
    let serialized = py
        .import("json")?
        .getattr("dumps")?
        .call1((value,))?
        .extract::<String>()?;
    Ok(serialized
        .replace('<', "\\u003c")
        .replace('>', "\\u003e")
        .replace('&', "\\u0026"))
}

fn html_safe_encoded_json(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<String> {
    let encoded = crate::encoding::jsonable_encoder_default(py, value)?;
    html_safe_json(py, &encoded)
}

fn html_response<'py>(py: Python<'py>, content: &str) -> PyResult<Bound<'py, PyAny>> {
    py.import("starlette.responses")?
        .getattr("HTMLResponse")?
        .call1((content,))
}

fn python_format(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<String> {
    py.import("builtins")?
        .getattr("format")?
        .call1((value, ""))?
        .extract::<String>()
}

/// Generate the HTML response that loads Swagger UI for the interactive API docs.
// lint-exception: Keep the pinned eight-parameter public Python helper at its native boundary.
#[allow(
    clippy::too_many_arguments,
    reason = "the native binding mirrors FastAPI's eight keyword-only helper parameters"
)]
#[pyfunction(
    signature = (
        *,
        openapi_url,
        title,
        swagger_js_url,
        swagger_css_url,
        swagger_favicon_url,
        oauth2_redirect_url,
        init_oauth,
        swagger_ui_parameters
    )
)]
fn get_swagger_ui_html<'py>(
    py: Python<'py>,
    openapi_url: Bound<'py, PyAny>,
    title: Bound<'py, PyAny>,
    swagger_js_url: Bound<'py, PyAny>,
    swagger_css_url: Bound<'py, PyAny>,
    swagger_favicon_url: Bound<'py, PyAny>,
    oauth2_redirect_url: Option<Bound<'py, PyAny>>,
    init_oauth: Option<Bound<'py, PyAny>>,
    swagger_ui_parameters: Option<Bound<'py, PyAny>>,
) -> PyResult<Bound<'py, PyAny>> {
    let defaults = py
        .import("fastapi_rs._core")?
        .getattr("swagger_ui_default_parameters")?;
    let current_parameters = defaults.call_method0("copy")?;
    if let Some(parameters) = swagger_ui_parameters.as_ref() {
        if parameters.is_truthy()? {
            current_parameters.call_method1("update", (parameters,))?;
        }
    }

    let mut html = String::from(
        "\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <link type=\"text/css\" rel=\"stylesheet\" href=\"",
    );
    html.push_str(&python_format(py, &swagger_css_url)?);
    html.push_str("\">\n    <link rel=\"shortcut icon\" href=\"");
    html.push_str(&python_format(py, &swagger_favicon_url)?);
    html.push_str("\">\n    <title>");
    html.push_str(&python_format(py, &title)?);
    html.push_str(
        "</title>\n    </head>\n    <body>\n    <div id=\"swagger-ui\">\n    </div>\n    <script src=\"",
    );
    html.push_str(&python_format(py, &swagger_js_url)?);
    html.push_str(
        "\"></script>\n    <!-- `SwaggerUIBundle` is now available on the page -->\n    <script>\n    const ui = SwaggerUIBundle({\n        url: '",
    );
    html.push_str(&python_format(py, &openapi_url)?);
    html.push_str("',\n    ");

    for pair in current_parameters.call_method0("items")?.try_iter()? {
        let pair = pair?;
        let key = pair.get_item(0)?;
        let value = pair.get_item(1)?;
        let encoded_value = crate::encoding::jsonable_encoder_default(py, &value)?;
        html.push_str(&html_safe_json(py, &key)?);
        html.push_str(": ");
        html.push_str(&html_safe_json(py, &encoded_value)?);
        html.push_str(",\n");
    }

    if let Some(redirect_url) = oauth2_redirect_url.as_ref() {
        if redirect_url.is_truthy()? {
            html.push_str("oauth2RedirectUrl: window.location.origin + '");
            html.push_str(&python_format(py, redirect_url)?);
            html.push_str("',");
        }
    }
    html.push_str(
        "\n    presets: [\n        SwaggerUIBundle.presets.apis,\n        SwaggerUIBundle.SwaggerUIStandalonePreset\n        ],\n    })",
    );

    if let Some(init_oauth) = init_oauth.as_ref() {
        if init_oauth.is_truthy()? {
            html.push_str("\n        ui.initOAuth(");
            html.push_str(&html_safe_encoded_json(py, init_oauth)?);
            html.push_str(")\n        ");
        }
    }
    html.push_str("\n    </script>\n    </body>\n    </html>\n    ");
    html_response(py, &html)
}

/// Generate the HTML response that loads ReDoc for the alternative API docs.
#[pyfunction(
    signature = (
        *,
        openapi_url,
        title,
        redoc_js_url,
        redoc_favicon_url,
        with_google_fonts
    )
)]
fn get_redoc_html<'py>(
    py: Python<'py>,
    openapi_url: Bound<'py, PyAny>,
    title: Bound<'py, PyAny>,
    redoc_js_url: Bound<'py, PyAny>,
    redoc_favicon_url: Bound<'py, PyAny>,
    with_google_fonts: Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let mut html = String::from("\n    <!DOCTYPE html>\n    <html>\n    <head>\n    <title>");
    html.push_str(&python_format(py, &title)?);
    html.push_str(
        "</title>\n    <!-- needed for adaptive design -->\n    <meta charset=\"utf-8\"/>\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n    ",
    );
    if with_google_fonts.is_truthy()? {
        html.push_str("\n    <link href=\"");
        html.push_str(GOOGLE_FONTS_URL);
        html.push_str("\" rel=\"stylesheet\">\n    ");
    }
    html.push_str("\n    <link rel=\"shortcut icon\" href=\"");
    html.push_str(&python_format(py, &redoc_favicon_url)?);
    html.push_str(
        "\">\n    <!--\n    ReDoc doesn't change outer page styles\n    -->\n    <style>\n      body {\n        margin: 0;\n        padding: 0;\n      }\n    </style>\n    </head>\n    <body>\n    <noscript>\n        ReDoc requires Javascript to function. Please enable it to browse the documentation.\n    </noscript>\n    <redoc spec-url=\"",
    );
    html.push_str(&python_format(py, &openapi_url)?);
    html.push_str("\"></redoc>\n    <script src=\"");
    html.push_str(&python_format(py, &redoc_js_url)?);
    html.push_str("\"> </script>\n    </body>\n    </html>\n    ");
    html_response(py, &html)
}

/// Generate the HTML response with the OAuth2 redirection for Swagger UI.
#[pyfunction]
fn get_swagger_ui_oauth2_redirect_html(py: Python<'_>) -> PyResult<Bound<'_, PyAny>> {
    html_response(py, oauth2_redirect_html())
}

const SWAGGER_UI_WRAPPER: &str = r#"
def get_swagger_ui_html(
    *,
    openapi_url,
    title,
    swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
    swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url=None,
    init_oauth=None,
    swagger_ui_parameters=None,
):
    return __fastapi_native_get_swagger_ui_html(
        openapi_url=openapi_url,
        title=title,
        swagger_js_url=swagger_js_url,
        swagger_css_url=swagger_css_url,
        swagger_favicon_url=swagger_favicon_url,
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=init_oauth,
        swagger_ui_parameters=swagger_ui_parameters,
    )
"#;

const REDOC_WRAPPER: &str = r#"
def get_redoc_html(
    *,
    openapi_url,
    title,
    redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js",
    redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    with_google_fonts=True,
):
    return __fastapi_native_get_redoc_html(
        openapi_url=openapi_url,
        title=title,
        redoc_js_url=redoc_js_url,
        redoc_favicon_url=redoc_favicon_url,
        with_google_fonts=with_google_fonts,
    )
"#;

const OAUTH2_REDIRECT_WRAPPER: &str = r#"
def get_swagger_ui_oauth2_redirect_html():
    return __fastapi_native_get_swagger_ui_oauth2_redirect_html()
"#;

fn add_docs_function(
    py: Python<'_>,
    module: &Bound<'_, PyModule>,
    name: &str,
    function: Bound<'_, PyAny>,
    wrapper_source: &str,
) -> PyResult<()> {
    let native_name = format!("__fastapi_native_{name}");
    module.add(native_name, function)?;
    py.import("builtins")?
        .getattr("exec")?
        .call1((wrapper_source, module.dict()))?;
    let public_function = module.getattr(name)?;
    public_function.setattr("__module__", "fastapi.openapi.docs")?;
    public_function.setattr("__annotations__", docs_function_annotations(py, name)?)?;
    Ok(())
}

fn docs_function_annotations<'py>(py: Python<'py>, name: &str) -> PyResult<Bound<'py, PyDict>> {
    let annotations = PyDict::new(py);
    let string_type = py.get_type::<PyString>().into_any();
    let bool_type = py.get_type::<PyBool>().into_any();
    let response_type = py.import("starlette.responses")?.getattr("HTMLResponse")?;
    if name == "get_swagger_ui_html" {
        annotations.set_item(
            "openapi_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The OpenAPI URL that Swagger UI should load and use.

            This is normally done automatically by FastAPI using the default URL
            `/openapi.json`.

            Read more about it in the
            [FastAPI docs for Conditional OpenAPI](https://fastapi.tiangolo.com/how-to/conditional-openapi/#conditional-openapi-from-settings-and-env-vars)
            "#,
            )?,
        )?;
        annotations.set_item(
            "title",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The HTML `<title>` content, normally shown in the browser tab.

            Read more about it in the
            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
            "#,
            )?,
        )?;
        annotations.set_item(
            "swagger_js_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The URL to use to load the Swagger UI JavaScript.

            It is normally set to a CDN URL.

            Read more about it in the
            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
            "#,
            )?,
        )?;
        annotations.set_item(
            "swagger_css_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The URL to use to load the Swagger UI CSS.

            It is normally set to a CDN URL.

            Read more about it in the
            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
            "#,
            )?,
        )?;
        annotations.set_item(
            "swagger_favicon_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The URL of the favicon to use. It is normally shown in the browser tab.
            "#,
            )?,
        )?;
        annotations.set_item(
            "oauth2_redirect_url",
            annotated_doc_type(
                py,
                union_with_none(py, string_type.clone())?,
                r#"
            The OAuth2 redirect URL, it is normally automatically handled by FastAPI.

            Read more about it in the
            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
            "#,
            )?,
        )?;
        let mapping_type = string_any_dict_type(py)?;
        let optional_mapping_type = union_with_none(py, mapping_type)?;
        annotations.set_item(
            "init_oauth",
            annotated_doc_type(
                py,
                optional_mapping_type.clone(),
                r#"
            A dictionary with Swagger UI OAuth2 initialization configurations.

            Read more about the available configuration options in the
            [Swagger UI docs](https://swagger.io/docs/open-source-tools/swagger-ui/usage/oauth2/).
            "#,
            )?,
        )?;
        annotations.set_item(
            "swagger_ui_parameters",
            annotated_doc_type(
                py,
                optional_mapping_type,
                r#"
            Configuration parameters for Swagger UI.

            It defaults to [swagger_ui_default_parameters][fastapi.openapi.docs.swagger_ui_default_parameters].

            Read more about it in the
            [FastAPI docs about how to Configure Swagger UI](https://fastapi.tiangolo.com/how-to/configure-swagger-ui/).
            "#,
            )?,
        )?;
    } else if name == "get_redoc_html" {
        annotations.set_item(
            "openapi_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The OpenAPI URL that ReDoc should load and use.

            This is normally done automatically by FastAPI using the default URL
            `/openapi.json`.

            Read more about it in the
            [FastAPI docs for Conditional OpenAPI](https://fastapi.tiangolo.com/how-to/conditional-openapi/#conditional-openapi-from-settings-and-env-vars)
            "#,
            )?,
        )?;
        annotations.set_item(
            "title",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The HTML `<title>` content, normally shown in the browser tab.

            Read more about it in the
            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
            "#,
            )?,
        )?;
        annotations.set_item(
            "redoc_js_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The URL to use to load the ReDoc JavaScript.

            It is normally set to a CDN URL.

            Read more about it in the
            [FastAPI docs for Custom Docs UI Static Assets](https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/)
            "#,
            )?,
        )?;
        annotations.set_item(
            "redoc_favicon_url",
            annotated_doc_type(
                py,
                string_type.clone(),
                r#"
            The URL of the favicon to use. It is normally shown in the browser tab.
            "#,
            )?,
        )?;
        annotations.set_item(
            "with_google_fonts",
            annotated_doc_type(
                py,
                bool_type,
                r#"
            Load and use Google Fonts.
            "#,
            )?,
        )?;
    }
    annotations.set_item("return", response_type)?;
    Ok(annotations)
}

fn annotated_doc_type<'py>(
    py: Python<'py>,
    annotation: Bound<'py, PyAny>,
    description: &str,
) -> PyResult<Bound<'py, PyAny>> {
    let doc = py
        .import("annotated_doc")?
        .getattr("Doc")?
        .call1((description,))?;
    let arguments = PyTuple::new(py, [annotation, doc])?;
    let annotated = py.import("typing")?.getattr("Annotated")?;
    py.import("operator")?
        .getattr("getitem")?
        .call1((annotated, arguments))
}

fn string_any_dict_type(py: Python<'_>) -> PyResult<Bound<'_, PyAny>> {
    let arguments = PyTuple::new(
        py,
        [
            py.get_type::<PyString>().as_any(),
            py.import("typing")?.getattr("Any")?.as_any(),
        ],
    )?;
    py.get_type::<PyDict>()
        .getattr("__class_getitem__")?
        .call1((arguments,))
}

fn union_with_none<'py>(
    py: Python<'py>,
    annotation: Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let none_type = py.None().bind(py).get_type().into_any();
    py.import("operator")?
        .getattr("or_")?
        .call1((annotation, none_type))
}

/// Register the `fastapi.openapi.docs` helper implementations on the native module.
pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    let py = module.py();
    module.add(
        "swagger_ui_default_parameters",
        default_swagger_ui_parameters(py)?,
    )?;
    add_docs_function(
        py,
        module,
        "get_swagger_ui_html",
        wrap_pyfunction!(get_swagger_ui_html, module)?.into_any(),
        SWAGGER_UI_WRAPPER,
    )?;
    add_docs_function(
        py,
        module,
        "get_redoc_html",
        wrap_pyfunction!(get_redoc_html, module)?.into_any(),
        REDOC_WRAPPER,
    )?;
    add_docs_function(
        py,
        module,
        "get_swagger_ui_oauth2_redirect_html",
        wrap_pyfunction!(get_swagger_ui_oauth2_redirect_html, module)?.into_any(),
        OAUTH2_REDIRECT_WRAPPER,
    )?;
    Ok(())
}
