"""
Request/response shapes for the submissions API.

Kept separate from app/db/models so the wire format can diverge from storage
without touching the ORM — e.g. SubmissionSummary omits body_text because the
Pre-Writer queue only needs a preview, not the full release.
"""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict


# Plain str, not EmailStr: real validation (plus Turnstile/rate limits) is
# Phase 5. Adding the email-validator dependency now for a check Phase 5
# will redo properly isn't worth it.
class SubmissionCreate(BaseModel):
    headline: str
    body_text: str
    sender_name: str
    sender_email: str
    sender_company: str | None = None


class SubmissionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    headline: str
    sender_name: str
    sender_company: str | None
    status: str
    created_at: dt.datetime


class DraftVersionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_id: int
    version: int
    body_text: str
    generator: str
    created_at: dt.datetime


class SubmissionDetail(SubmissionSummary):
    body_text: str
    sender_email: str
    wp_post_id: int | None
    live_url: str | None
    published_at: dt.datetime | None
    drafts: list[DraftVersionOut]


class PublishRequest(BaseModel):
    wp_post_id: int
    live_url: str
