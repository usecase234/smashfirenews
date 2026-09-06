"""
Seed Buddy Magazine as Publisher/Tenant #001.

Run after `alembic upgrade head`:

    python scripts/seed_buddy_magazine.py

Idempotent: re-running finds the existing publisher by slug and leaves it
alone rather than creating a duplicate tenant. Issuing a fresh installation
credential is a separate, explicit step (--reissue-credential) so re-running
the seed never silently invalidates a plugin that's already configured.
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy.exc import OperationalError

from app.core.security import generate_installation_token, hash_token
from app.db.models.publisher import Publisher, PublisherInstallation
from app.db.session import SessionLocal

BUDDY_SLUG = "buddy-magazine"
BUDDY_NAME = "Buddy Magazine"


def seed(reissue_credential: bool = False) -> None:
    db = SessionLocal()
    try:
        publisher = db.query(Publisher).filter(Publisher.slug == BUDDY_SLUG).one_or_none()
        if publisher is None:
            publisher = Publisher(slug=BUDDY_SLUG, name=BUDDY_NAME, status="active")
            db.add(publisher)
            db.flush()  # assign publisher.id
            print(f"created publisher {publisher.slug!r} as publisher_id={publisher.id}")
        else:
            print(f"publisher {publisher.slug!r} already exists as publisher_id={publisher.id}")

        needs_credential = reissue_credential or not publisher.installations
        if needs_credential:
            token = generate_installation_token()
            installation = PublisherInstallation(
                publisher_id=publisher.id,
                site_id="buddy-magazine-primary",
                site_url="https://buddymagazine.example",
                credential_hash=hash_token(token),
                status="active",
            )
            db.add(installation)
            db.commit()
            print("issued installation credential (shown once — store it in the plugin config now):")
            print(f"  {token}")
        else:
            db.commit()
            print(
                f"publisher already has {len(publisher.installations)} installation(s); "
                "pass --reissue-credential to add a new one"
            )
    except OperationalError as exc:
        db.rollback()
        print(
            "database error — has `alembic upgrade head` been run against this DATABASE_URL?",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reissue-credential",
        action="store_true",
        help="issue a new installation credential even if Buddy already has one",
    )
    args = parser.parse_args()
    seed(reissue_credential=args.reissue_credential)
