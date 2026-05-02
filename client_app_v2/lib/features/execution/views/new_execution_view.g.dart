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
          AsyncValue<List<Map<String, dynamic>>>,
          List<Map<String, dynamic>>,
          FutureOr<List<Map<String, dynamic>>>
        >
    with
        $FutureModifier<List<Map<String, dynamic>>>,
        $FutureProvider<List<Map<String, dynamic>>> {
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
  $FutureProviderElement<List<Map<String, dynamic>>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Map<String, dynamic>>> create(Ref ref) {
    return availableWorkflows(ref);
  }
}

String _$availableWorkflowsHash() =>
    r'19ae922d67285befdac2f993e92010ab3d206610';

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
    r'25f3f7e831ff4f3785413fc861823c3aefc0b873';

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
