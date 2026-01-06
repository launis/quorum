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
/// Uses strict Riverpod 3.0 [AsyncNotifier] pattern.

@ProviderFor(DashboardController)
final dashboardControllerProvider = DashboardControllerProvider._();

/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 [AsyncNotifier] pattern.
final class DashboardControllerProvider
    extends $AsyncNotifierProvider<DashboardController, List<Execution>> {
  /// Controller for the Orchestration Dashboard.
  ///
  /// Manages the state of the execution list.
  /// Uses strict Riverpod 3.0 [AsyncNotifier] pattern.
  DashboardControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'dashboardControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$dashboardControllerHash();

  @$internal
  @override
  DashboardController create() => DashboardController();
}

String _$dashboardControllerHash() =>
    r'50448d49729b0825fcd706f4ac56f6a62316acc8';

/// Controller for the Orchestration Dashboard.
///
/// Manages the state of the execution list.
/// Uses strict Riverpod 3.0 [AsyncNotifier] pattern.

abstract class _$DashboardController extends $AsyncNotifier<List<Execution>> {
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
