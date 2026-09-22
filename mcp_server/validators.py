import re


FORBIDDEN_SQL = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
}


class UnsafeQueryError(ValueError):
    """Raised when SQL contains a forbidden operation."""


def validate_read_only_sql(query: str) -> str:
    """
    Validate that the SQL query is read-only.

    Allowed:
        SELECT
        WITH ... SELECT
        EXPLAIN

    Blocked:
        INSERT
        UPDATE
        DELETE
        DROP
        ALTER
        TRUNCATE
        CREATE
        GRANT
        REVOKE
    """

    if not query or not query.strip():
        raise UnsafeQueryError("SQL query cannot be empty.")

    normalized = query.strip()

    # Remove SQL comments
    normalized = re.sub(r"--.*?$", "", normalized, flags=re.MULTILINE)
    normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL)

    normalized = normalized.strip()

    if not normalized:
        raise UnsafeQueryError("SQL query cannot contain only comments.")

    # Remove trailing semicolon
    normalized = normalized.rstrip(";").strip()

    # Reject multiple statements.
    if ";" in normalized:
        raise UnsafeQueryError(
            "Multiple SQL statements are not allowed."
        )

    first_keyword = normalized.split(None, 1)[0].upper()

    if first_keyword not in {"SELECT", "WITH", "EXPLAIN"}:
        raise UnsafeQueryError(
            f"Only read-only SQL is allowed. "
            f"Found statement type: {first_keyword}"
        )

    upper_query = normalized.upper()

    for forbidden in FORBIDDEN_SQL:
        pattern = rf"\b{forbidden}\b"

        if re.search(pattern, upper_query):
            raise UnsafeQueryError(
                f"Forbidden SQL operation detected: {forbidden}"
            )

    return normalized