"""PostgreSQL checkpointer for conversation persistence."""

import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from psycopg.rows import DictRow, dict_row
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

load_dotenv()


async def create_checkpointer() -> AsyncPostgresSaver:
    """
    Initialize PostgreSQL checkpointer for conversation persistence.

    Creates database connection pool and sets up required tables:
    - checkpoints: Stores conversation state snapshots
    - checkpoint_blobs: Stores large binary data
    - checkpoint_writes: Tracks checkpoint write operations

    Returns:
        AsyncPostgresSaver: Configured checkpointer instance
    """
    # Get PostgreSQL URI from environment
    postgres_uri = os.getenv("POSTGRES_URI_CUSTOM")

    if not postgres_uri:
        raise ValueError("POSTGRES_URI_CUSTOM environment variable is required")

    # Create async connection pool with proper typing for type checker
    pool: AsyncConnectionPool[AsyncConnection[DictRow]] = AsyncConnectionPool(
        conninfo=postgres_uri,
        max_size=20,
        kwargs={
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row
        },
        open=False,
    )

    await pool.open()

    checkpointer = AsyncPostgresSaver(conn=pool)
    await checkpointer.setup()

    return checkpointer
