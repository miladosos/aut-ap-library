from .application import app

# import routes after app is created to avoid circular imports
from .routes import *
