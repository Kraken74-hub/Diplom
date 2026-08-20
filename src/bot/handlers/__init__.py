from .start import router as start_router
from .track import router as track_router
from .list import router as list_router

routers = [track_router, start_router, list_router]