// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_providers.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 AsyncNotifier pattern.

@ProviderFor(ExecutionListController)
final executionListControllerProvider = ExecutionListControllerProvider._();

/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 AsyncNotifier pattern.
final class ExecutionListControllerProvider
    extends $AsyncNotifierProvider<ExecutionListController, List<Execution>> {
  /// Controller for the Orchestration Dashboard.
  ///
  /// Manages the state of the execution list.
  /// Uses strict Riverpod 3.0 AsyncNotifier pattern.
  ExecutionListControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'executionListControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$executionListControllerHash();

  @$internal
  @override
  ExecutionListController create() => ExecutionListController();
}

String _$executionListControllerHash() =>
    r'c3c82359a335475b2acae4470639df5644e308ae';

/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 AsyncNotifier pattern.

abstract class _$ExecutionListController
    extends $AsyncNotifier<List<Execution>> {
  FutureOr<List<Execution>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<List<Execution>>, List<Execution>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<Execution>>, List<Execution>>,
              AsyncValue<List<Execution>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
