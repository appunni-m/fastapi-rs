use std::sync::atomic::{AtomicBool, Ordering};

const HTTP_ROUTE_INVOKE_BEFORE: &str = "http.route.invoke.before";
const HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE: &str =
    "http.route.invoke.after_dependencies.before";

static HTTP_ROUTE_INVOKE_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);
static HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);

pub(crate) fn arm(point: &str) -> Result<(), &'static str> {
    let armed = match point {
        HTTP_ROUTE_INVOKE_BEFORE => &HTTP_ROUTE_INVOKE_BEFORE_ARMED,
        HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE => {
            &HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED
        }
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

pub(crate) fn clear() {
    HTTP_ROUTE_INVOKE_BEFORE_ARMED.store(false, Ordering::SeqCst);
    HTTP_ROUTE_INVOKE_AFTER_DEPENDENCIES_BEFORE_ARMED.store(false, Ordering::SeqCst);
}
