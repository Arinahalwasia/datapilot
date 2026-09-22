from sqlalchemy import inspect, text

from mcp_server.db import engine


def list_tables_impl() -> list[str]:
    """Return all user tables in the public schema."""

    inspector = inspect(engine)

    tables = inspector.get_table_names(
        schema="public"
    )

    return sorted(tables)


def describe_table_impl(table_name: str) -> dict:
    """Return column metadata for a table."""

    inspector = inspect(engine)

    tables = inspector.get_table_names(
        schema="public"
    )

    if table_name not in tables:
        raise ValueError(
            f"Table '{table_name}' does not exist."
        )

    columns = inspector.get_columns(
        table_name,
        schema="public",
    )

    primary_keys = inspector.get_pk_constraint(
        table_name,
        schema="public",
    ).get("constrained_columns", [])

    return {
        "table_name": table_name,
        "columns": [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "default": str(column["default"])
                if column["default"] is not None
                else None,
                "primary_key": column["name"] in primary_keys,
            }
            for column in columns
        ],
    }


def get_sample_rows_impl(
    table_name: str,
    limit: int = 5,
) -> dict:
    """Return sample rows from a table."""

    if limit < 1:
        raise ValueError("limit must be greater than 0.")

    if limit > 100:
        limit = 100

    # Validate table against known tables rather than interpolating
    # arbitrary user input into SQL.
    tables = list_tables_impl()

    if table_name not in tables:
        raise ValueError(
            f"Table '{table_name}' does not exist."
        )

    query = text(
        f'SELECT * FROM "{table_name}" LIMIT :limit'
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"limit": limit},
        )

        rows = [
            dict(row._mapping)
            for row in result
        ]

    return {
        "table_name": table_name,
        "row_count": len(rows),
        "rows": rows,
    }