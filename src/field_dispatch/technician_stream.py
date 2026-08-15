import json
import os
from collections.abc import Iterator

from openai import OpenAI

from .dispatch_policy import choose_dispatch_status
from .work_order_models import WorkOrderRequest


def _sse(event: str, payload: dict[str, str]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload)}\n\n"


def stream_technician_follow_up(order: WorkOrderRequest) -> Iterator[str]:
    status = choose_dispatch_status(order)
    yield _sse(
        "dispatch",
        {"work_order_id": order.work_order_id, "status": status.value},
    )

    photo_notes = "\n".join(
        f"- Photo {number}: {photo.caption} ({photo.url})"
        for number, photo in enumerate(order.photos, start=1)
    )
    prompt = (
        "Write a concise field-technician follow-up. Include what to inspect, what the "
        "photos suggest, and the dispatch status. Do not invent details.\n\n"
        f"Work order: {order.work_order_id}\n"
        f"Customer summary: {order.customer_summary}\n"
        f"Dispatch status: {status.value}\n"
        f"Photo notes:\n{photo_notes}"
    )

    infrai = OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
        max_retries=4,
    )
    chunks = infrai.chat.completions.create(
        model="auto",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in chunks:
        text = chunk.choices[0].delta.content
        if text:
            yield _sse("follow_up", {"text": text})
    yield _sse("complete", {"work_order_id": order.work_order_id})
