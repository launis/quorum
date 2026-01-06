import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'theme_provider.g.dart';

/// **Theme Mode Provider**
///
/// Manages the application's [ThemeMode] (Light, Dark, System).
/// Persists the user's preference using [SharedPreferences].
///
/// **Design**:
/// - Defaults to [ThemeMode.system] if no preference is saved.
/// - Loads preference asynchronously on startup (defaulting to system while loading).
/// - Exposes methods to update and save the preference.
@riverpod
class ThemeModeNotifier extends _$ThemeModeNotifier {
  static const _storageKey = 'theme_mode_preference';

  @override
  ThemeMode build() {
    // We can load the specific value here if we want synchronous startup behavior,
    // but ideally we load it asynchronously.
    // For simplicity in a Notifier, we start with System and load immediately.
    _loadTheme();
    return ThemeMode.system;
  }

  Future<void> _loadTheme() async {
    final prefs = await SharedPreferences.getInstance();
    final savedMode = prefs.getString(_storageKey);

    if (savedMode != null) {
      final mode = ThemeMode.values.firstWhere(
        (e) => e.toString() == savedMode,
        orElse: () => ThemeMode.system,
      );
      state = mode;
    }
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    state = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_storageKey, mode.toString());
  }
}
