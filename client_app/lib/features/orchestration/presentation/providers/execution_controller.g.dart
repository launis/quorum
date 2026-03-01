// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Execution Data Stream (Full Domain Model)**
///
/// Real-time monitoring of a specific execution via SSE.
/// Used by ExecutionResultScreen and ExecutionDetailsScreen.

@ProviderFor(executionStream)
final executionStreamProvider = ExecutionStreamFamily._();

/// **Execution Data Stream (Full Domain Model)**
///
/// Real-time monitoring of a specific execution via SSE.
/// Used by ExecutionResultScreen and ExecutionDetailsScreen.

final class ExecutionStreamProvider
    extends
        $FunctionalProvider<AsyncValue<Execution>, Execution, Stream<Execution>>
    with $FutureModifier<Execution>, $StreamProvider<Execution> {
  /// **Execution Data Stream (Full Domain Model)**
  ///
  /// Real-time monitoring of a specific execution via SSE.
  /// Used by ExecutionResultScreen and ExecutionDetailsScreen.
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

String _$executionStreamHash() => r'c497ee1b811204bbf03b40c9ceb350d1ac0f8e0f';

/// **Execution Data Stream (Full Domain Model)**
///
/// Real-time monitoring of a specific execution via SSE.
/// Used by ExecutionResultScreen and ExecutionDetailsScreen.

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

  /// **Execution Data Stream (Full Domain Model)**
  ///
  /// Real-time monitoring of a specific execution via SSE.
  /// Used by ExecutionResultScreen and ExecutionDetailsScreen.

  ExecutionStreamProvider call(String executionId) =>
      ExecutionStreamProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionStreamProvider';
}

/// **Assessment View Data Stream (Server-Driven UI)**
///
/// Real-time monitoring via SSE, projected to a View Model.
/// Used by ExecutionMonitorScreen.

@ProviderFor(assessmentStream)
final assessmentStreamProvider = AssessmentStreamFamily._();

/// **Assessment View Data Stream (Server-Driven UI)**
///
/// Real-time monitoring via SSE, projected to a View Model.
/// Used by ExecutionMonitorScreen.

final class AssessmentStreamProvider
    extends
        $FunctionalProvider<
          AsyncValue<AssessmentView>,
          AssessmentView,
          Stream<AssessmentView>
        >
    with $FutureModifier<AssessmentView>, $StreamProvider<AssessmentView> {
  /// **Assessment View Data Stream (Server-Driven UI)**
  ///
  /// Real-time monitoring via SSE, projected to a View Model.
  /// Used by ExecutionMonitorScreen.
  AssessmentStreamProvider._({
    required AssessmentStreamFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'assessmentStreamProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$assessmentStreamHash();

  @override
  String toString() {
    return r'assessmentStreamProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $StreamProviderElement<AssessmentView> $createElement(
    $ProviderPointer pointer,
  ) => $StreamProviderElement(pointer);

  @override
  Stream<AssessmentView> create(Ref ref) {
    final argument = this.argument as String;
    return assessmentStream(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is AssessmentStreamProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$assessmentStreamHash() => r'958a8bda9806b36c47f609a923196f9338d954b8';

/// **Assessment View Data Stream (Server-Driven UI)**
///
/// Real-time monitoring via SSE, projected to a View Model.
/// Used by ExecutionMonitorScreen.

final class AssessmentStreamFamily extends $Family
    with $FunctionalFamilyOverride<Stream<AssessmentView>, String> {
  AssessmentStreamFamily._()
    : super(
        retry: null,
        name: r'assessmentStreamProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// **Assessment View Data Stream (Server-Driven UI)**
  ///
  /// Real-time monitoring via SSE, projected to a View Model.
  /// Used by ExecutionMonitorScreen.

  AssessmentStreamProvider call(String executionId) =>
      AssessmentStreamProvider._(argument: executionId, from: this);

  @override
  String toString() => r'assessmentStreamProvider';
}

/// **Execution Actions Controller**
///
/// Manages actions like Start, Cancel, Delete.
/// Does NOT hold the active execution state (use [executionStream] for that).

@ProviderFor(ExecutionController)
final executionControllerProvider = ExecutionControllerProvider._();

/// **Execution Actions Controller**
///
/// Manages actions like Start, Cancel, Delete.
/// Does NOT hold the active execution state (use [executionStream] for that).
final class ExecutionControllerProvider
    extends $AsyncNotifierProvider<ExecutionController, void> {
  /// **Execution Actions Controller**
  ///
  /// Manages actions like Start, Cancel, Delete.
  /// Does NOT hold the active execution state (use [executionStream] for that).
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
    r'6f14104f9ccf463d2335623dcb28d432cd15fb7d';

/// **Execution Actions Controller**
///
/// Manages actions like Start, Cancel, Delete.
/// Does NOT hold the active execution state (use [executionStream] for that).

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

@ProviderFor(executionRawData)
final executionRawDataProvider = ExecutionRawDataFamily._();

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

  ExecutionRawDataProvider call(String executionId) =>
      ExecutionRawDataProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionRawDataProvider';
}
