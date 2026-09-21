// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Provider to fetch executions strictly adhering to Freezed DTOs

@ProviderFor(executionList)
final executionListProvider = ExecutionListProvider._();

/// Provider to fetch executions strictly adhering to Freezed DTOs

final class ExecutionListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<ExecutionRecord>>,
          List<ExecutionRecord>,
          FutureOr<List<ExecutionRecord>>
        >
    with
        $FutureModifier<List<ExecutionRecord>>,
        $FutureProvider<List<ExecutionRecord>> {
  /// Provider to fetch executions strictly adhering to Freezed DTOs
  ExecutionListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'executionListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$executionListHash();

  @$internal
  @override
  $FutureProviderElement<List<ExecutionRecord>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<ExecutionRecord>> create(Ref ref) {
    return executionList(ref);
  }
}

String _$executionListHash() => r'53088a35bac32973bee5242a2b42f1f7a2ee3506';

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses strictly typed `ExecutionRecord` models.

@ProviderFor(ExecutionController)
final executionControllerProvider = ExecutionControllerProvider._();

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses strictly typed `ExecutionRecord` models.
final class ExecutionControllerProvider
    extends $StreamNotifierProvider<ExecutionController, ExecutionRecord?> {
  /// Controller managing the lifecycle of a V2 DAG Execution.
  ///
  /// Implements Riverpod 3.x optimal practices:
  /// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
  /// - Handles real-time backend updates efficiently without manual polling loops.
  /// - Uses strictly typed `ExecutionRecord` models.
  ExecutionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'executionControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$executionControllerHash();

  @$internal
  @override
  ExecutionController create() => ExecutionController();
}

String _$executionControllerHash() =>
    r'5cf3716f086d83e68b393cbfaff147ae7f4c0bab';

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses strictly typed `ExecutionRecord` models.

abstract class _$ExecutionController extends $StreamNotifier<ExecutionRecord?> {
  Stream<ExecutionRecord?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<ExecutionRecord?>, ExecutionRecord?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<ExecutionRecord?>, ExecutionRecord?>,
              AsyncValue<ExecutionRecord?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
