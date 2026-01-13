"""Rate Limiting Configuration Module.

Stores the SlowAPI Limiter instance centrally to avoid circular imports
between main.py and router modules.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize Limiter with Remote Address as key
limiter = Limiter(key_func=get_remote_address)
