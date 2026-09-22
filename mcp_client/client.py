import asyncio

from mcp import Client, StdioServerParameters

from mcp_client.manager import MCPToolManager


server = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "--with-editable",
        ".",
        "mcp",
        "run",
        "mcp_server/server.py",
    ],
)


async def main():

    async with Client(server) as client:

        print("\nConnected to DataPilot MCP Server")

        manager = MCPToolManager(client)

        # Discover tools
        tools_result = await client.list_tools()

        print("\nAvailable tools:")

        for tool in tools_result.tools:
            print(f"- {tool.name}")

        # Test list_tables
        print("\n--- list_tables() ---")

        result = await manager.list_tables()

        print(result)

        # Test describe_table
        print("\n--- describe_table('orders') ---")

        result = await manager.describe_table("orders")

        print(result)

        # Test sample rows
        print("\n--- get_sample_rows('customers') ---")

        result = await manager.get_sample_rows(
            "customers",
            3
        )

        print(result)

        # Test SQL
        print("\n--- execute_sql() ---")

        result = await manager.execute_sql(
            """
            SELECT
                region,
                COUNT(*) AS customer_count
            FROM customers
            GROUP BY region
            ORDER BY customer_count DESC
            """
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())