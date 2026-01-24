// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Execution Data Stream**
///
/// Legacy/Simple polling provider (retained for fallback/simplicity if needed)
/// But ExecutionController now takes over active monitoring.

@ProviderFor(executionStream)
final executionStreamProvider = ExecutionStreamFamily._();

/// **Execution Data Stream**
///
/// Legacy/Simple polling provider (retained for fallback/simplicity if needed)
/// But ExecutionController now takes over active monitoring.

final class ExecutionStreamProvider
    extends
        $FunctionalProvider<AsyncValue<Execution>, Execution, Stream<Execution>>
    with $FutureModifier<Execution>, $StreamProvider<Execution> {
  /// **Execution Data Stream**
  ///
  /// Legacy/Simple polling provider (retained for fallback/simplicity if needed)
  /// But ExecutionController now takes over active monitoring.
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
/// Legacy/Simple polling provider (retained for fallback/simplicity if needed)
/// But ExecutionController now takes over active monitoring.

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
  /// Legacy/Simple polling provider (retained for fallback/simplicity if needed)
  /// But ExecutionController now takes over active monitoring.

  ExecutionStreamProvider call(String executionId) =>
      ExecutionStreamProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionStreamProvider';
}

/// **Execution Controller**
///
/// Manages the state of the active execution, including SSE monitoring and actions.

@ProviderFor(ExecutionController)
final executionControllerProvider = ExecutionControllerProvider._();

/// **Execution Controller**
///
/// Manages the state of the active execution, including SSE monitoring and actions.
final class ExecutionControllerProvider
    extends $AsyncNotifierProvider<ExecutionController, Execution?> {
  /// **Execution Controller**
  ///
  /// Manages the state of the active execution, including SSE monitoring and actions.
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
    r'7b4bdd3dfdb8c437dc37daa18c3abfdf6f70bd4b';

/// **Execution Controller**
///
/// Manages the state of the active execution, including SSE monitoring and actions.

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
