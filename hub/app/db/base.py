"""
Declarative base for all Hub models.

Phase 1 adds Tenant/Publisher here plus a mixin that every subsequent
tenant-scoped table inherits for publisher_id — see
docs/Smashfire_PR_Starting_Build_Plan.md, Phase 1.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
