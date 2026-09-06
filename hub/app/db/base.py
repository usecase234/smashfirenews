"""
Declarative base for all Hub models.

Every table other than `publishers` itself is tenant-scoped: it inherits
`TenantScopedMixin` (app/db/tenancy.py) and carries `publisher_id` from its
first migration. See docs/Smashfire_PR_Starting_Build_Plan.md, Phase 1.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models so they register on Base.metadata for Alembic autogenerate
# and for `Base.metadata.create_all()` in tests.
from app.db.models import publisher  # noqa: E402, F401
