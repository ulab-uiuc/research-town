from functools import wraps

from beartype.typing import Any, Callable, Literal, TypeVar, cast

Role = Literal['reviewer', 'leader', 'participant', 'chair']
F = TypeVar('F', bound=Callable[..., Any])


def leader_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'leader':
            raise PermissionError(
                "This operation is allowed only for 'leader' role."
            )
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


def participant_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'participant' and self.role != 'leader':
            raise PermissionError(
                "This operation is allowed only for 'participant' role."
            )
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
