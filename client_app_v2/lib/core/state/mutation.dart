import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Standard Riverpod 3.0 UI Mutation State
class MutationState<T> {
  final AsyncValue<T>? state;
  final Future<T?> Function(Future<T> Function() action) mutate;

  const MutationState({required this.state, required this.mutate});

  bool get isIdle => state == null;
  bool get isLoading => state?.isLoading ?? false;
  bool get hasError => state?.hasError ?? false;
  bool get isSuccess => state?.hasValue ?? false && !state!.isLoading && !state!.hasError;

  Object? get error => state?.error;
  StackTrace? get stackTrace => state?.stackTrace;
  T? get value => state?.value;
}

/// Standardized Hook for Riverpod UI Mutations.
/// 
/// Replaces manual `bool isLoading` flags and ad-hoc error catching.
/// Ensures all side-effects follow: Idle -> Pending -> Success / Error.
MutationState<T> useMutation<T>({
  void Function(T data)? onSuccess,
  void Function(Object error)? onError,
}) {
  final state = useState<AsyncValue<T>?>(null);

  final mutate = useCallback((Future<T> Function() action) async {
    state.value = const AsyncValue.loading();
    try {
      final result = await action();
      state.value = AsyncValue.data(result);
      if (onSuccess != null) onSuccess(result);
      return result;
    } catch (e, stack) {
      state.value = AsyncValue.error(e, stack);
      if (onError != null) onError(e);
      return null;
    }
  }, [onSuccess, onError]);

  return MutationState(state: state.value, mutate: mutate);
}

/// A standard explicit wrapper button that reflects the Mutation lifecycle.
class MutationButton<T> extends StatelessWidget {
  final MutationState<T> mutation;
  final Future<T> Function()? action;
  final String label;
  final IconData? icon;
  final Widget? child;

  const MutationButton({
    super.key,
    required this.mutation,
    required this.label,
    this.action,
    this.icon,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    if (mutation.isLoading) {
      return const FilledButton(
        onPressed: null,
        child: SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(strokeWidth: 2),
        ),
      );
    }
    return FilledButton.icon(
      onPressed: action == null ? null : () => mutation.mutate(action!),
      icon: icon != null ? Icon(icon) : const SizedBox.shrink(),
      label: child ?? Text(label),
    );
  }
}
