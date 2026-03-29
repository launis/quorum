// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'settings_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Settings Controller**
///
/// Adheres to V2 Flutter Mandates (5.3 Concurrency):
/// Uses `SharedPreferencesAsync` to avoid blocking the main UI thread during I/O.

@ProviderFor(SettingsController)
final settingsControllerProvider = SettingsControllerProvider._();

/// **Settings Controller**
///
/// Adheres to V2 Flutter Mandates (5.3 Concurrency):
/// Uses `SharedPreferencesAsync` to avoid blocking the main UI thread during I/O.
final class SettingsControllerProvider
    extends $AsyncNotifierProvider<SettingsController, AppSettingsState> {
  /// **Settings Controller**
  ///
  /// Adheres to V2 Flutter Mandates (5.3 Concurrency):
  /// Uses `SharedPreferencesAsync` to avoid blocking the main UI thread during I/O.
  SettingsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'settingsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$settingsControllerHash();

  @$internal
  @override
  SettingsController create() => SettingsController();
}

String _$settingsControllerHash() =>
    r'a87502b6937bfb4a70546a059d4174b47e147554';

/// **Settings Controller**
///
/// Adheres to V2 Flutter Mandates (5.3 Concurrency):
/// Uses `SharedPreferencesAsync` to avoid blocking the main UI thread during I/O.

abstract class _$SettingsController extends $AsyncNotifier<AppSettingsState> {
  FutureOr<AppSettingsState> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<AppSettingsState>, AppSettingsState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<AppSettingsState>, AppSettingsState>,
              AsyncValue<AppSettingsState>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
