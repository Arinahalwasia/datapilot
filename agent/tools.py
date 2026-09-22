from typing import Any
from langchain_core.tools import StructuredTool
from mcp_client.manager import MCPToolManager


def normalize_result(result: Any) -> Any:
    """
    Convert MCP CallToolResult into a simple Python structure
    that LangChain/Gemma can easily understand.
    """

    # MCP Pydantic result
    if hasattr(result, "structured_content") and result.structured_content:
        return result.structured_content

    # MCP text content
    if hasattr(result, "content"):
        contents = []

        for item in result.content:
            if hasattr(item, "text"):
                contents.append(item.text)

        if len(contents) == 1:
            return contents[0]

        return contents

    # Fallback
    return result


def create_mcp_tools(manager: MCPToolManager) -> list[StructuredTool]:

    async def list_tables() -> Any:
        result = await manager.list_tables()
        return normalize_result(result)

    async def describe_table(table_name: str) -> Any:
        result = await manager.describe_table(table_name)
        return normalize_result(result)

    async def get_sample_rows(
        table_name: str,
        limit: int = 5
    ) -> Any:
        result = await manager.get_sample_rows(
            table_name,
            limit
        )
        return normalize_result(result)

    async def execute_sql(
        query: str,
        limit: int = 100
    ) -> Any:
        result = await manager.execute_sql(
            query,
            limit
        )
        return normalize_result(result)

    return [

        StructuredTool.from_function(
            coroutine=list_tables,
            name="list_tables",
            description=(
                "List all available tables in the analytics database. "
                "Use this when you need to discover the database schema."
            ),
        ),

        StructuredTool.from_function(
            coroutine=describe_table,
            name="describe_table",
            description=(
                "Describe a database table including its columns, "
                "data types, nullability and primary keys. "
                "Use this before writing SQL when you need to "
                "understand the structure of a table."
            ),
        ),

        StructuredTool.from_function(
            coroutine=get_sample_rows,
            name="get_sample_rows",
            description=(
                "Retrieve sample rows from a database table. "
                "Use this when you need to understand the actual "
                "data stored in a table."
            ),
        ),

        StructuredTool.from_function(
            coroutine=execute_sql,
            name="execute_sql",
            description=(
                "Execute a read-only SQL query against the analytics "
                "database. Only SELECT, WITH and EXPLAIN queries are "
                "allowed. Use this to answer analytical questions "
                "that require querying the database."
            ),
        ),
    ]