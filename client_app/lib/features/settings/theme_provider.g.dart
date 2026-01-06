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

String _$themeModeNotifierHash() => r'ea228f10a5ed4f78baf99af81851a7ee224da94f';

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
