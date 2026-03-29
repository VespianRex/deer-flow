"""Custom NVIDIA NIM provider with exponential backoff for rate limiting.

Handles 429 Too Many Requests with proper retry logic:
  - Exponential backoff: 2000ms * 2^(attempt-1) + 20% jitter
  - Respects Retry-After header when present
  - Configurable max retry attempts

Config example:
    - name: stepfun
      use: deerflow.models.nvidia_nim_provider:NvidiaNimChatModel
      model: stepfun-ai/step-3.5-flash
      max_tokens: 4096
      retry_max_attempts: 5
"""

import logging
import time
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_BACKOFF_MS = 2000
JITTER_RATIO = 0.2


class NvidiaNimChatModel(ChatOpenAI):
    """ChatOpenAI subclass with NVIDIA NIM-specific retry and backoff logic.

    Handles rate limiting (429) and server errors (500, 502, 503, 529) with
    exponential backoff and Retry-After header support.
    """

    retry_max_attempts: int = MAX_RETRIES

    def _validate_retry_config(self) -> None:
        if self.retry_max_attempts < 1:
            raise ValueError("retry_max_attempts must be >= 1")

    def model_post_init(self, __context: Any) -> None:
        self._validate_retry_config()
        super().model_post_init(__context)

    def _generate(self, messages: list[BaseMessage], stop: list[str] | None = None, **kwargs: Any) -> Any:
        last_error = None
        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                return super()._generate(messages, stop=stop, **kwargs)
            except Exception as e:
                last_error = e
                if self._is_rate_limit_error(e):
                    if attempt >= self.retry_max_attempts:
                        break
                    wait_ms = self._calc_backoff_ms(attempt, e)
                    logger.warning(f"NVIDIA NIM rate limited, retrying attempt {attempt}/{self.retry_max_attempts} after {wait_ms}ms")
                    time.sleep(wait_ms / 1000)
                elif self._is_server_error(e):
                    if attempt >= self.retry_max_attempts:
                        break
                    wait_ms = self._calc_backoff_ms(attempt, e)
                    logger.warning(f"NVIDIA NIM server error, retrying attempt {attempt}/{self.retry_max_attempts} after {wait_ms}ms")
                    time.sleep(wait_ms / 1000)
                else:
                    raise
        raise last_error

    async def _agenerate(self, messages: list[BaseMessage], stop: list[str] | None = None, **kwargs: Any) -> Any:
        import asyncio

        last_error = None
        for attempt in range(1, self.retry_max_attempts + 1):
            try:
                return await super()._agenerate(messages, stop=stop, **kwargs)
            except Exception as e:
                last_error = e
                if self._is_rate_limit_error(e):
                    if attempt >= self.retry_max_attempts:
                        break
                    wait_ms = self._calc_backoff_ms(attempt, e)
                    logger.warning(f"NVIDIA NIM rate limited, retrying attempt {attempt}/{self.retry_max_attempts} after {wait_ms}ms")
                    await asyncio.sleep(wait_ms / 1000)
                elif self._is_server_error(e):
                    if attempt >= self.retry_max_attempts:
                        break
                    wait_ms = self._calc_backoff_ms(attempt, e)
                    logger.warning(f"NVIDIA NIM server error, retrying attempt {attempt}/{self.retry_max_attempts} after {wait_ms}ms")
                    await asyncio.sleep(wait_ms / 1000)
                else:
                    raise
        raise last_error

    def _is_rate_limit_error(self, error: Exception) -> bool:
        if hasattr(error, "status_code"):
            return error.status_code == 429
        if hasattr(error, "response") and hasattr(error.response, "status_code"):
            return error.response.status_code == 429
        error_str = str(error).lower()
        return "429" in error_str or "rate limit" in error_str or "too many requests" in error_str

    def _is_server_error(self, error: Exception) -> bool:
        if hasattr(error, "status_code"):
            return error.status_code in (500, 502, 503, 529)
        if hasattr(error, "response") and hasattr(error.response, "status_code"):
            return error.response.status_code in (500, 502, 503, 529)
        error_str = str(error).lower()
        return any(code in error_str for code in ["500", "502", "503", "529", "internal server error", "service unavailable"])

    def _calc_backoff_ms(self, attempt: int, error: Exception) -> int:
        backoff_ms = BASE_BACKOFF_MS * (1 << (attempt - 1))
        jitter_ms = int(backoff_ms * JITTER_RATIO)
        total_ms = backoff_ms + jitter_ms

        retry_after = self._get_retry_after_header(error)
        if retry_after is not None:
            total_ms = retry_after * 1000

        return total_ms

    def _get_retry_after_header(self, error: Exception) -> int | None:
        headers = None
        if hasattr(error, "response") and error.response is not None:
            headers = getattr(error.response, "headers", None)
        elif hasattr(error, "response_headers"):
            headers = error.response_headers

        if headers:
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
            if retry_after:
                try:
                    return int(retry_after)
                except (ValueError, TypeError):
                    pass
        return None
