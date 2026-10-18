from datetime import datetime


class AuthError(Exception):
    status_code: int = 400

    @property
    def meta(self) -> dict | None:
        return None


class UsernameAlreadyExists(AuthError):
    status_code = 409

    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Username {self.username} already exists")


class UserNotFound(AuthError):
    status_code = 404

    def __init__(self, username: str) -> None:
        self.username = username
        super().__init__(f"Username {self.username} not found")


class UsernameNotExists(AuthError):
    status_code = 404


class WrongPassword(AuthError):
    status_code = 401


class UserDeleted(AuthError):
    status_code = 410

    def __init__(self, deleted_at: datetime) -> None:
        self.deleted_at = deleted_at
        super().__init__(f"User deleted account at {self.deleted_at}")

    @property
    def meta(self) -> dict:
        return {"deleted_at": self.deleted_at.isoformat()}


class UserBanned(AuthError):
    status_code = 403

    def __init__(
        self, username: str, banned_until: datetime | None, reason: str | None = None
    ) -> None:
        self.username = username
        self.banned_until = banned_until
        self.reason = reason
        super().__init__(
            f"Username {self.username} banned until {self.banned_until}, ban reason: {self.reason}"
        )

    @property
    def meta(self) -> dict:
        return {
            "banned_until": self.banned_until.isoformat()
            if self.banned_until
            else None,
            "reason": self.reason,
        }
