from backend_v2.core.hook_registry import HookDependencies, HookRegistry, HookResult, HookState


def test_hook_registry_singleton() -> None:
    hr1 = HookRegistry()
    hr2 = HookRegistry()
    assert hr1 is hr2


def test_hook_registry_register_and_get() -> None:
    hr = HookRegistry()
    saved_hooks = hr._hooks.copy()
    try:
        hr.clear()

        @hr.register("test_hook")
        def my_hook(state: HookState, deps: HookDependencies) -> HookResult:
            return HookResult(success=True, state_delta={"test": "data"})

        hook = hr.get_hook("test_hook")
        assert hook is my_hook
    finally:
        hr._hooks = saved_hooks
