import os
import sqlite3

from intake_service.models import Document, DocumentSummary

DEFAULT_DB_PATH = "intake.db"

# SQLite stores integers in 64 bits. A larger id can't be passed to a query
# (sqlite3 raises OverflowError), and no document can have one anyway.
MAX_SQLITE_INTEGER = 2**63 - 1

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    text       TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def connect() -> sqlite3.Connection:
    """Open the database named by INTAKE_DB_PATH, creating the table if needed.

    The path is read on every call, so each test can point at its own file.
    The caller closes the connection.
    """
    path = os.environ.get("INTAKE_DB_PATH", DEFAULT_DB_PATH)
    connection = sqlite3.connect(path)
    connection.execute(CREATE_TABLE)
    return connection


def insert_document(
    connection: sqlite3.Connection, title: str, text: str, created_at: str
) -> int:
    """Store a document and return its new id."""
    cursor = connection.execute(
        "INSERT INTO documents (title, text, created_at) VALUES (?, ?, ?)",
        (title, text, created_at),
    )
    connection.commit()
    document_id = cursor.lastrowid
    if document_id is None:
        raise RuntimeError("SQLite did not return an id for the new document")
    return document_id


def get_document(connection: sqlite3.Connection, document_id: int) -> Document | None:
    """Return the document with this id, or None if there isn't one."""
    if abs(document_id) > MAX_SQLITE_INTEGER:
        return None
    row = connection.execute(
        "SELECT id, title, text, created_at FROM documents WHERE id = ?",
        (document_id,),
    ).fetchone()
    if row is None:
        return None
    return Document(id=row[0], title=row[1], text=row[2], created_at=row[3])


def delete_document(connection: sqlite3.Connection, document_id: int) -> bool:
    """Delete the document with this id. Return False if there wasn't one."""
    if abs(document_id) > MAX_SQLITE_INTEGER:
        return False
    cursor = connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    connection.commit()
    return cursor.rowcount > 0


def escape_like(term: str) -> str:
    """Make % and _ in a search term match themselves in a LIKE pattern.

    In SQL's LIKE, % means "any characters" and _ means "any one character".
    Putting a backslash in front turns each back into an ordinary character.
    The backslash itself is escaped first so it stays ordinary too.
    """
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_documents(
    connection: sqlite3.Connection, search: str | None
) -> list[DocumentSummary]:
    """Return summaries of all documents, oldest first.

    With a search term, only documents whose title or text contains it.
    LIKE ignores case for the letters A to Z.
    """
    if search:
        pattern = "%" + escape_like(search) + "%"
        rows = connection.execute(
            "SELECT id, title, created_at FROM documents "
            "WHERE title LIKE ? ESCAPE '\\' OR text LIKE ? ESCAPE '\\' "
            "ORDER BY id",
            (pattern, pattern),
        ).fetchall()
    else:
        rows = connection.execute(
            "SELECT id, title, created_at FROM documents ORDER BY id"
        ).fetchall()
    return [DocumentSummary(id=row[0], title=row[1], created_at=row[2]) for row in rows]
