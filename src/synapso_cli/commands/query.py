from synapso_core.config_manager import get_config
from synapso_core.query_manager.query_config import QueryConfig
from synapso_core.query_manager.query_manager import QueryManager


def cmd_query(query: str):
    """Execute a query against a cortex."""
    config = get_config()
    vectorizer_type = config.vectorizer.vectorizer_type
    reranker_type = config.reranker.reranker_type
    summarizer_type = config.summarizer.summarizer_type
    query_config = QueryConfig(
        vectorizer_type=vectorizer_type,
        reranker_type=reranker_type,
        summarizer_type=summarizer_type,
    )
    query_manager = QueryManager(query_config)
    result = query_manager.query(query)
    return result
