from pydantic import BaseModel, field_validator

MAX_TITLE_LENGTH = 200
MAX_TEXT_LENGTH = 100_000


class DocumentCreate(BaseModel):
    """The body of POST /documents. Fields not listed here are ignored."""

    title: str
    text: str

    @field_validator("title")
    @classmethod
    def trim_and_check_title(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("title must not be empty")
        if len(trimmed) > MAX_TITLE_LENGTH:
            raise ValueError(f"title must be at most {MAX_TITLE_LENGTH} characters")
        return trimmed

    @field_validator("text")
    @classmethod
    def check_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty")
        if len(value) > MAX_TEXT_LENGTH:
            raise ValueError(f"text must be at most {MAX_TEXT_LENGTH} characters")
        return value


class Document(BaseModel):
    """A stored document, as returned by POST and GET /documents/{id}."""

    id: int
    title: str
    text: str
    created_at: str


class DocumentSummary(BaseModel):
    """One item in the GET /documents list: a document without its text."""

    id: int
    title: str
    created_at: str
