from .base import get_start_handler
from typing import Any
# импортируем модули, чтобы они зарегистрировали себя в реестре
from . import yookassa  # noqa
from . import stars     # noqa
from . import ton       # noqa
from . import intellectmoney
from . import tribute        # noqa 

__all__ = ["get_start_handler"]
