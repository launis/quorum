// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'steps_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(StepsController)
final stepsControllerProvider = StepsControllerProvider._();

final class StepsControllerProvider
    extends $AsyncNotifierProvider<StepsController, List<StepConfig>> {
  StepsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'stepsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$stepsControllerHash();

  @$internal
  @override
  StepsController create() => StepsController();
}

String _$stepsControllerHash() => r'293669324ef332f93733bd7ca45878db9292e0f4';

abstract class _$StepsController extends $AsyncNotifier<List<StepConfig>> {
  FutureOr<List<StepConfig>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<StepConfig>>, List<StepConfig>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<StepConfig>>, List<StepConfig>>,
              AsyncValue<List<StepConfig>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
