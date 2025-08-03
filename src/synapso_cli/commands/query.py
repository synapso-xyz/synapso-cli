from synapso_core.query_manager import QueryManager


def cmd_query(query: str):
    """Execute a query against a cortex."""
    query_manager = QueryManager()
    result = query_manager.query(query)
    return result
