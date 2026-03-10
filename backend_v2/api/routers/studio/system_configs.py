import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system-configs", tags=["Admin Studio V2 - System Configs"])

# Generic system configurations will be placed here in the future.
# Model Registry logic has been extracted to model_registry.py
