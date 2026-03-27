// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Workflow API Client Provider

@ProviderFor(workflowClient)
final workflowClientProvider = WorkflowClientProvider._();

/// Workflow API Client Provider

final class WorkflowClientProvider
    extends $FunctionalProvider<WorkflowClient, WorkflowClient, WorkflowClient>
    with $Provider<WorkflowClient> {
  /// Workflow API Client Provider
  WorkflowClientProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowClientProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowClientHash();

  @$internal
  @override
  $ProviderElement<WorkflowClient> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  WorkflowClient create(Ref ref) {
    return workflowClient(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(WorkflowClient value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<WorkflowClient>(value),
    );
  }
}

String _$workflowClientHash() => r'3181e8901bc9a9e4efcb28efeb676681191d7243';
