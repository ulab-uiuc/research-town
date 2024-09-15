from functools import wraps

from beartype.typing import Any, Callable, TypeVar, cast

F = TypeVar('F', bound=Callable[..., Any])


def leader_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'leader':
            raise PermissionError("This operation is allowed only for 'leader' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)


def reviewer_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'reviewer':
            raise PermissionError("This operation is allowed only for 'reviewer' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)


def member_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'member' and self.role != 'leader':
            raise PermissionError("This operation is allowed only for 'member' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)


def chair_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'chair':
            raise PermissionError("This operation is allowed only for 'chair' role.")
        return method(self, *args, **kwargs)

    return cast(F, wrapper)
