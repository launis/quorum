// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Manages the state of the *currently active* or *most recently created* execution.
///
/// **Role**:
/// - Validation of inputs.
/// - triggering `startAnalysis`.
/// - Polling for status updates (simple polling for MVP).

@ProviderFor(ExecutionController)
final executionControllerProvider = ExecutionControllerProvider._();

/// Manages the state of the *currently active* or *most recently created* execution.
///
/// **Role**:
/// - Validation of inputs.
/// - triggering `startAnalysis`.
/// - Polling for status updates (simple polling for MVP).
final class ExecutionControllerProvider
    extends $AsyncNotifierProvider<ExecutionController, Execution?> {
  /// Manages the state of the *currently active* or *most recently created* execution.
  ///
  /// **Role**:
  /// - Validation of inputs.
  /// - triggering `startAnalysis`.
  /// - Polling for status updates (simple polling for MVP).
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
    r'21a607918b428d6dd9418acad521002a7d3cc91d';

/// Manages the state of the *currently active* or *most recently created* execution.
///
/// **Role**:
/// - Validation of inputs.
/// - triggering `startAnalysis`.
/// - Polling for status updates (simple polling for MVP).

abstract class _$ExecutionController extends $AsyncNotifier<Execution?> {
  FutureOr<Execution?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<Execution?>, Execution?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<Execution?>, Execution?>,
              AsyncValue<Execution?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
