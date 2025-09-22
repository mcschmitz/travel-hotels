from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from src.api.hotels import router as hotels_router
from src.app.services.factory import ServiceFactory
from src.core.config import ServerSettings

server_settings = ServerSettings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events for proper resource management.
    """
    logger.info("Starting up application")

    try:
        yield
    finally:
        logger.info("Shutting down application")
        try:
            await ServiceFactory.cleanup()
            logger.info("Factory cleanup completed successfully")
        except Exception as e:
            logger.error(f"Error during factory cleanup: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=server_settings.app_name,
        version=server_settings.version,
        debug=server_settings.debug,
        lifespan=lifespan,
    )
    app.include_router(hotels_router)
    add_health_check(app)
    add_root_route(app)
    return app


def add_health_check(app: FastAPI) -> None:
    """Add health check endpoint."""

    @app.get("/health", status_code=200)
    async def health_check() -> dict[str, str]:
        """
        Health check endpoint.

        Returns a simple status message to indicate that the service is
        up and running.

        Returns:
            dict[str, str]: Health status message

        Example:
            {"status": "healthy"}

        """
        return {"status": "healthy"}


def add_root_route(app: FastAPI) -> None:
    """Add root endpoint."""

    @app.get("/", status_code=200)
    async def root() -> dict[str, Any]:
        """
        Root endpoint with basic application information.

        Returns:
            dict[str, Any]: Application metadata including message, version, and status

        Example:
            {
                "message": "Hotel API is running",
                "version": "0.1.0",
                "status": "healthy"
            }

        """
        return {
            "message": "Hotel API is running",
            "version": server_settings.version,
            "status": "healthy",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:create_app", host="localhost", port=8000, reload=True)
