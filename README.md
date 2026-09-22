# DataPilot — MCP-Powered AI Data Analyst

> An agentic data-analysis platform using Gemma 4, LangGraph, MCP, and PostgreSQL to autonomously investigate business questions through schema discovery, multi-step SQL analysis, self-correcting queries, and evidence-backed reasoning.

---

## Overview

DataPilot allows users to ask analytical questions about a PostgreSQL database using natural language.

Instead of manually writing SQL, the agent can:

- Discover database tables
- Inspect table schemas
- Retrieve sample data
- Generate and execute SQL
- Recover from SQL errors
- Perform multi-step investigations
- Track investigation evidence
- Generate evidence-backed analytical conclusions

The system uses **MCP (Model Context Protocol)** to separate the AI agent from database operations and **LangGraph** to orchestrate the investigation workflow.

---

## Architecture

```text
                    ┌──────────────────┐
                    │       User       │
                    │ Natural Language │
                    │    Question      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Gemma 4 31B    │
                    │   Tool Calling   │
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
                    │   Tool Manager   │
                    └────────┬─────────┘
                             │
                             ▼
              ┌─────────────────────────────┐
              │     Analytics MCP Server    │
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
```

---

## Key Features

### 🔍 Autonomous Investigation

The agent can break down complex business questions into multiple analytical steps.

For example:

```text
"Why was October 2025 revenue higher than September 2025?"
```

The agent can:

```text
Discover tables
      ↓
Inspect schemas
      ↓
Calculate monthly revenue
      ↓
Compare months
      ↓
Investigate relevant dimensions
      ↓
Execute additional SQL
      ↓
Collect evidence
      ↓
Generate conclusion
```

---

### 🔌 MCP-Based Database Tools

The analytics MCP server exposes four tools:

| Tool | Description |
|------|-------------|
| `list_tables` | Lists available database tables |
| `describe_table` | Returns columns, types, nullability and primary keys |
| `get_sample_rows` | Retrieves sample records from a table |
| `execute_sql` | Executes read-only analytical SQL |

This keeps database access separate from the agent's reasoning layer.

---

### 🧠 Self-Correcting Text-to-SQL

DataPilot can recover from SQL generation errors.

```text
Generate SQL
     ↓
Execute SQL
     ↓
Database Error
     ↓
Analyze Error
     ↓
Correct SQL
     ↓
Retry
     ↓
Successful Result
```

For example, if the generated query references an incorrect column:

```sql
SELECT SUM(quantity * price)
FROM order_items;
```

and PostgreSQL reports that `price` does not exist, the agent can inspect the error and correct the query to use the appropriate column:

```sql
SELECT SUM(quantity * unit_price)
FROM order_items;
```

SQL retries are bounded to prevent uncontrolled loops.

---

### 🔐 Read-Only SQL Safety

The `execute_sql` tool validates queries before execution.

Allowed statement types:

```text
SELECT
WITH
EXPLAIN
```

Write and schema-modifying operations such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
```

are rejected.

Query result sizes are also limited to prevent excessive result retrieval.

> The current validation layer is designed for the project environment. A production implementation should additionally use a dedicated read-only PostgreSQL role, database-level permissions, read-only transactions, query timeouts, and stronger SQL parsing.

---

### 📋 Evidence & Provenance Tracking

DataPilot maintains structured evidence throughout the investigation.

For each SQL execution, the agent can track:

- SQL query
- Execution status
- Returned columns
- Result rows
- Database errors
- Investigation state

This allows the final answer to be grounded in the evidence collected during the investigation.

```text
Investigation
│
├── SQL Query 1
│   └── Monthly Revenue
│
├── SQL Query 2
│   └── Revenue by Category
│
└── Final Conclusion
    └── Based on collected evidence
```

---

## Agent Workflow

The LangGraph agent follows a tool-calling loop:

```text
User Question
      │
      ▼
LLM analyzes question
      │
      ▼
Need more information?
      │
   ┌──┴──┐
   │     │
  Yes    No
   │     │
   ▼     ▼
Select   Final
Tool     Answer
   │
   ▼
Execute Tool
   │
   ▼
Add Result to State
   │
   ▼
Analyze Result
   │
   └──────────────► Continue Investigation
```

The agent state contains:

```python
messages
sql_retries
investigation
```

This allows the workflow to preserve context, control SQL retries, and maintain investigation evidence.

---

## Example Investigation

### Question

```text
Why was October 2025 revenue higher than September 2025?
Investigate the database and explain the main factors.
```

The agent can first calculate monthly revenue:

```text
September 2025
Revenue: $650,000
Orders: 8
Units: 24

October 2025
Revenue: $696,000
Orders: 8
Units: 26
```

It can then investigate revenue by category:

```text
Category        September       October
----------------------------------------
Accessories       $42,000        $42,000
Electronics      $512,000       $462,000
Furniture         $96,000       $192,000
```

The evidence shows that the increase in Furniture revenue was the primary contributor to the overall increase, while the decline in Electronics revenue partially offset it.

---

## Project Structure

```text
datapilot/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py
│   ├── run.py
│   ├── test_graph.py
│   └── tools.py
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── llm.py
│
├── data/
│   └── init.sql
│
├── mcp_client/
│   ├── __init__.py
│   ├── client.py
│   └── manager.py
│
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── db.py
│   ├── validators.py
│   └── tools/
│       ├── __init__.py
│       ├── schema.py
│       └── sql.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemma 4 31B |
| Agent Orchestration | LangGraph |
| LLM Framework | LangChain |
| Tool Protocol | MCP |
| Database | PostgreSQL |
| Database Layer | SQLAlchemy |
| Language | Python |
| Configuration | python-dotenv |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Arinahalwasia/datapilot.git
cd datapilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

#### macOS / Linux

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -e .
```

---

### 4. Configure PostgreSQL

Create a PostgreSQL database named:

```text
datapilot
```

Initialize the database:

```bash
psql -d datapilot -f data/init.sql
```

---

### 5. Configure environment variables

Create a `.env` file:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=datapilot
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
```

Add the required LLM configuration for your Gemma deployment.

> `.env` is intentionally excluded from Git.

---

## Running DataPilot

Run the MCP client:

```bash
python -m mcp_client.client
```

Run the agent:

```bash
python -m agent.run
```

Example questions:

```text
What is the total revenue generated by all orders?
```

```text
What are the monthly revenues, and which month generated the highest revenue?
```

```text
Why was October 2025 revenue higher than September 2025?
Investigate the database and explain the main factors.
```

---

## Security Considerations

The current implementation includes basic SQL validation to prevent write operations through the MCP SQL tool.

For production use, additional controls should include:

- Dedicated PostgreSQL read-only user
- Database-level permissions
- Read-only transactions
- SQL parser-based validation
- Query timeout enforcement
- Resource limits
- Authentication and authorization
- Audit logging

The LLM-generated SQL should always be treated as untrusted input.

---

## Design Principles

### Tool Separation

The agent handles reasoning and decision-making while database access is isolated behind MCP tools.

### Controlled Autonomy

The agent can perform multi-step investigations while operating within bounded execution and retry limits.

### Evidence-Based Reasoning

Final conclusions are generated from information retrieved from the database rather than assumptions or fabricated values.

---

## Project Status

### V1 — Core Agentic Data Analyst

Implemented:

- PostgreSQL integration
- MCP server
- MCP client
- MCP tool manager
- Gemma 4 integration
- LangGraph orchestration
- Tool calling
- Text-to-SQL
- Self-correcting SQL
- Autonomous investigation
- Evidence/provenance tracking
- Bounded SQL retries
- CLI investigation interface

### Future Improvements

- Structured findings and hypothesis tracking
- Automated data visualizations
- Langfuse / OpenTelemetry observability
- Automated evaluation datasets
- Agent quality metrics
- Regression testing
- Web-based analytics dashboard
- Advanced SQL validation

---

## Why DataPilot?

DataPilot demonstrates how an LLM can move beyond simple question-answering and operate as an agentic data analyst:

```text
Natural Language
      ↓
LLM Reasoning
      ↓
Tool Selection
      ↓
Database Exploration
      ↓
SQL Generation
      ↓
SQL Error Recovery
      ↓
Multi-Step Investigation
      ↓
Evidence Collection
      ↓
Analytical Conclusion
```

---

## Author

**Arina Aggarwal**

AI / LLM Engineer

Interests:

- Agentic AI
- LLM Evaluation
- Model Context Protocol (MCP)
- LLM Applications
- AI Observability
- AI Reliability
- Evaluation & Testing

---

⭐ If you find the project useful, consider starring the repository.
