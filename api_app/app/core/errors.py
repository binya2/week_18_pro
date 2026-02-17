class AppError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CacheError(AppError):
    pass


class DatabaseError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass
