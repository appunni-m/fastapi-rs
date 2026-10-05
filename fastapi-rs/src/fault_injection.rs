use std::sync::atomic::{AtomicBool, Ordering};

const HTTP_ROUTE_INVOKE_BEFORE: &str = "http.route.invoke.before";
const HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE: &str =
    "http.route.invoke.after_dependencies.before";
const HTTP_REQUEST_JSON_DECODE_BEFORE: &str = "http.request.json_decode.before";
const HTTP_REQUEST_FORM_PARSE_BEFORE: &str = "http.request.form_parse.before";
const HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR: &str = "http.frontend.lookup.permission-error";
const HTTP_FRONTEND_LOOKUP_VALUE_ERROR: &str = "http.frontend.lookup.value-error";
const HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG: &str = "http.frontend.lookup.name-too-long";
const HTTP_FRONTEND_LOOKUP_OS_ERROR: &str = "http.frontend.lookup.os-error";

static HTTP_ROUTE_INVOKE_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_REQUEST_JSON_DECODE_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_REQUEST_FORM_PARSE_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_FRONTEND_LOOKUP_VALUE_ERROR_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_FRONTEND_LOOKUP_OS_ERROR_ARMED: AtomicBool = AtomicBool::new(false);

pub(crate) enum FrontendLookupFault {
    PermissionError,
    ValueError,
    NameTooLong,
    OsError,
}

pub(crate) fn arm(point: &str) -> Result<(), &'static str> {
    let armed = match point {
        HTTP_ROUTE_INVOKE_BEFORE => &HTTP_ROUTE_INVOKE_BEFORE_ARMED,
        HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE => {
            &HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED
        }
        HTTP_REQUEST_JSON_DECODE_BEFORE => &HTTP_REQUEST_JSON_DECODE_BEFORE_ARMED,
        HTTP_REQUEST_FORM_PARSE_BEFORE => &HTTP_REQUEST_FORM_PARSE_BEFORE_ARMED,
        HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR => &HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_ARMED,
        HTTP_FRONTEND_LOOKUP_VALUE_ERROR => &HTTP_FRONTEND_LOOKUP_VALUE_ERROR_ARMED,
        HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG => &HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_ARMED,
        HTTP_FRONTEND_LOOKUP_OS_ERROR => &HTTP_FRONTEND_LOOKUP_OS_ERROR_ARMED,
        _ => return Err("unknown fault injection point"),
    };
    armed
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .map(|_| ())
        .map_err(|_| "fault injection point is already armed")
}

pub(crate) fn take_http_route_invoke_before() -> bool {
    HTTP_ROUTE_INVOKE_BEFORE_ARMED.swap(false, Ordering::SeqCst)
}

pub(crate) fn take_http_route_invoke_after_dependencies_before() -> bool {
    HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED.swap(false, Ordering::SeqCst)
}

pub(crate) fn take_http_request_json_decode_before() -> bool {
    HTTP_REQUEST_JSON_DECODE_BEFORE_ARMED.swap(false, Ordering::SeqCst)
}

pub(crate) fn take_http_request_form_parse_before() -> bool {
    HTTP_REQUEST_FORM_PARSE_BEFORE_ARMED.swap(false, Ordering::SeqCst)
}

pub(crate) fn take_http_frontend_lookup_fault() -> Option<FrontendLookupFault> {
    if HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_ARMED.swap(false, Ordering::SeqCst) {
        return Some(FrontendLookupFault::PermissionError);
    }
    if HTTP_FRONTEND_LOOKUP_VALUE_ERROR_ARMED.swap(false, Ordering::SeqCst) {
        return Some(FrontendLookupFault::ValueError);
    }
    if HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_ARMED.swap(false, Ordering::SeqCst) {
        return Some(FrontendLookupFault::NameTooLong);
    }
    if HTTP_FRONTEND_LOOKUP_OS_ERROR_ARMED.swap(false, Ordering::SeqCst) {
        return Some(FrontendLookupFault::OsError);
    }
    None
}

pub(crate) fn clear() {
    HTTP_ROUTE_INVOKE_BEFORE_ARMED.store(false, Ordering::SeqCst);
    HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED.store(false, Ordering::SeqCst);
    HTTP_REQUEST_JSON_DECODE_BEFORE_ARMED.store(false, Ordering::SeqCst);
    HTTP_REQUEST_FORM_PARSE_BEFORE_ARMED.store(false, Ordering::SeqCst);
    HTTP_FRONTEND_LOOKUP_PERMISSION_ERROR_ARMED.store(false, Ordering::SeqCst);
    HTTP_FRONTEND_LOOKUP_VALUE_ERROR_ARMED.store(false, Ordering::SeqCst);
    HTTP_FRONTEND_LOOKUP_NAME_TOO_LONG_ARMED.store(false, Ordering::SeqCst);
    HTTP_FRONTEND_LOOKUP_OS_ERROR_ARMED.store(false, Ordering::SeqCst);
}
