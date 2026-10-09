from pydantic import BaseModel, ConfigDict


class ProblemCatalogOut(BaseModel):
    frontend_id: int
    title_slug: str
    title: str
    difficulty: str

    model_config = ConfigDict(from_attributes=True)
