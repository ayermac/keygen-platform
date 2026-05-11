from __future__ import annotations

"""Business exception hierarchy with stable error codes.

All business exceptions carry an error code and message.
The router layer maps them to the standard {code, message, data} envelope.
"""


class BizError(Exception):
    """Base business exception."""

    code: int = 0
    message: str = "unknown error"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.message
        super().__init__(self.message)


# ── C-end: Redeem errors (1001-1099) ──

class CodeNotFound(BizError):
    code = 1001
    message = "兑换码不存在"


class CodeAlreadyRedeemed(BizError):
    code = 1002
    message = "兑换码已兑换"


class CodeExpired(BizError):
    code = 1003
    message = "兑换码已过期"


class CodeDisabled(BizError):
    code = 1004
    message = "兑换码已禁用"


class ProductMismatch(BizError):
    code = 1005
    message = "兑换码不属于该产品"


# ── C-end: Consume errors (1101-1199) ──

class ConsumeFailed(BizError):
    code = 1101
    message = "消费失败"


class InsufficientCredits(BizError):
    code = 1102
    message = "额度不足"


class SystemBusy(BizError):
    code = 1103
    message = "系统繁忙，请稍后重试"


class CodeNotActivated(BizError):
    code = 1104
    message = "兑换码未兑换或已过期"


# ── B-end: Auth errors (1201-1299) ──

class LoginFailed(BizError):
    code = 1201
    message = "用户名或密码错误"


# ── B-end: Product errors (1301-1399) ──

class ProductCodeExists(BizError):
    code = 1301
    message = "产品标识码已存在"


class ProductNotFound(BizError):
    code = 1302
    message = "产品不存在"


class ProductHasCodes(BizError):
    code = 1303
    message = "该产品下存在兑换码，无法删除"


# ── B-end: Code management errors (1401-1499) ──

class InvalidGenerateCount(BizError):
    code = 1401
    message = "生成数量需在 1-10000 之间"


# ── B-end: API Key errors (1501-1599) ──

class InvalidApiKey(BizError):
    code = 1501
    message = "无效的 API Key"
