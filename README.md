# DataPilot — MCP-Powered AI Data Analyst

> An agentic data-analysis platform that uses Gemma 4, LangGraph, MCP, and PostgreSQL to autonomously investigate business questions through schema discovery, multi-step SQL analysis, self-correcting queries, and evidence-backed reasoning.

---

## 🚀 Overview

DataPilot is an AI-powered data analyst that allows users to ask natural-language questions about a PostgreSQL database.

Instead of manually writing SQL, the agent can:

- Discover available database tables
- Inspect table schemas
- Retrieve sample data
- Generate SQL queries
- Execute read-only SQL through MCP tools
- Detect and recover from SQL errors
- Perform multi-step investigations
- Collect evidence from multiple queries
- Use previous results to guide subsequent analysis
- Generate a final evidence-backed answer

The project is designed around an **MCP-based tool architecture** and a **LangGraph agentic workflow**.

---

## 🏗️ Architecture

                    ┌──────────────────┐
                    │      User        │
                    │ Natural Language │
                    │     Question     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Gemma 4 31B   │
                    │   LLM + Tool     │
                    │     Calling      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    LangGraph     │
                    │  Agent Workflow  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    MCP Client    │
                    │  Tool Manager    │
                    └────────┬─────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │   Analytics MCP Server      │
              │                             │
              │  • list_tables              │
              │  • describe_table           │
              │  • get_sample_rows          │
              │  • execute_sql              │
              └─────────────┬───────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │    PostgreSQL    │
                    │    Analytics DB  │
                    └──────────────────┘
