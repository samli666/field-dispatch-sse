from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class Priority(str, Enum):
    ROUTINE = "routine"
    URGENT = "urgent"


class SiteSafety(str, Enum):
    CLEAR = "clear"
    HOLD = "hold"


class WorkPhoto(BaseModel):
    url: HttpUrl
    caption: str = Field(min_length=1, max_length=240)


class WorkOrderRequest(BaseModel):
    work_order_id: str = Field(min_length=1, max_length=80)
    customer_summary: str = Field(min_length=1, max_length=1000)
    priority: Priority
    site_safety: SiteSafety = SiteSafety.CLEAR
    photos: list[WorkPhoto] = Field(min_length=1, max_length=8)


class DispatchStatus(str, Enum):
    SAFETY_REVIEW = "safety_review"
    DISPATCH_NOW = "dispatch_now"
    READY_TO_SCHEDULE = "ready_to_schedule"
