from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from .technician_stream import stream_technician_follow_up
from .work_order_models import WorkOrderRequest


service = FastAPI(title="Field dispatch stream")


@service.post("/work-orders/follow-up")
def follow_up(order: WorkOrderRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_technician_follow_up(order),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
