from collections.abc import Iterator
from typing import TypeVar
from pydantic import BaseModel
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    OpenAIError,
    RateLimitError,
)

from app.core.config import settings
StructuredOutputT = TypeVar(
    "StructuredOutputT",
    bound=BaseModel,
)

class LLMError(RuntimeError):
    """LLM 客户端统一异常。"""

    code = "LLM_ERROR"


class LLMNotConfiguredError(LLMError):
    """未配置 LLM API Key。"""

    code = "LLM_NOT_CONFIGURED"


class LLMTimeoutError(LLMError):
    """LLM 请求超时。"""

    code = "LLM_TIMEOUT"


class LLMRateLimitError(LLMError):
    """LLM 服务触发限流。"""

    code = "LLM_RATE_LIMITED"


class LLMAuthenticationError(LLMError):
    """LLM API 身份验证失败。"""

    code = "LLM_AUTHENTICATION_FAILED"


class LLMUnavailableError(LLMError):
    """LLM 服务暂时不可用。"""

    code = "LLM_UNAVAILABLE"


class LLMClient:
    """封装 OpenAI Responses API。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.api_key = (
            settings.openai_api_key if api_key is None else api_key
        ).strip()
        self.model = model or settings.openai_model
        self.base_url = base_url or settings.openai_base_url
        self.timeout = (
            settings.openai_timeout_seconds if timeout is None else timeout
        )
        self.max_retries = (
            settings.openai_max_retries
            if max_retries is None
            else max_retries
        )

        self._client: OpenAI | None = None

        if self.api_key:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                max_retries=self.max_retries,
            )

    @property
    def configured(self) -> bool:
        """是否已经配置 API Key。"""
        return self._client is not None

    def health(self) -> dict[str, object]:
        """返回本地配置状态，不产生真实 API 请求。"""
        return {
            "status": "ready" if self.configured else "not_configured",
            "configured": self.configured,
            "model": self.model,
            "timeout_seconds": self.timeout,
            "max_retries": self.max_retries,
        }

    def generate_text(
        self,
        prompt: str,
        *,
        instructions: str | None = None,
    ) -> str:
        """调用 Responses API 生成文本。"""
        if self._client is None:
            raise LLMNotConfiguredError("LLM API Key 尚未配置。")

        request: dict[str, object] = {
            "model": self.model,
            "input": prompt,
        }
        if instructions:
            request["instructions"] = instructions

        try:
            response = self._client.responses.create(**request)
        except APITimeoutError:
            raise LLMTimeoutError("LLM 请求超时，请稍后重试。") from None
        except RateLimitError:
            raise LLMRateLimitError("LLM 请求过于频繁，请稍后重试。") from None
        except AuthenticationError:
            raise LLMAuthenticationError("LLM API 身份验证失败。") from None
        except APIConnectionError:
            raise LLMUnavailableError("当前无法连接 LLM 服务。") from None
        except APIStatusError:
            raise LLMUnavailableError("LLM 服务返回异常状态。") from None
        except OpenAIError:
            raise LLMUnavailableError("LLM 服务调用失败。") from None

        output_text = response.output_text.strip()
        if not output_text:
            raise LLMUnavailableError("LLM 服务未返回有效文本。")

        return output_text

    def stream_text(
        self,
        prompt: str,
        *,
        instructions: str | None = None,
    ) -> Iterator[str]:
        """调用 Responses API，并逐段返回生成的文本。"""
        if self._client is None:
            raise LLMNotConfiguredError("LLM API Key 尚未配置。")

        request: dict[str, object] = {
            "model": self.model,
            "input": prompt,
            "stream": True,
        }
        if instructions:
            request["instructions"] = instructions

        emitted_text = False

        try:
            stream = self._client.responses.create(**request)

            for event in stream:
                event_type = getattr(event, "type", "")

                if event_type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    if delta:
                        emitted_text = True
                        yield delta

                elif event_type in {"error", "response.failed"}:
                    raise LLMUnavailableError(
                        "LLM 流式响应生成失败。"
                    )

        except LLMError:
            raise
        except APITimeoutError:
            raise LLMTimeoutError(
                "LLM 请求超时，请稍后重试。"
            ) from None
        except RateLimitError:
            raise LLMRateLimitError(
                "LLM 请求过于频繁，请稍后重试。"
            ) from None
        except AuthenticationError:
            raise LLMAuthenticationError(
                "LLM API 身份验证失败。"
            ) from None
        except APIConnectionError:
            raise LLMUnavailableError(
                "当前无法连接 LLM 服务。"
            ) from None
        except APIStatusError:
            raise LLMUnavailableError(
                "LLM 服务返回异常状态。"
            ) from None
        except OpenAIError:
            raise LLMUnavailableError(
                "LLM 服务调用失败。"
            ) from None

        if not emitted_text:
            raise LLMUnavailableError(
                "LLM 服务未返回有效的流式文本。"
            )

    def parse_structured(
        self,
        prompt: str,
        *,
        response_model: type[StructuredOutputT],
        instructions: str | None = None,
    ) -> StructuredOutputT:
        """调用 Responses API，并返回经过 Pydantic 校验的结构化结果。"""
        if self._client is None:
            raise LLMNotConfiguredError("LLM API Key 尚未配置。")

        request: dict[str, object] = {
            "model": self.model,
            "input": prompt,
            "text_format": response_model,
        }
        if instructions:
            request["instructions"] = instructions

        try:
            response = self._client.responses.parse(**request)
        except APITimeoutError:
            raise LLMTimeoutError(
                "LLM 请求超时，请稍后重试。"
            ) from None
        except RateLimitError:
            raise LLMRateLimitError(
                "LLM 请求过于频繁，请稍后重试。"
            ) from None
        except AuthenticationError:
            raise LLMAuthenticationError(
                "LLM API 身份验证失败。"
            ) from None
        except APIConnectionError:
            raise LLMUnavailableError(
                "当前无法连接 LLM 服务。"
            ) from None
        except APIStatusError:
            raise LLMUnavailableError(
                "LLM 服务返回异常状态。"
            ) from None
        except OpenAIError:
            raise LLMUnavailableError(
                "LLM 服务调用失败。"
            ) from None

        parsed = response.output_parsed
        if parsed is None:
            raise LLMUnavailableError(
                "LLM 服务未返回有效的结构化结果。"
            )

        return parsed

llm_client = LLMClient()