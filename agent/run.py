import asyncio

from mcp import Client, StdioServerParameters

from mcp_client.manager import MCPToolManager

from agent.graph import build_graph

import logging

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("core.llm").setLevel(logging.WARNING)

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

        # Create MCP manager
        manager = MCPToolManager(client)

        # Build LangGraph agent
        graph = build_graph(manager)

        # Ask a question
        question = (
            "Why was October 2025 revenue higher than September 2025? "
            "Investigate the database and explain the main factors contributing to "
            "the difference."
        )
        print()
        print("╭──────────────────────────────────────────────╮")
        print("│              🚀 DataPilot                   │")
        print("│         AI-Powered Data Analyst              │")
        print("╰──────────────────────────────────────────────╯")
        print()
        print("🤖 Model: Gemma 4 31B")
        print("🔌 MCP: Connected")
        print()
        print("────────────────────────────────────────────────")
        print("QUESTION")
        print("────────────────────────────────────────────────")
        print(question)
        print()
        print("────────────────────────────────────────────────")
        print("INVESTIGATION")
        print("────────────────────────────────────────────────")
        result = await graph.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "sql_retries": 0,
                "investigation": [],
            },
            config={"recursion_limit": 30},
        )

        final_answer = result["messages"][-1].content
        print()
        print("==============================")
        print("DataPilot Final Answer")
        print("==============================")
        print()
        print(final_answer)
        print("==============================")
        print("\n==============================")
        print("DataPilot Investigation Trace")
        print("==============================")

        investigation = result.get("investigation", [])

        print()
        print("────────────────────────────────────────────────")
        print("EVIDENCE COLLECTED")
        print("────────────────────────────────────────────────")

        for i, event in enumerate(investigation, start=1):

            if event["type"] != "evidence":
                continue

            print(f"\n[{i}] 📊 SQL Evidence")

            if event.get("success"):
                print("    ✓ Query executed successfully")

                rows = event.get("rows", [])

                print(f"    ✓ Rows returned: {len(rows)}")

                if rows:
                    print("    ✓ Result:")

                    for row in rows:
                        print(f"      {row}")

            else:
                print("    ✗ Query failed")
                print(f"    Error: {event.get('error')}")

        for message in result["messages"]:
            print("\n", message)


if __name__ == "__main__":
    asyncio.run(main())