// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Provider to fetch executions using native casting (No Freezed API DTOs)

@ProviderFor(executionList)
final executionListProvider = ExecutionListProvider._();

/// Provider to fetch executions using native casting (No Freezed API DTOs)

final class ExecutionListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Map<String, dynamic>>>,
          List<Map<String, dynamic>>,
          FutureOr<List<Map<String, dynamic>>>
        >
    with
        $FutureModifier<List<Map<String, dynamic>>>,
        $FutureProvider<List<Map<String, dynamic>>> {
  /// Provider to fetch executions using native casting (No Freezed API DTOs)
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
  $FutureProviderElement<List<Map<String, dynamic>>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Map<String, dynamic>>> create(Ref ref) {
    return executionList(ref);
  }
}

String _$executionListHash() => r'48613113487c8f8b6e793453e63b0b32b8229ba8';

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses raw `Map<String, dynamic>` strictly adhering to the De-Generator Policy.

@ProviderFor(ExecutionController)
final executionControllerProvider = ExecutionControllerProvider._();

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses raw `Map<String, dynamic>` strictly adhering to the De-Generator Policy.
final class ExecutionControllerProvider
    extends
        $StreamNotifierProvider<ExecutionController, Map<String, dynamic>?> {
  /// Controller managing the lifecycle of a V2 DAG Execution.
  ///
  /// Implements Riverpod 3.x optimal practices:
  /// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
  /// - Handles real-time backend updates efficiently without manual polling loops.
  /// - Uses raw `Map<String, dynamic>` strictly adhering to the De-Generator Policy.
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
    r'71d16ba8f0913ad82c5fb80b4eb1542e9d8c99dc';

/// Controller managing the lifecycle of a V2 DAG Execution.
///
/// Implements Riverpod 3.x optimal practices:
/// - Uses [StreamNotifier] for built-in loading/error/data states reacting to SSE.
/// - Handles real-time backend updates efficiently without manual polling loops.
/// - Uses raw `Map<String, dynamic>` strictly adhering to the De-Generator Policy.

abstract class _$ExecutionController
    extends $StreamNotifier<Map<String, dynamic>?> {
  Stream<Map<String, dynamic>?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<Map<String, dynamic>?>, Map<String, dynamic>?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, dynamic>?>,
                Map<String, dynamic>?
              >,
              AsyncValue<Map<String, dynamic>?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
