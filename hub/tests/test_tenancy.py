"""
Phase 1 isolation test (docs/Smashfire_PR_Starting_Build_Plan.md).

Proves a tenant-scoped query can never return another tenant's rows -- by
inspecting the compiled query's WHERE clause, not just the rows it happens to
return, so this catches a future table that "forgets" to go through
`tenant_scoped_select` even before data makes the mistake visible.
"""
from __future__ import annotations

import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models.publisher import Publisher
from app.db.tenancy import MissingTenantScopeError, TenantScopedMixin, tenant_scoped_select


class _WidgetForTest(Base, TenantScopedMixin):
    """Stand-in for a future tenant-owned table -- Phase 1 has no real one yet."""

    __tablename__ = "test_widgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


def _make_publisher(db, slug: str) -> Publisher:
    publisher = Publisher(slug=slug, name=slug)
    db.add(publisher)
    db.flush()
    return publisher


def test_tenant_scoped_select_filters_by_publisher_id_in_the_query_itself(db_session):
    buddy = _make_publisher(db_session, "buddy-magazine")
    db_session.add(_WidgetForTest(publisher_id=buddy.id, name="only widget"))
    db_session.commit()

    stmt = tenant_scoped_select(_WidgetForTest, buddy.id)
    compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))

    assert "test_widgets.publisher_id" in compiled
    assert f"= {buddy.id}" in compiled


def test_tenant_scoped_select_excludes_other_tenants_rows(db_session):
    buddy = _make_publisher(db_session, "buddy-magazine")
    other = _make_publisher(db_session, "some-other-publisher")
    db_session.add_all(
        [
            _WidgetForTest(publisher_id=buddy.id, name="buddy widget"),
            _WidgetForTest(publisher_id=other.id, name="other widget"),
        ]
    )
    db_session.commit()

    rows = db_session.scalars(tenant_scoped_select(_WidgetForTest, buddy.id)).all()

    assert [r.name for r in rows] == ["buddy widget"]


def test_tenant_scoped_select_refuses_unresolved_publisher_id():
    with pytest.raises(MissingTenantScopeError):
        tenant_scoped_select(_WidgetForTest, None)

    with pytest.raises(MissingTenantScopeError):
        tenant_scoped_select(_WidgetForTest, 0)


def test_tenant_scoped_select_refuses_non_tenant_scoped_model():
    with pytest.raises(MissingTenantScopeError):
        tenant_scoped_select(Publisher, 1)
