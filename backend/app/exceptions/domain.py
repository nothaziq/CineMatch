"""
Domain-level exceptions. These carry no HTTP knowledge — the middleware layer
maps them to status codes and a consistent JSON error shape. This keeps
services/repositories free of any FastAPI import.
"""


class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    status_code: int = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class MovieNotFoundError(DomainError):
    code = "MOVIE_NOT_FOUND"
    status_code = 404

    def __init__(self, movie_id: int) -> None:
        super().__init__(f"Movie with id {movie_id} was not found.")


class ArtifactsNotLoadedError(DomainError):
    code = "ARTIFACTS_NOT_LOADED"
    status_code = 503

    def __init__(self) -> None:
        super().__init__(
            "Movie data artifacts are not loaded yet. The server may still be starting up."
        )


class InvalidQueryError(DomainError):
    code = "INVALID_QUERY"
    status_code = 422

    def __init__(self, message: str) -> None:
        super().__init__(message)
