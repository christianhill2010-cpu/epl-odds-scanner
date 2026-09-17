from pydantic import BaseModel


class RawOddsEvent(BaseModel):
    provider_event_id: str
    home_team: str
    away_team: str
