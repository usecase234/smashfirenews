"""
Tenant-scoping primitives shared by every tenant-owned table.

Hard rule from docs/Smashfire_PR_Full_Product_Technical_Plan_2026.md: every
Hub table carries `publisher_id` from its first migration, and no
tenant-scoped query path is allowed to omit the tenant filter. This module
is the *only* supported way to read a `TenantScopedMixin` table — routes and
services should never hand-write `select(Model).where(...)` for a
tenant-scoped model.
"""
from __future__ import annotations

from typing import TypeVar

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import Select, select

ModelT = TypeVar("ModelT", bound="TenantScopedMixin")


class TenantScopedMixin:
    """Mixin for every table that belongs to exactly one publisher/tenant.

    Inheriting this (instead of adding an ad-hoc `publisher_id` column) is
    what makes the FK, the index, and the NOT NULL constraint consistent
    across tables, and is what `tenant_scoped_select` relies on existing.
    """

    publisher_id: Mapped[int] = mapped_column(
        ForeignKey("publishers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class MissingTenantScopeError(RuntimeError):
    """Raised when a tenant-scoped query is built without a valid publisher_id.

    This is a programmer error, not a runtime/user error — it means a code
    path tried to read a tenant-scoped table without first resolving a
    tenant, which is exactly the class of bug Phase 1's isolation test
    exists to catch.
    """


def tenant_scoped_select(model: type[ModelT], publisher_id: int) -> Select:
    """Build a `SELECT * FROM <model>` that is always filtered to one tenant.

    This is intentionally the single choke point for reading tenant-scoped
    tables. `publisher_id` must be a resolved tenant id (see
    app/core/tenancy.py) — never a value that could be missing, None, or
    attacker-controlled without having been authenticated first.
    """
    if not issubclass(model, TenantScopedMixin):
        raise MissingTenantScopeError(
            f"{model.__name__} is not a TenantScopedMixin model; "
            "tenant_scoped_select only applies to tenant-owned tables"
        )
    if not isinstance(publisher_id, int) or isinstance(publisher_id, bool) or publisher_id <= 0:
        raise MissingTenantScopeError(
            f"refusing to build a {model.__name__} query without a resolved publisher_id "
            f"(got {publisher_id!r})"
        )
    return select(model).where(model.publisher_id == publisher_id)
