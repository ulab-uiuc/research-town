from functools import wraps
from ..data import Role

from beartype.typing import Any, Callable, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])


def leader_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role == Role.NONE:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != Role.LEADER:
            raise PermissionError("This operation is allowed only for 'leader' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)


def reviewer_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role == Role.NONE:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != Role.REVIEWER:
            raise PermissionError("This operation is allowed only for 'reviewer' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)


def member_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role == Role.NONE:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != Role.MEMBER and self.role != Role.LEADER:
            raise PermissionError("This operation is allowed only for 'member' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)


def chair_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role == Role.NONE:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != Role.CHAIR:
            raise PermissionError("This operation is allowed only for 'chair' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)
