import functools
import inspect
import itertools
from collections.abc import Generator, Iterator
from copy import deepcopy
from pickle import PickleError
from typing import Any, Protocol, TypeVar
from unittest.mock import NonCallableMock, _Call

import pytest
from pytest_mock import MockerFixture, MockType


class SpyObj(NonCallableMock):
    spy_return: Any
    spy_return_iter: Iterator[Any]
    spy_return_list: list[Any]
    spy_exception = Exception


type SpyType = MockType | SpyObj


class SpyFunc(Protocol):
    def __call__(self, obj: object, name: str, duplicate_iterators: bool = False) -> SpyType:
        """
        Create a spy of method. It will run method normally, but it is now
        possible to use `mock` call features with it, like call count.

        :param obj: An object.
        :param name: A method in object.
        :param duplicate_iterators: Whether to keep a copy of the returned iterator in `spy_return_iter`.
        :return: Spy object.
        """


A = TypeVar("A", bound=Any)


def safe_deepcopy[A](val: A) -> A:
    try:
        val_copy = deepcopy(val)
    except (TypeError, PickleError):
        val_copy = val

    return val_copy


class MyMockerFixture(MockerFixture):
    def spy(self, obj: object, name: str, duplicate_iterators: bool = False) -> MockType:
        """
        Create a spy of method. It will run method normally, but it is now
        possible to use `mock` call features with it, like call count.

        :param obj: An object.
        :param name: A method in object.
        :param duplicate_iterators: Whether to keep a copy of the returned iterator in `spy_return_iter`.
        :return: Spy object.
        """
        method = getattr(obj, name)

        def wrapper(*args, **kwargs):
            spy_obj.spy_return = None
            spy_obj.spy_exception = None
            _call = _Call((safe_deepcopy(args), safe_deepcopy(kwargs)), two=True)
            try:
                r = method(*args, **kwargs)
            except BaseException as e:
                spy_obj.spy_exception = e
                raise
            else:
                if duplicate_iterators and isinstance(r, Iterator):
                    r, duplicated_iterator = itertools.tee(r, 2)
                    spy_obj.spy_return_iter = duplicated_iterator
                else:
                    spy_obj.spy_return_iter = None

                r_copy = safe_deepcopy(r)
                spy_obj.spy_return = r_copy
                spy_obj.spy_return_list.append(r_copy)

                spy_obj.call_args = _call
                spy_obj.call_args_list.append(_call)
            return r

        async def async_wrapper(*args, **kwargs):
            spy_obj.spy_return = None
            spy_obj.spy_exception = None
            _call = _Call((safe_deepcopy(args), safe_deepcopy(kwargs)), two=True)
            try:
                r = await method(*args, **kwargs)
            except BaseException as e:
                spy_obj.spy_exception = e
                raise
            else:
                r_copy = safe_deepcopy(r)
                spy_obj.spy_return = r_copy
                spy_obj.spy_return_list.append(r_copy)

                spy_obj.call_args = _call
                spy_obj.call_args_list.append(_call)
            return r

        if inspect.iscoroutinefunction(method):
            wrapped = functools.update_wrapper(async_wrapper, method)
        else:
            wrapped = functools.update_wrapper(wrapper, method)

        autospec = inspect.ismethod(method) or inspect.isfunction(method)

        spy_obj = self.patch.object(obj, name, side_effect=wrapped, autospec=autospec)
        spy_obj.spy_return = None
        spy_obj.spy_return_iter = None
        spy_obj.spy_return_list = []
        spy_obj.spy_exception = None
        return spy_obj


@pytest.fixture
def my_mocker(pytestconfig) -> Generator[MyMockerFixture]:
    result = MyMockerFixture(pytestconfig)
    yield result
    result.stopall()


@pytest.fixture()
def spy(my_mocker: "MyMockerFixture") -> SpyFunc:
    return my_mocker.spy
