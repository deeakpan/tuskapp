from collections.abc import Iterator
from contextlib import contextmanager

from msflib.db.sqlite import enable_savepoints
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

from tusk_mcp.core.config import settings

if settings.USE_SQLITE:
    url = settings.SQLITE_DATABASE_URI
    in_memory = {"poolclass": StaticPool} if url in ("sqlite://", "sqlite:///:memory:") else {}
    engine = enable_savepoints(
        create_engine(
            url,
            connect_args={"check_same_thread": False},
            echo=settings.DB_DEBUG_MODE,
            **in_memory,
        )
    )
else:
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True, echo=settings.DB_DEBUG_MODE
    )


@contextmanager
def session_scope() -> Iterator[Session]:
    """A session for code that runs outside a FastAPI request, such as MCP tools."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
