import 'package:client_app/features/settings/domain/models/app_settings_state.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('AppSettingsState Domain Model Hardening Tests', () {
    test(
      'Positive: default constructor initializes ThemeMode.system and Locale("fi", "") and supports immutable copyWith updates',
      () {
        const defaultState = AppSettingsState();
        expect(defaultState.themeMode, equals(ThemeMode.system));
        expect(defaultState.locale, equals(const Locale('fi', '')));

        final updatedTheme = defaultState.copyWith(themeMode: ThemeMode.dark);
        expect(updatedTheme.themeMode, equals(ThemeMode.dark));
        expect(updatedTheme.locale, equals(const Locale('fi', '')));

        final updatedLocale = updatedTheme.copyWith(
          locale: const Locale('en', 'US'),
        );
        expect(updatedLocale.themeMode, equals(ThemeMode.dark));
        expect(updatedLocale.locale, equals(const Locale('en', 'US')));
      },
    );

    test(
      'Negative/Boundary 1: @Freezed(equal: false) enforces strict O(1) identity equality instead of deep value equality across separate instances',
      () {
        // Two non-const instances with identical field values must not be equal when equal: false is enforced.
        // Instantiate dynamically at runtime via helper to bypass const canonicalization.
        AppSettingsState createRuntimeInstance(
          ThemeMode mode,
          String langCode,
        ) {
          return AppSettingsState(themeMode: mode, locale: Locale(langCode));
        }

        final first = createRuntimeInstance(ThemeMode.dark, 'en');
        final second = createRuntimeInstance(ThemeMode.dark, 'en');

        expect(identical(first, second), isFalse);
        expect(first == second, isFalse);
        expect(first == first, isTrue);
      },
    );

    test(
      'Negative/Boundary 2: copyWith preserves unmodified fields across all ThemeMode enum boundaries and multi-part Locale boundaries',
      () {
        for (final mode in ThemeMode.values) {
          final state = AppSettingsState(
            themeMode: mode,
            locale: const Locale.fromSubtags(
              languageCode: 'fi',
              countryCode: 'FI',
            ),
          );
          expect(state.themeMode, equals(mode));
          expect(state.locale.languageCode, equals('fi'));
          expect(state.locale.countryCode, equals('FI'));

          // No-arg copyWith returns an instance with identical field values
          final cloned = state.copyWith();
          expect(cloned.themeMode, equals(mode));
          expect(cloned.locale, equals(state.locale));
        }
      },
    );
  });
}
