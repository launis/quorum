from typing import Callable, Any

class HookRegistry:
    _registry = {}

    @classmethod
    def register(cls, name: str, func: Callable):
        cls._registry[name] = func

    @classmethod
    def get_hook(cls, hook_name: str) -> Callable:
        hook = cls._registry.get(hook_name)
        if not hook:
            raise ValueError(f"Hook '{hook_name}' not found in registry.")
        return hook
