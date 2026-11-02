// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'settings_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Manages application theme and locale preferences via non-blocking `SharedPreferencesAsync`.

@ProviderFor(SettingsController)
final settingsControllerProvider = SettingsControllerProvider._();

/// Manages application theme and locale preferences via non-blocking `SharedPreferencesAsync`.
final class SettingsControllerProvider
    extends $AsyncNotifierProvider<SettingsController, AppSettingsState> {
  /// Manages application theme and locale preferences via non-blocking `SharedPreferencesAsync`.
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
    r'72c12db45e9b9a66d47bf2f2fb561cc1d5f668c4';

/// Manages application theme and locale preferences via non-blocking `SharedPreferencesAsync`.

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
