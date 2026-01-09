// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(workflowList)
final workflowListProvider = WorkflowListProvider._();

final class WorkflowListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Workflow>>,
          List<Workflow>,
          FutureOr<List<Workflow>>
        >
    with $FutureModifier<List<Workflow>>, $FutureProvider<List<Workflow>> {
  WorkflowListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowListHash();

  @$internal
  @override
  $FutureProviderElement<List<Workflow>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Workflow>> create(Ref ref) {
    return workflowList(ref);
  }
}

String _$workflowListHash() => r'8d18c71d24fde4a4980c1e6a42835aded31e3796';
