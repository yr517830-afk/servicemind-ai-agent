from app.clients.llm_client import (
    LLMClient,
    LLMError,
    LLMInvalidResponseError,
    LLMRateLimitError,
    LLMRefusalError,
    llm_client,
)
from app.prompts.loader import PromptBundle, load_intent_prompt
from app.schemas.failures import FailureCode
from app.schemas.intent import IntentExtraction, IntentType, RiskLevel
from app.services.fallback_service import fallback_service


DEFAULT_INTENT_PROMPT_VERSION = "v2"
MAX_INTENT_MESSAGE_LENGTH = 2000

class IntentService:
    """负责从客户消息中提取结构化意图。"""

    def __init__(
        self,
        client: LLMClient | None = None,
        *,
        prompt_version: str = DEFAULT_INTENT_PROMPT_VERSION,
    ) -> None:
        self.client = client or llm_client
        self.prompt_bundle = load_intent_prompt(prompt_version)

    @property
    def prompt_version(self) -> str:
        """返回当前使用的 Prompt 版本。"""
        return self.prompt_bundle.metadata.version

    @staticmethod
    def fallback(reason: str) -> IntentExtraction:
        """返回安全、可解析的兜底结果。"""
        return IntentExtraction(
            intent=IntentType.OTHER,
            order_number=None,
            risk=RiskLevel.UNKNOWN,
            confidence_reason=reason,
        )

    @classmethod
    def failure_fallback(
        cls,
        code: FailureCode,
    ) -> IntentExtraction:
        """把统一故障回复转换为安全的意图提取结果。"""

        reply = fallback_service.reply_for(code)

        return cls.fallback(
            f"{reply.message} 降级动作：{reply.action.value}。"
        )

    @staticmethod
    def build_model_input(
        message: str,
        prompt_bundle: PromptBundle,
    ) -> str:
        """把 few-shot 示例和当前客户消息组合为模型输入。"""
        rendered_examples = []

        for index, example in enumerate(
            prompt_bundle.examples,
            start=1,
        ):
            rendered_examples.append(
                "\n".join(
                    [
                        f"示例 {index} 输入：",
                        example.input,
                        f"示例 {index} 输出：",
                        example.output.model_dump_json(indent=2),
                    ]
                )
            )

        examples_text = "\n\n".join(rendered_examples)

        return "\n\n".join(
            [
                "以下是已标注的参考示例：",
                examples_text,
                "现在分析以下客户消息：",
                message,
            ]
        )

    def extract(self, message: str) -> IntentExtraction:
        """提取客户消息中的意图、订单号和风险。"""
        normalized_message = message.strip()

        if not normalized_message:
            return self.fallback("客户消息为空，无法判断意图。")

        if len(normalized_message) > MAX_INTENT_MESSAGE_LENGTH:
            return self.failure_fallback(
                FailureCode.INPUT_TOO_LONG
            )

        model_input = self.build_model_input(
            normalized_message,
            self.prompt_bundle,
        )

        try:
            return self.client.parse_structured(
                model_input,
                response_model=IntentExtraction,
                instructions=self.prompt_bundle.system_prompt,
            )
        except LLMInvalidResponseError:
            return self.failure_fallback(
                FailureCode.INVALID_RESPONSE
            )
        except LLMRefusalError:
            return self.failure_fallback(
                FailureCode.MODEL_REFUSAL
            )
        except LLMRateLimitError:
            return self.failure_fallback(
                FailureCode.RATE_LIMITED
            )
        except (LLMError, ValueError):
            return self.failure_fallback(
                FailureCode.INVALID_RESPONSE
            )


intent_service = IntentService()