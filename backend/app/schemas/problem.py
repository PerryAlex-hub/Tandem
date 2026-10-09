from pydantic import BaseModel, ConfigDict


class ProblemOut(BaseModel):
    frontend_id: int
    title_slug: str
    title: str
    difficulty: str
    description_html: str
    example_testcases: str
    topic_tags: list
    code_snippets: list

    model_config = ConfigDict(from_attributes=True)
