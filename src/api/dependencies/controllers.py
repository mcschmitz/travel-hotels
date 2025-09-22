from src.app.controllers.hotel_controller import HotelController


def get_hotel_controller() -> HotelController:
    """
    Create HotelController instance.

    This function provides a simple way to get a controller instance
    for dependency injection in FastAPI routes.

    Returns:
        HotelController: New controller instance

    """
    return HotelController()
