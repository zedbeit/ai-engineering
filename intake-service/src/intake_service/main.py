from contextlib import closing
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException

from intake_service import db
from intake_service.models import Document, DocumentCreate, DocumentSummary

app = FastAPI()


def now_utc() -> str:
    """The current time as ISO 8601 in UTC, to the second: 2026-11-16T09:30:00Z."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@app.post("/documents", status_code=201)
def create_document(body: DocumentCreate) -> Document:
    created_at = now_utc()
    with closing(db.connect()) as connection:
        document_id = db.insert_document(connection, body.title, body.text, created_at)
    return Document(
        id=document_id, title=body.title, text=body.text, created_at=created_at
    )


@app.get("/documents")
def list_documents(search: str | None = None) -> list[DocumentSummary]:
    with closing(db.connect()) as connection:
        return db.list_documents(connection, search)


@app.get("/documents/{document_id}")
def get_document(document_id: int) -> Document:
    with closing(db.connect()) as connection:
        document = db.get_document(connection, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: int) -> None:
    with closing(db.connect()) as connection:
        deleted = db.delete_document(connection, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
