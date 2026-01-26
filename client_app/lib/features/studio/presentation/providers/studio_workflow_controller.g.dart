// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_workflow_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(StudioWorkflowController)
final studioWorkflowControllerProvider = StudioWorkflowControllerFamily._();

final class StudioWorkflowControllerProvider
    extends
        $AsyncNotifierProvider<StudioWorkflowController, WorkflowEditorState> {
  StudioWorkflowControllerProvider._({
    required StudioWorkflowControllerFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'studioWorkflowControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$studioWorkflowControllerHash();

  @override
  String toString() {
    return r'studioWorkflowControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  StudioWorkflowController create() => StudioWorkflowController();

  @override
  bool operator ==(Object other) {
    return other is StudioWorkflowControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$studioWorkflowControllerHash() =>
    r'2782b311d880440a6675ba34699ba7be9deb2112';

final class StudioWorkflowControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          StudioWorkflowController,
          AsyncValue<WorkflowEditorState>,
          WorkflowEditorState,
          FutureOr<WorkflowEditorState>,
          String
        > {
  StudioWorkflowControllerFamily._()
    : super(
        retry: null,
        name: r'studioWorkflowControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  StudioWorkflowControllerProvider call(String workflowId) =>
      StudioWorkflowControllerProvider._(argument: workflowId, from: this);

  @override
  String toString() => r'studioWorkflowControllerProvider';
}

abstract class _$StudioWorkflowController
    extends $AsyncNotifier<WorkflowEditorState> {
  late final _$args = ref.$arg as String;
  String get workflowId => _$args;

  FutureOr<WorkflowEditorState> build(String workflowId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<WorkflowEditorState>, WorkflowEditorState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<WorkflowEditorState>, WorkflowEditorState>,
              AsyncValue<WorkflowEditorState>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
