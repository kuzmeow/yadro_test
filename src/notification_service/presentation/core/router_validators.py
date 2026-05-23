import functools
from collections.abc import Callable
from typing import Any

from flask import request
from pydantic import BaseModel


def validate_body(schema: type[BaseModel], kwarg_name: str = "body") -> Callable:
    """Валидирует JSON-тело запроса и инжектирует Pydantic-модель в хендлер."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            raw_data = request.get_json(silent=True) or {}
            kwargs[kwarg_name] = schema.model_validate(raw_data)
            return await func(*args, **kwargs)

        return async_wrapper

    return decorator


def validate_query(schema: type[BaseModel], kwarg_name: str = "query") -> Callable:
    """Валидирует query-параметры и инжектирует Pydantic-модель в хендлер."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            raw_data = dict(request.args)
            kwargs[kwarg_name] = schema.model_validate(raw_data)
            return await func(*args, **kwargs)

        return async_wrapper

    return decorator
