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

/// **Execution Raw Data Provider**
///
/// Fetches complete raw execution data from the /raw API endpoint.
/// This includes all agent outputs, hook outputs, and timing information.

@ProviderFor(executionRawData)
final executionRawDataProvider = ExecutionRawDataFamily._();

/// **Execution Raw Data Provider**
///
/// Fetches complete raw execution data from the /raw API endpoint.
/// This includes all agent outputs, hook outputs, and timing information.

final class ExecutionRawDataProvider
    extends
        $FunctionalProvider<
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
  /// **Execution Raw Data Provider**
  ///
  /// Fetches complete raw execution data from the /raw API endpoint.
  /// This includes all agent outputs, hook outputs, and timing information.
  ExecutionRawDataProvider._({
    required ExecutionRawDataFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'executionRawDataProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$executionRawDataHash();

  @override
  String toString() {
    return r'executionRawDataProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
    final argument = this.argument as String;
    return executionRawData(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ExecutionRawDataProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$executionRawDataHash() => r'935a6ab9b4b19a9a341082f6068f1715e6d6a59e';

/// **Execution Raw Data Provider**
///
/// Fetches complete raw execution data from the /raw API endpoint.
/// This includes all agent outputs, hook outputs, and timing information.

final class ExecutionRawDataFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
  ExecutionRawDataFamily._()
    : super(
        retry: null,
        name: r'executionRawDataProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// **Execution Raw Data Provider**
  ///
  /// Fetches complete raw execution data from the /raw API endpoint.
  /// This includes all agent outputs, hook outputs, and timing information.

  ExecutionRawDataProvider call(String executionId) =>
      ExecutionRawDataProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionRawDataProvider';
}
