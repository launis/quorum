// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'new_execution_view.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(availableWorkflows)
final availableWorkflowsProvider = AvailableWorkflowsProvider._();

final class AvailableWorkflowsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Workflow>>,
          List<Workflow>,
          FutureOr<List<Workflow>>
        >
    with $FutureModifier<List<Workflow>>, $FutureProvider<List<Workflow>> {
  AvailableWorkflowsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableWorkflowsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableWorkflowsHash();

  @$internal
  @override
  $FutureProviderElement<List<Workflow>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Workflow>> create(Ref ref) {
    return availableWorkflows(ref);
  }
}

String _$availableWorkflowsHash() =>
    r'6daccfc472d3b4c4275393f75039c22ff4e26acb';

@ProviderFor(NewExecutionController)
final newExecutionControllerProvider = NewExecutionControllerProvider._();

final class NewExecutionControllerProvider
    extends $AsyncNotifierProvider<NewExecutionController, void> {
  NewExecutionControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'newExecutionControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$newExecutionControllerHash();

  @$internal
  @override
  NewExecutionController create() => NewExecutionController();
}

String _$newExecutionControllerHash() =>
    r'b934c9e57c6f9f97dd3ce2c91caa2542b5a4521a';

abstract class _$NewExecutionController extends $AsyncNotifier<void> {
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
