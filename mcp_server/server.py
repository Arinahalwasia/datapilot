from mcp.server.mcpserver import MCPServer

from mcp_server.tools.schema import (
    list_tables_impl,
    describe_table_impl,
    get_sample_rows_impl,
)

from mcp_server.tools.sql import (
    execute_sql_impl,
)


mcp = MCPServer(
    "DataPilot Analytics Server"
)


@mcp.tool()
def list_tables() -> list[str]:
    """
    List all available database tables.
    """

    return list_tables_impl()


@mcp.tool()
def describe_table(table_name: str) -> dict:
    """
    Describe the columns, types, nullability and primary keys
    of a database table.

    Args:
        table_name: Name of the table to inspect.
    """

    return describe_table_impl(table_name)


@mcp.tool()
def get_sample_rows(
    table_name: str,
    limit: int = 5,
) -> dict:
    """
    Retrieve sample rows from a database table.

    Args:
        table_name: Name of the table.
        limit: Maximum number of rows to return.
    """

    return get_sample_rows_impl(
        table_name,
        limit,
    )


@mcp.tool()
def execute_sql(
    query: str,
    limit: int = 100,
) -> dict:
    """
    Execute a read-only SQL query against the analytics database.

    Only SELECT, WITH and EXPLAIN queries are allowed.

    Args:
        query: SQL query to execute.
        limit: Maximum number of rows returned.
    """

    return execute_sql_impl(
        query,
        limit,
    )


if __name__ == "__main__":
    mcp.run()