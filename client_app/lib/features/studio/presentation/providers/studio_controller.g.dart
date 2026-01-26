// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(StudioController)
final studioControllerProvider = StudioControllerProvider._();

final class StudioControllerProvider
    extends $AsyncNotifierProvider<StudioController, WorkflowDef?> {
  StudioControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'studioControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$studioControllerHash();

  @$internal
  @override
  StudioController create() => StudioController();
}

String _$studioControllerHash() => r'b29a1fb08a48f3f222d32a85e00a8b9bed3723f2';

abstract class _$StudioController extends $AsyncNotifier<WorkflowDef?> {
  FutureOr<WorkflowDef?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<WorkflowDef?>, WorkflowDef?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<WorkflowDef?>, WorkflowDef?>,
              AsyncValue<WorkflowDef?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
