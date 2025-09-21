"""Controller factory for creating and managing controller instances."""

from src.app.controllers.hotel_controller import HotelController
from src.app.services.factory import ServiceFactory
from src.core.config import SearchAPISettings


class ControllerFactory:
    """
    Factory class for creating and managing controller layer instances.

    This factory follows the singleton pattern to ensure consistent
    configuration and resource management across the application.
    It coordinates with ServiceFactory to provide properly configured controllers.
    """

    _hotel_controller: HotelController | None = None

    @classmethod
    def get_hotel_controller(cls, settings: SearchAPISettings | None = None) -> HotelController:
        """
        Get configured hotel controller instance.

        Args:
            settings: Optional SearchAPI settings to pass to service layer

        Returns:
            HotelController: Configured hotel controller instance

        """
        if cls._hotel_controller is None:
            # Ensure service layer is initialized with consistent settings
            ServiceFactory.get_hotel_service(settings)
            cls._hotel_controller = HotelController()

        return cls._hotel_controller

    @classmethod
    def reset(cls) -> None:
        """
        Reset factory state for testing purposes.

        This method is primarily intended for use in tests
        to ensure clean state between test runs.
        """
        cls._hotel_controller = None
