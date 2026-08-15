from field_dispatch.dispatch_policy import choose_dispatch_status
from field_dispatch.work_order_models import DispatchStatus, WorkOrderRequest


def test_urgent_documented_order_dispatches_now() -> None:
    order = WorkOrderRequest.model_validate(
        {
            "work_order_id": "WO-1842",
            "customer_summary": "Cooler stopped after a compressor rattle.",
            "priority": "urgent",
            "site_safety": "clear",
            "photos": [
                {"url": "https://example.com/compressor.jpg", "caption": "Compressor label"},
                {"url": "https://example.com/panel.jpg", "caption": "Panel indicator"},
            ],
        }
    )

    assert choose_dispatch_status(order) is DispatchStatus.DISPATCH_NOW


def test_safety_hold_precedes_urgent_dispatch() -> None:
    order = WorkOrderRequest.model_validate(
        {
            "work_order_id": "WO-1843",
            "customer_summary": "Water is visible beside the electrical cabinet.",
            "priority": "urgent",
            "site_safety": "hold",
            "photos": [
                {"url": "https://example.com/cabinet.jpg", "caption": "Wet cabinet floor"},
                {"url": "https://example.com/breaker.jpg", "caption": "Breaker panel"},
            ],
        }
    )

    assert choose_dispatch_status(order) is DispatchStatus.SAFETY_REVIEW
