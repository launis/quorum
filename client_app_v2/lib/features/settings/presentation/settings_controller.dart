import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:client_app/features/settings/domain/models/app_settings_state.dart';
import 'package:client_app/core/logging/logger_service.dart';

part 'settings_controller.g.dart';

/// **Settings Controller**
///
/// Adheres to V2 Flutter Mandates (5.3 Concurrency):
/// Uses `SharedPreferencesAsync` to avoid blocking the main UI thread during I/O.
@riverpod
class SettingsController extends _$SettingsController {
  final _prefs = SharedPreferencesAsync();

  static const _themeModeKey = 'app_theme_mode';
  static const _localeKey = 'app_locale';

  @override
  FutureOr<AppSettingsState> build() async {
    // Read from SharedPreferencesAsync (Non-blocking I/O)
    final themeStr = await _prefs.getString(_themeModeKey);
    final localeStr = await _prefs.getString(_localeKey);

    return AppSettingsState(
      themeMode: _parseThemeMode(themeStr),
      locale: Locale(localeStr ?? 'fi'),
    );
  }

  /// Implements Optimistic Update pattern
  Future<void> updateThemeMode(ThemeMode newMode) async {
    // 1. Optimistic UI update
    final previousState = state.value;
    if (previousState != null) {
      state = AsyncData(previousState.copyWith(themeMode: newMode));
    }

    // 2. Persist to storage
    try {
      await _prefs.setString(_themeModeKey, newMode.name);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('SettingsController', 'Failed to update theme mode', e, st);
      // 3. Rollback on failure
      if (previousState != null) {
        state = AsyncData(previousState);
      }
      state = AsyncError(e, st);
    }
  }

  /// Implements Optimistic Update pattern
  Future<void> updateLocale(Locale newLocale) async {
    // 1. Optimistic UI update
    final previousState = state.value;
    if (previousState != null) {
      state = AsyncData(previousState.copyWith(locale: newLocale));
    }

    // 2. Persist to storage
    try {
      await _prefs.setString(_localeKey, newLocale.languageCode);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('SettingsController', 'Failed to update locale', e, st);
      // 3. Rollback on failure
      if (previousState != null) {
        state = AsyncData(previousState);
      }
      state = AsyncError(e, st);
    }
  }

  ThemeMode _parseThemeMode(String? val) {
    if (val == ThemeMode.light.name) return ThemeMode.light;
    if (val == ThemeMode.dark.name) return ThemeMode.dark;
    return ThemeMode.system; // Default
  }
}
