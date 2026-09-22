import logging
from typing import Dict, Optional
import httpx
from langchain_openai import ChatOpenAI
from core import config
from pydantic import SecretStr

# Configure root logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Cache for model instances
_global_chat_model_instances: Dict[str, ChatOpenAI] = {}


def get_llm(
    temperature: Optional[float] = None,
    streaming: Optional[bool] = None,
    model_name: Optional[str] = None,
    top_p: Optional[float] = None,
    max_tokens: Optional[int] = None,
    parallel_tool_calls: Optional[bool] = None
    ) -> ChatOpenAI:
    """
    Initializes or returns a cached ChatOpenAI instance with overrideable params.
    If model_name is provided, looks up the corresponding API URL and key from AVAILABLE_MODELS.
    
    Args:
        parallel_tool_calls: If False, disables parallel tool calls (prevents LLM from 
                            generating multiple tool calls in a single response).
                            Set to False for sequential conversation flows.
    """
    default_temp = 0.6
    default_stream = True
    default_model = config.AI_MODEL_NAME
    default_top_p = 1.0
    default_max_tokens = 4096  # Default reasonable limit

    final_temp = temperature if temperature is not None else default_temp
    final_streaming = streaming if streaming is not None else default_stream
    final_model = model_name if model_name is not None else default_model
    final_top_p = top_p if top_p is not None else default_top_p
    final_max_tokens = max_tokens if max_tokens is not None else default_max_tokens
    final_parallel_tool_calls = parallel_tool_calls  # None means use default (allow parallel)
    
    # Look up model configuration from AVAILABLE_MODELS
    selected_model = next(
        (m for m in config.AVAILABLE_MODELS if m["name"] == final_model),
        config.DEFAULT_MODEL
    )
    
    # Use backend_model if specified, otherwise use name
    # This allows friendly names like "gpt_oss_new" while sending the actual model name "openai/gpt-oss-120b" to the API
    final_model_name = selected_model.get("backend_model") or selected_model["name"]
    final_api_url = selected_model["api_url"]
    final_api_key = selected_model["api_key"]

    # Include parallel_tool_calls in cache key if specified
    ptc_key = f"_ptc{final_parallel_tool_calls}" if final_parallel_tool_calls is not None else ""
    cache_key = f"{final_model_name}_{final_temp}_{final_streaming}_{final_top_p}_{final_max_tokens}{ptc_key}"

    if cache_key not in _global_chat_model_instances:
        logger.info(
            "LLM: Creating new ChatOpenAI instance for key: %s (API: %s)",
            cache_key, final_api_url
        )
        if not final_api_url:
            logger.critical("API URL is not set for model '%s'. Cannot initialize ChatOpenAI.", final_model_name)
            raise ValueError(f"API URL is required to initialize ChatOpenAI for model {final_model_name}.")

        api_key = final_api_key
        api_headers = None
        if api_key and api_key.lower().startswith("bearer "):
            # strip "Bearer " prefix if present
            token = api_key[7:].strip()
            logger.info(f"Stripped 'Bearer ' prefix from API key for headers. {token}")
            api_headers = {"Authorization": f"Bearer {token}"}
        else:
            api_headers = {"Authorization": f"Bearer {api_key}"} if api_key else None

        # High connection limits for parallel/stress testing (up to 500 concurrent)
        http_client = httpx.Client(
            verify=False, 
            headers=api_headers,
            limits=httpx.Limits(
                max_connections=500,
                max_keepalive_connections=100,
                keepalive_expiry=30
            ),
            timeout=httpx.Timeout(120.0, connect=30.0)  # 120s read, 30s connect
        )

        # Build model_kwargs for additional OpenAI API parameters
        model_kwargs = {}
        if final_parallel_tool_calls is not None:
            model_kwargs["parallel_tool_calls"] = final_parallel_tool_calls
            logger.info("LLM: parallel_tool_calls set to %s", final_parallel_tool_calls)

        # 🔎 TOKLOG: attach centralized token-usage callback so every LLM call
        # gets its prompt size logged (helps surface 32k context-limit issues).
        # See utils/token_logger.py.
        try:
            from utils.token_logger import TOKEN_USAGE_HANDLER, CONTEXT_LIMIT
            _token_callbacks = [TOKEN_USAGE_HANDLER]
            logger.info(
                "LLM: TokenUsageCallbackHandler attached for model '%s' (context_limit=%d, max_tokens=%d)",
                final_model_name, CONTEXT_LIMIT, final_max_tokens,
            )
        except Exception as _e:  # pragma: no cover
            logger.debug("LLM: token_logger unavailable (%s) — skipping callback", _e)
            _token_callbacks = []

        try:
            # Build ChatOpenAI kwargs - only include model_kwargs if non-empty
            chat_kwargs = dict(
                model=final_model_name,
                openai_api_base=final_api_url,
                openai_api_key=final_api_key,
                temperature=final_temp,
                top_p=final_top_p,
                max_tokens=final_max_tokens,
                max_retries=config.MAX_API_RETRIES,
                streaming=final_streaming,
                http_client=http_client,
                default_headers=api_headers,
                callbacks=_token_callbacks or None,
            )
            if model_kwargs:  # Only add if non-empty
                chat_kwargs["model_kwargs"] = model_kwargs

            llm_instance = ChatOpenAI(**chat_kwargs)
            _global_chat_model_instances[cache_key] = llm_instance
            logger.info("ChatOpenAI instance for key '%s' created and cached successfully.", cache_key)
        except Exception as e:
            logger.exception(
                "!!! FATAL ERROR initializing ChatOpenAI instance for key %s: %s",
                cache_key, e
            )
            raise RuntimeError(f"Could not initialize AI chat model for {cache_key}") from e
    else:
        logger.debug("LLM: Returning cached ChatOpenAI instance for key: %s", cache_key)

    return _global_chat_model_instances[cache_key]