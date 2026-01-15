// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_execution_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Manages the state of the active workflow execution.

@ProviderFor(WorkflowExecution)
final workflowExecutionProvider = WorkflowExecutionProvider._();

/// Manages the state of the active workflow execution.
final class WorkflowExecutionProvider
    extends $NotifierProvider<WorkflowExecution, AsyncValue<Execution?>> {
  /// Manages the state of the active workflow execution.
  WorkflowExecutionProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowExecutionProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowExecutionHash();

  @$internal
  @override
  WorkflowExecution create() => WorkflowExecution();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AsyncValue<Execution?> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AsyncValue<Execution?>>(value),
    );
  }
}

String _$workflowExecutionHash() => r'720ab27c3ded29baa0926ecd97021d9f9249d87a';

/// Manages the state of the active workflow execution.

abstract class _$WorkflowExecution extends $Notifier<AsyncValue<Execution?>> {
  AsyncValue<Execution?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<Execution?>, AsyncValue<Execution?>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<Execution?>, AsyncValue<Execution?>>,
              AsyncValue<Execution?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
