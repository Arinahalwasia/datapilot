from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from core.llm import get_llm
from mcp_client.manager import MCPToolManager
from agent.tools import create_mcp_tools

import json

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    sql_retries: int
    investigation: list[dict]


MAX_SQL_RETRIES = 3


SYSTEM_PROMPT = """
You are DataPilot, an AI data analyst.

Your job is to answer the user's analytical questions using the available
database tools.

You have access to these tools:

1. list_tables
   - Use this to discover available database tables.

2. describe_table
   - Use this to understand the columns and structure of a table.

3. get_sample_rows
   - Use this when you need to inspect actual example data.

4. execute_sql
   - Use this to execute read-only SQL queries.

Rules:

- Use database tools when the answer depends on database data.
- Do not guess database values.
- Before writing SQL, make sure you understand the relevant table structure.
- Generate valid PostgreSQL SQL.
- Only generate read-only SQL.
- Prefer simple and efficient queries.
- Use execute_sql to verify your SQL and obtain the actual result.


Error recovery:

- If execute_sql returns success=false, inspect the error carefully.
- Determine whether the SQL can be corrected from the error.
- If the error indicates an invalid table, column, function, syntax,
  or other SQL problem, correct the SQL and try again.
- Use the database schema when necessary to determine the correct
  table or column.
- Never invent database values.
- Do not repeat the exact same failed SQL query unnecessarily.
- Stop attempting SQL when a valid result has been obtained.

General behavior:

- After obtaining sufficient information from the database, answer the user.
- Do not repeatedly call the same tool when the required information is already available.
- Do not call tools unnecessarily.
- Clearly explain the result in natural language.

Investigation behavior:

- Treat complex analytical questions as investigations.
- Break the question into smaller analytical steps when necessary.
- Use database tools to gather the evidence required for each step.
- After receiving a tool result, decide whether additional investigation
  is required before answering.
- Do not assume that one SQL query is always sufficient.
- Use previous query results as evidence for subsequent analysis.
- When comparing values or trends, obtain the underlying data from the
  database rather than estimating.
- Stop investigating once sufficient evidence has been collected to
  answer the user's question.
"""

def record_investigation_event(
    state: AgentState,
    event_type: str,
    content: dict,
):
    investigation = list(state.get("investigation", []))

    investigation.append(
        {
            "type": event_type,
            **content,
        }
    )

    return investigation


def build_graph(mcp_manager: MCPToolManager):

    llm = get_llm(
        temperature=0.2,
        streaming=False,
        parallel_tool_calls=False,
    )

    tools = create_mcp_tools(mcp_manager)

    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: AgentState):

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ]

        sql_retries = state.get("sql_retries", 0)
        investigation = list(state.get("investigation", []))

        # Check whether the previous tool execution failed
        # and record successful/failed SQL as investigation evidence.
        last_message = state["messages"][-1]

        if getattr(last_message, "name", None) == "execute_sql":

            content = last_message.content

            if isinstance(content, str):
                try:
                    result = json.loads(content)

                    # Count only failed SQL executions as retries
                    if result.get("success") is False:
                        sql_retries += 1

                    # Record SQL execution as investigation evidence
                    investigation.append(
                        {
                            "type": "evidence",
                            "source": "execute_sql",
                            "query": result.get("query"),
                            "success": result.get("success"),
                            "columns": result.get("columns"),
                            "rows": result.get("rows"),
                            "error": result.get("error"),
                        }
                    )

                except (json.JSONDecodeError, TypeError):
                    pass

        response = llm_with_tools.invoke(messages)

        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]

                if tool_name == "execute_sql":
                    print("  → Running SQL analysis")
                elif tool_name == "list_tables":
                    print("  → Discovering database tables")
                elif tool_name == "describe_table":
                    table_name = tool_call["args"].get("table_name", "")
                    print(f"  → Inspecting table: {table_name}")
                elif tool_name == "get_sample_rows":
                    table_name = tool_call["args"].get("table_name", "")
                    print(f"  → Sampling table: {table_name}")

        return {
            "messages": [response],
            "sql_retries": sql_retries,
            "investigation": investigation,
        }


    tool_node = ToolNode(tools)

    def should_continue(state: AgentState):

        last_message = state["messages"][-1]

        if getattr(last_message, "tool_calls", None):

            if state["sql_retries"] >= MAX_SQL_RETRIES:

                print(
                    f"\nMaximum SQL retry limit "
                    f"({MAX_SQL_RETRIES}) reached."
                )

                return END

            return "tools"

        return END

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("model", call_model)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "model")

    graph_builder.add_conditional_edges(
        "model",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    graph_builder.add_edge("tools", "model")

    return graph_builder.compile()