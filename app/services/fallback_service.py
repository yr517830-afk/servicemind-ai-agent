from app.schemas.failures import (
    FailureCode,
    FailureReply,
    FallbackAction,
)


class FallbackService:
    """将模型故障转换为用户可以理解的降级回复。"""

    @staticmethod
    def reply_for(code: FailureCode) -> FailureReply:
        """根据故障类型生成对应的安全回复。"""

        if code is FailureCode.INVALID_RESPONSE:
            return FailureReply(
                code=code,
                message=(
                    "智能服务暂时无法准确理解您的问题，"
                    "系统将使用基础规则继续处理。"
                ),
                action=FallbackAction.USE_RULES,
                retryable=False,
            )

        if code is FailureCode.MODEL_REFUSAL:
            return FailureReply(
                code=code,
                message=(
                    "智能服务无法处理当前请求，"
                    "已建议转接人工客服进一步确认。"
                ),
                action=FallbackAction.HUMAN_HANDOFF,
                retryable=False,
            )

        if code is FailureCode.RATE_LIMITED:
            return FailureReply(
                code=code,
                message=(
                    "当前咨询人数较多，智能服务暂时繁忙，"
                    "请稍后重新尝试。"
                ),
                action=FallbackAction.RETRY_LATER,
                retryable=True,
            )

        if code is FailureCode.INPUT_TOO_LONG:
            return FailureReply(
                code=code,
                message=(
                    "您发送的内容过长，请保留订单号和主要问题，"
                    "缩短内容后重新发送。"
                ),
                action=FallbackAction.SHORTEN_INPUT,
                retryable=True,
            )

        raise ValueError(f"不支持的故障类型：{code}")


fallback_service = FallbackService()