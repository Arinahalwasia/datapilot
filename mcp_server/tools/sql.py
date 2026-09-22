import os

from sqlalchemy import text

from mcp_server.db import engine
from mcp_server.validators import validate_read_only_sql


# Used only for controlled testing of agent self-correction.
_test_error_triggered = False


def execute_sql_impl(query: str, limit: int = 100) -> dict:

    global _test_error_triggered

    # ---------------------------------------------------------
    # 1. Validate SQL
    # ---------------------------------------------------------

    try:
        query = validate_read_only_sql(query)

    except Exception as e:

        return {
            "success": False,
            "error_type": "validation_error",
            "error": str(e),
            "query": query,
        }

    # ---------------------------------------------------------
    # 2. Validate limit
    # ---------------------------------------------------------

    if limit < 1:

        return {
            "success": False,
            "error_type": "validation_error",
            "error": "limit must be greater than 0.",
            "query": query,
        }

    if limit > 1000:
        limit = 1000

    # ---------------------------------------------------------
    # 3. Controlled SQL error injection
    # ---------------------------------------------------------

    test_error_enabled = (
        os.getenv("DATAPILOT_TEST_SQL_ERROR", "false").lower()
        == "true"
    )

    if test_error_enabled and not _test_error_triggered:

        _test_error_triggered = True

        return {
            "success": False,
            "error_type": "database_error",
            "error": (
                'column "intentional_test_error" does not exist'
            ),
            "query": query,
        }

    # ---------------------------------------------------------
    # 4. Execute SQL normally
    # ---------------------------------------------------------

    try:

        with engine.connect() as connection:

            result = connection.execute(text(query))

            columns = list(result.keys())

            rows = [
                dict(row._mapping)
                for row in result.fetchmany(limit)
            ]

        return {
            "success": True,
            "query": query,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "limit": limit,
        }

    except Exception as e:

        return {
            "success": False,
            "error_type": "database_error",
            "error": str(e),
            "query": query,
        }