# Smashfire PR

AI newsroom intake and editorial queue. Independently-deployed multi-tenant
Hub + a thin WordPress plugin (Buddy Magazine is Tenant #001).

See `docs/` for the full product/architecture plan and the phased build plan.
See `CLAUDE.md` for the rules Claude Code should follow in this repo and the
current phase status.

## Local dev

```bash
cp infra/.env.example infra/.env    # fill in secrets
cd infra
docker compose up --build
```

- Hub: http://localhost:8000/health
- WordPress (optional, plugin dev only): http://localhost:8080

## Running Hub tests directly (no docker)

```bash
cd hub
pip install -e ".[dev]"
pytest
```
