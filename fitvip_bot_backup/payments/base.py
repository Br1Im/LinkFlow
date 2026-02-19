from typing import Optional
from typing import Callable, Awaitable, Dict, Any

# Реестр обработчиков запуска оплаты: code -> coroutine
_PAYMENT_START_HANDLERS: Dict[str, Callable[..., Awaitable[None]]] = {}


def register_payment(code: str):
    """Декоратор для регистрации обработчика способа оплаты.

    Использование:
        @register_payment("yookassa")
        async def start_payment(...):
            ...
    """
    def decorator(func: Callable[..., Awaitable[None]]):
        _PAYMENT_START_HANDLERS[code] = func
        return func
    return decorator


def get_start_handler(code: str) -> Optional[Callable[..., Awaitable[None]]]:
    return _PAYMENT_START_HANDLERS.get(code)
