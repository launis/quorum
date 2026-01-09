// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(workflowRepository)
final workflowRepositoryProvider = WorkflowRepositoryProvider._();

final class WorkflowRepositoryProvider
    extends
        $FunctionalProvider<
          WorkflowRepository,
          WorkflowRepository,
          WorkflowRepository
        >
    with $Provider<WorkflowRepository> {
  WorkflowRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowRepositoryHash();

  @$internal
  @override
  $ProviderElement<WorkflowRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  WorkflowRepository create(Ref ref) {
    return workflowRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(WorkflowRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<WorkflowRepository>(value),
    );
  }
}

String _$workflowRepositoryHash() =>
    r'd0811316c52f1e80400b1a8f3d556ccef9109fd3';
