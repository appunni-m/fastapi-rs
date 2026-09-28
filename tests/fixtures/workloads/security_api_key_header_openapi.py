"""Independent OpenAPI workload for a default-named APIKeyHeader dependency."""

from fastapi import Depends, FastAPI, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

roster_ticket = APIKeyHeader(name="x-roster-ticket")


class RosterCard(BaseModel):
    callsign: str


def resolve_roster_card(ticket: str = Security(roster_ticket)) -> RosterCard:
    return RosterCard(callsign=ticket)


def create_app() -> FastAPI:
    app = FastAPI(title="Partner Roster", version="2.0")

    @app.get("/roster/profile")
    def read_roster_profile(
        card: RosterCard = Depends(resolve_roster_card),  # noqa: B008
    ) -> RosterCard:
        return card

    return app
