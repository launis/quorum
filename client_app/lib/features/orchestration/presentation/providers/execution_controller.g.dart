// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Execution Data Stream**
///
/// Provides real-time updates for a specific execution ID.
/// Automatically handles polling and lifecycle via [ExecutionRepository.streamExecution].

@ProviderFor(executionStream)
final executionStreamProvider = ExecutionStreamFamily._();

/// **Execution Data Stream**
///
/// Provides real-time updates for a specific execution ID.
/// Automatically handles polling and lifecycle via [ExecutionRepository.streamExecution].

final class ExecutionStreamProvider
    extends
        $FunctionalProvider<AsyncValue<Execution>, Execution, Stream<Execution>>
    with $FutureModifier<Execution>, $StreamProvider<Execution> {
  /// **Execution Data Stream**
  ///
  /// Provides real-time updates for a specific execution ID.
  /// Automatically handles polling and lifecycle via [ExecutionRepository.streamExecution].
  ExecutionStreamProvider._({
    required ExecutionStreamFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'executionStreamProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$executionStreamHash();

  @override
  String toString() {
    return r'executionStreamProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $StreamProviderElement<Execution> $createElement($ProviderPointer pointer) =>
      $StreamProviderElement(pointer);

  @override
  Stream<Execution> create(Ref ref) {
    final argument = this.argument as String;
    return executionStream(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ExecutionStreamProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$executionStreamHash() => r'75844d06741279b7d7b5002a7bae1161e1a923fa';

/// **Execution Data Stream**
///
/// Provides real-time updates for a specific execution ID.
/// Automatically handles polling and lifecycle via [ExecutionRepository.streamExecution].

final class ExecutionStreamFamily extends $Family
    with $FunctionalFamilyOverride<Stream<Execution>, String> {
  ExecutionStreamFamily._()
    : super(
        retry: null,
        name: r'executionStreamProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// **Execution Data Stream**
  ///
  /// Provides real-time updates for a specific execution ID.
  /// Automatically handles polling and lifecycle via [ExecutionRepository.streamExecution].

  ExecutionStreamProvider call(String executionId) =>
      ExecutionStreamProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionStreamProvider';
}

/// **Execution Controller (Actions)**
///
/// Manages actions like `startAnalysis`.
/// DOES NOT manage the state of the active execution (use [executionStreamProvider]).

@ProviderFor(ExecutionController)
final executionControllerProvider = ExecutionControllerProvider._();

/// **Execution Controller (Actions)**
///
/// Manages actions like `startAnalysis`.
/// DOES NOT manage the state of the active execution (use [executionStreamProvider]).
final class ExecutionControllerProvider
    extends $AsyncNotifierProvider<ExecutionController, void> {
  /// **Execution Controller (Actions)**
  ///
  /// Manages actions like `startAnalysis`.
  /// DOES NOT manage the state of the active execution (use [executionStreamProvider]).
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
    r'3d5e5a8925fa56a541d41d844cddfe7085c3a824';

/// **Execution Controller (Actions)**
///
/// Manages actions like `startAnalysis`.
/// DOES NOT manage the state of the active execution (use [executionStreamProvider]).

abstract class _$ExecutionController extends $AsyncNotifier<void> {
  FutureOr<void> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<void>, void>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<void>, void>,
              AsyncValue<void>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
