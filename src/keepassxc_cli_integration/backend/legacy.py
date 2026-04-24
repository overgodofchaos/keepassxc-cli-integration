from pydantic import BaseModel


class Associate(BaseModel):
    db_hash: str
    id: str
    key: str


class Associates(BaseModel):
    entries: dict[str, Associate] | None



class Settings(BaseModel):
    associates: Associates | None