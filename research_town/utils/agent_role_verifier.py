from functools import wraps
from typing import Literal

Role = Literal['reviewer', 'leader', 'collaborator', 'chair']


def leader_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.role != 'leader':
            raise PermissionError("This operation is allowed only for 'leader' role.")
        return method(self, *args, **kwargs)

    return wrapper


def reviewer_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.role != 'reviewer':
            raise PermissionError("This operation is allowed only for 'reviewer' role.")
        return method(self, *args, **kwargs)

    return wrapper


def collaborator_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.role != 'collaborator':
            raise PermissionError(
                "This operation is allowed only for 'collaborator' role."
            )
        return method(self, *args, **kwargs)

    return wrapper


def collaborator_or_leader_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.role != 'collaborator' or self.role != 'leader':
            raise PermissionError(
                "This operation is allowed only for 'collaborator' role."
            )
        return method(self, *args, **kwargs)

    return wrapper


def chair_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.role != 'chair':
            raise PermissionError("This operation is allowed only for 'chair' role.")
        return method(self, *args, **kwargs)

    return wrapper
