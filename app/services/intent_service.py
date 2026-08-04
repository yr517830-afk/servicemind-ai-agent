from app.clients.llm_client import LLMClient, LLMError, llm_client
from app.prompts.loader import PromptBundle, load_intent_prompt
from app.schemas.intent import IntentExtraction, IntentType, RiskLevel


DEFAULT_INTENT_PROMPT_VERSION = "v2"


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
        except (LLMError, ValueError) as error:
            error_code = getattr(
                error,
                "code",
                "INVALID_RESPONSE",
            )
            return self.fallback(
                f"结构化提取失败（{error_code}），"
                "已使用安全兜底结果。"
            )


intent_service = IntentService()