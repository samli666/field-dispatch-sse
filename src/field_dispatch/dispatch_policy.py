from .work_order_models import DispatchStatus, Priority, SiteSafety, WorkOrderRequest


def choose_dispatch_status(order: WorkOrderRequest) -> DispatchStatus:
    """Make the operational decision before model-generated follow-up begins."""
    if order.site_safety is SiteSafety.HOLD:
        return DispatchStatus.SAFETY_REVIEW
    if order.priority is Priority.URGENT and len(order.photos) >= 2:
        return DispatchStatus.DISPATCH_NOW
    return DispatchStatus.READY_TO_SCHEDULE
