use std::sync::atomic::{AtomicBool, Ordering};

const HTTP_ROUTE_INVOKE_BEFORE: &str = "http.route.invoke.before";

static HTTP_ROUTE_INVOKE_BEFORE_ARMED: AtomicBool = AtomicBool::new(false);

pub(crate) fn arm(point: &str) -> Result<(), &'static str> {
    if point != HTTP_ROUTE_INVOKE_BEFORE {
        return Err("unknown fault injection point");
    }

    HTTP_ROUTE_INVOKE_BEFORE_ARMED
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .map(|_| ())
        .map_err(|_| "fault injection point is already armed")
}

pub(crate) fn take_http_route_invoke_before() -> bool {
    HTTP_ROUTE_INVOKE_BEFORE_ARMED.swap(false, Ordering::SeqCst)
}

pub(crate) fn clear() {
    HTTP_ROUTE_INVOKE_BEFORE_ARMED.store(false, Ordering::SeqCst);
}
