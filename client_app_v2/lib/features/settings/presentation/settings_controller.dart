import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/settings/domain/models/app_settings_state.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'settings_controller.g.dart';

/// Manages application theme and locale preferences via non-blocking `SharedPreferencesAsync`.
@riverpod
class SettingsController extends _$SettingsController {
  SettingsController({SharedPreferencesAsync? prefs})
    : _prefs = prefs ?? SharedPreferencesAsync();

  final SharedPreferencesAsync _prefs;

  static const _themeModeKey = 'app_theme_mode';
  static const _localeKey = 'app_locale';

  @override
  FutureOr<AppSettingsState> build() async {
    const defaultState = AppSettingsState();
    final themeStr = await _prefs.getString(_themeModeKey);
    final localeStr = await _prefs.getString(_localeKey);

    return AppSettingsState(
      themeMode: _parseThemeMode(themeStr, defaultState.themeMode),
      locale: _parseLocale(localeStr, defaultState.locale),
    );
  }

  /// Updates theme mode optimistically and rolls back state on persistence failure.
  Future<void> updateThemeMode(ThemeMode newMode) async {
    final previousState = switch (state) {
      AsyncData(:final value) => value,
      _ => null,
    };
    if (previousState != null) {
      state = AsyncData(previousState.copyWith(themeMode: newMode));
    }

    try {
      await _prefs.setString(_themeModeKey, newMode.name);
    } catch (e, st) {
      if (ref.mounted) {
        ref
            .read(loggerServiceProvider)
            .error('SettingsController', 'Failed to update theme mode', e, st);
        if (previousState != null) {
          state = AsyncData(previousState);
        } else {
          state = AsyncError(e, st);
        }
      }
      rethrow;
    }
  }

  /// Validates and updates locale optimistically, rolling back state on persistence failure.
  Future<void> updateLocale(Locale newLocale) async {
    final isSupported = AppLocalizations.supportedLocales.any(
      (locale) => locale.languageCode == newLocale.languageCode,
    );
    if (!isSupported) {
      _failValidation(
        'SETTINGS_INVALID_LOCALE',
        'Unsupported locale "${newLocale.languageCode}".',
      );
    }

    final previousState = switch (state) {
      AsyncData(:final value) => value,
      _ => null,
    };
    if (previousState != null) {
      state = AsyncData(previousState.copyWith(locale: newLocale));
    }

    try {
      await _prefs.setString(_localeKey, newLocale.languageCode);
    } catch (e, st) {
      if (ref.mounted) {
        ref
            .read(loggerServiceProvider)
            .error('SettingsController', 'Failed to update locale', e, st);
        if (previousState != null) {
          state = AsyncData(previousState);
        } else {
          state = AsyncError(e, st);
        }
      }
      rethrow;
    }
  }

  /// Synchronizes persisted backend user preferences (`language` and `themeMode`) into local settings state.
  Future<void> syncFromUserProfile({
    String? language,
    String? themeMode,
  }) async {
    final current = switch (state) {
      AsyncData(:final value) => value,
      _ => const AppSettingsState(),
    };

    ThemeMode resolvedTheme = current.themeMode;
    if (themeMode != null && themeMode.trim().isNotEmpty) {
      final normalizedTheme = themeMode.trim().toLowerCase();
      if (normalizedTheme == 'system' ||
          normalizedTheme == 'light' ||
          normalizedTheme == 'dark') {
        resolvedTheme = _parseThemeMode(normalizedTheme, current.themeMode);
      }
    }

    Locale resolvedLocale = current.locale;
    if (language != null && language.trim().isNotEmpty) {
      final normalizedLang = language.trim().toLowerCase();
      final isSupported = AppLocalizations.supportedLocales.any(
        (locale) => locale.languageCode == normalizedLang,
      );
      if (isSupported) {
        resolvedLocale = Locale(normalizedLang);
      }
    }

    state = AsyncData(
      current.copyWith(themeMode: resolvedTheme, locale: resolvedLocale),
    );

    try {
      await _prefs.setString(_themeModeKey, resolvedTheme.name);
      await _prefs.setString(_localeKey, resolvedLocale.languageCode);
    } catch (e, st) {
      if (ref.mounted) {
        ref
            .read(loggerServiceProvider)
            .warning(
              'SettingsController',
              'Could not persist synced user profile preferences locally: $e\n$st',
            );
      }
    }
  }

  ThemeMode _parseThemeMode(String? val, ThemeMode uninitializedDefault) {
    return switch (val) {
      null => uninitializedDefault,
      'system' => ThemeMode.system,
      'light' => ThemeMode.light,
      'dark' => ThemeMode.dark,
      _ => _failValidation(
        'SETTINGS_INVALID_THEME_MODE',
        'Unrecognized persisted theme mode "$val".',
      ),
    };
  }

  Locale _parseLocale(String? val, Locale uninitializedDefault) {
    if (val == null) {
      return uninitializedDefault;
    }
    final isSupported = AppLocalizations.supportedLocales.any(
      (locale) => locale.languageCode == val,
    );
    if (!isSupported) {
      _failValidation(
        'SETTINGS_INVALID_LOCALE',
        'Unsupported persisted locale "$val".',
      );
    }
    return Locale(val);
  }

  Never _failValidation(String code, String message) {
    final exception = AppException.validation('$code: $message');
    ref
        .read(loggerServiceProvider)
        .error('SettingsController', '$code: $message', exception);
    throw exception;
  }
}
