from functools import wraps
from typing import Any, Callable, Literal, TypeVar, cast

Role = Literal['reviewer', 'proj_leader', 'proj_participant', 'chair']
F = TypeVar('F', bound=Callable[..., Any])


def proj_leader_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'proj_leader':
            raise PermissionError(
                "This operation is allowed only for 'proj_leader' role."
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


def proj_participant_required(method: F) -> F:
    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if self.role is None:
            raise PermissionError('Roles are not assigned for research agent.')
        if self.role != 'proj_participant' and self.role != 'proj_leader':
            raise PermissionError(
                "This operation is allowed only for 'proj_participant' role."
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
