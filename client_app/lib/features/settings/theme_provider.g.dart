// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'theme_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Theme Mode Provider**
///
/// Manages the application's [ThemeMode] (Light, Dark, System).
/// Persists the user's preference using [SharedPreferences].
///
/// **Design**:
/// - Defaults to [ThemeMode.system] if no preference is saved.
/// - Loads preference asynchronously on startup (defaulting to system while loading).
/// - Exposes methods to update and save the preference.

@ProviderFor(ThemeModeNotifier)
final themeModeProvider = ThemeModeNotifierProvider._();

/// **Theme Mode Provider**
///
/// Manages the application's [ThemeMode] (Light, Dark, System).
/// Persists the user's preference using [SharedPreferences].
///
/// **Design**:
/// - Defaults to [ThemeMode.system] if no preference is saved.
/// - Loads preference asynchronously on startup (defaulting to system while loading).
/// - Exposes methods to update and save the preference.
final class ThemeModeNotifierProvider
    extends $NotifierProvider<ThemeModeNotifier, ThemeMode> {
  /// **Theme Mode Provider**
  ///
  /// Manages the application's [ThemeMode] (Light, Dark, System).
  /// Persists the user's preference using [SharedPreferences].
  ///
  /// **Design**:
  /// - Defaults to [ThemeMode.system] if no preference is saved.
  /// - Loads preference asynchronously on startup (defaulting to system while loading).
  /// - Exposes methods to update and save the preference.
  ThemeModeNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'themeModeProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$themeModeNotifierHash();

  @$internal
  @override
  ThemeModeNotifier create() => ThemeModeNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ThemeMode value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ThemeMode>(value),
    );
  }
}

String _$themeModeNotifierHash() => r'c5af43c3c94fd234bf0ea93964349fb1f6bdcfd6';

/// **Theme Mode Provider**
///
/// Manages the application's [ThemeMode] (Light, Dark, System).
/// Persists the user's preference using [SharedPreferences].
///
/// **Design**:
/// - Defaults to [ThemeMode.system] if no preference is saved.
/// - Loads preference asynchronously on startup (defaulting to system while loading).
/// - Exposes methods to update and save the preference.

abstract class _$ThemeModeNotifier extends $Notifier<ThemeMode> {
  ThemeMode build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<ThemeMode, ThemeMode>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<ThemeMode, ThemeMode>,
              ThemeMode,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
