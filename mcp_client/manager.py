class MCPToolManager:

    def __init__(self, client):
        self.client = client

    async def list_tables(self):
        result = await self.client.call_tool(
            "list_tables",
            {}
        )

        return result

    async def describe_table(self, table_name: str):
        result = await self.client.call_tool(
            "describe_table",
            {
                "table_name": table_name
            }
        )

        return result

    async def get_sample_rows(
        self,
        table_name: str,
        limit: int = 5
    ):
        result = await self.client.call_tool(
            "get_sample_rows",
            {
                "table_name": table_name,
                "limit": limit
            }
        )

        return result

    async def execute_sql(
        self,
        query: str,
        limit: int = 100
    ):
        result = await self.client.call_tool(
            "execute_sql",
            {
                "query": query,
                "limit": limit
            }
        )

        return result