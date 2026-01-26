// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_studio_screen.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(studioWorkflowList)
final studioWorkflowListProvider = StudioWorkflowListProvider._();

final class StudioWorkflowListProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<WorkflowSummary>>,
          List<WorkflowSummary>,
          FutureOr<List<WorkflowSummary>>
        >
    with
        $FutureModifier<List<WorkflowSummary>>,
        $FutureProvider<List<WorkflowSummary>> {
  StudioWorkflowListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'studioWorkflowListProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$studioWorkflowListHash();

  @$internal
  @override
  $FutureProviderElement<List<WorkflowSummary>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<WorkflowSummary>> create(Ref ref) {
    return studioWorkflowList(ref);
  }
}

String _$studioWorkflowListHash() =>
    r'8703b6bb0452176487764812f917f8011d24d320';
