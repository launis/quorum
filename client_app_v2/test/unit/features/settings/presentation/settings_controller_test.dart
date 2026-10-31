import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/settings/domain/models/app_settings_state.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MockLoggerService extends Mock implements LoggerService {}

class _StatefulFakeSharedPreferencesAsync implements SharedPreferencesAsync {
  _StatefulFakeSharedPreferencesAsync({
    Map<String, String>? initialStore,
    this.shouldFailWrite,
  }) : _store = Map<String, String>.from(initialStore ?? const {});

  final Map<String, String> _store;
  final bool Function()? shouldFailWrite;

  Map<String, String> get snapshot => Map<String, String>.unmodifiable(_store);

  @override
  Future<String?> getString(String key) async => _store[key];

  @override
  Future<void> setString(String key, String value) async {
    if (shouldFailWrite?.call() ?? false) {
      throw StateError('Disk I/O write failure for key "$key"');
    }
    _store[key] = value;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  late MockLoggerService mockLogger;
  late _StatefulFakeSharedPreferencesAsync fakePrefs;

  ProviderContainer createContainer(_StatefulFakeSharedPreferencesAsync prefs) {
    return ProviderContainer(
      retry: (retryCount, error) => null,
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        settingsControllerProvider.overrideWith(
          () => SettingsController(prefs: prefs),
        ),
      ],
    );
  }

  setUp(() {
    mockLogger = MockLoggerService();
    fakePrefs = _StatefulFakeSharedPreferencesAsync();
  });

  group('SettingsController Hardening Tests', () {
    test(
      'Positive: hydrates AppSettingsState defaults when storage is empty and persists themeMode and locale across stateful roundtrips',
      () async {
        final container = createContainer(fakePrefs);
        addTearDown(container.dispose);

        final AppSettingsState initial = await container.read(
          settingsControllerProvider.future,
        );
        expect(initial.themeMode, equals(ThemeMode.system));
        expect(initial.locale, equals(const Locale('fi', '')));

        final notifier = container.read(settingsControllerProvider.notifier);

        await notifier.updateThemeMode(ThemeMode.dark);
        expect(
          container.read(settingsControllerProvider).value?.themeMode,
          equals(ThemeMode.dark),
        );
        expect(fakePrefs.snapshot['app_theme_mode'], equals('dark'));

        await notifier.updateLocale(const Locale('en'));
        expect(
          container.read(settingsControllerProvider).value?.locale,
          equals(const Locale('en')),
        );
        expect(fakePrefs.snapshot['app_locale'], equals('en'));

        // Reconstitute in a fresh ProviderContainer against the same stateful store to prove roundtrip persistence
        final secondContainer = createContainer(fakePrefs);
        addTearDown(secondContainer.dispose);

        final AppSettingsState roundtripState = await secondContainer.read(
          settingsControllerProvider.future,
        );
        expect(roundtripState.themeMode, equals(ThemeMode.dark));
        expect(roundtripState.locale, equals(const Locale('en')));
      },
    );

    test(
      'Negative/Boundary 1 (ISTQB BVA): fails fast with AppException(VALIDATION_FAILED) and logs error on corrupted persisted themeMode or unsupported locale boundaries',
      () async {
        const invalidThemeValues = <String>['', 'DARK', 'neon_invalid'];
        for (final invalidTheme in invalidThemeValues) {
          final corruptedPrefs = _StatefulFakeSharedPreferencesAsync(
            initialStore: {'app_theme_mode': invalidTheme, 'app_locale': 'fi'},
          );
          final container = createContainer(corruptedPrefs);

          await expectLater(
            container.read(settingsControllerProvider.future),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          container.dispose();
        }

        const invalidLocaleValues = <String>['', 'sv', 'de'];
        for (final invalidLocale in invalidLocaleValues) {
          final corruptedPrefs = _StatefulFakeSharedPreferencesAsync(
            initialStore: {
              'app_theme_mode': 'light',
              'app_locale': invalidLocale,
            },
          );
          final container = createContainer(corruptedPrefs);

          await expectLater(
            container.read(settingsControllerProvider.future),
            throwsA(
              isA<AppException>().having(
                (e) => e.errorCode,
                'errorCode',
                equals('VALIDATION_FAILED'),
              ),
            ),
          );
          container.dispose();
        }

        // Also verify runtime updateLocale rejects unsupported locale codes before mutating state or storage
        final validContainer = createContainer(fakePrefs);
        addTearDown(validContainer.dispose);
        await validContainer.read(settingsControllerProvider.future);

        await expectLater(
          validContainer
              .read(settingsControllerProvider.notifier)
              .updateLocale(const Locale('sv')),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
        expect(
          validContainer.read(settingsControllerProvider).value?.locale,
          equals(const Locale('fi', '')),
        );
        expect(fakePrefs.snapshot.containsKey('app_locale'), isFalse);

        verify(
          () => mockLogger.error(
            'SettingsController',
            any(that: contains('SETTINGS_INVALID_')),
            any(),
            any(),
          ),
        ).called(invalidThemeValues.length + invalidLocaleValues.length + 1);
      },
    );

    test(
      'Negative/Boundary 2: rolls back optimistic state to prior AsyncData, logs via LoggerService, and rethrows when storage persistence fails',
      () async {
        var failWrites = false;
        final faultInjectablePrefs = _StatefulFakeSharedPreferencesAsync(
          shouldFailWrite: () => failWrites,
        );
        final container = createContainer(faultInjectablePrefs);
        addTearDown(container.dispose);

        final AppSettingsState initial = await container.read(
          settingsControllerProvider.future,
        );
        expect(initial.themeMode, equals(ThemeMode.system));
        expect(initial.locale, equals(const Locale('fi', '')));

        failWrites = true;
        final notifier = container.read(settingsControllerProvider.notifier);

        await expectLater(
          notifier.updateThemeMode(ThemeMode.light),
          throwsA(isA<StateError>()),
        );

        final stateAfterThemeFailure = container.read(
          settingsControllerProvider,
        );
        expect(stateAfterThemeFailure.hasValue, isTrue);
        expect(stateAfterThemeFailure.hasError, isFalse);
        expect(
          stateAfterThemeFailure.value?.themeMode,
          equals(ThemeMode.system),
        );

        await expectLater(
          notifier.updateLocale(const Locale('en')),
          throwsA(isA<StateError>()),
        );

        final stateAfterLocaleFailure = container.read(
          settingsControllerProvider,
        );
        expect(stateAfterLocaleFailure.hasValue, isTrue);
        expect(stateAfterLocaleFailure.hasError, isFalse);
        expect(
          stateAfterLocaleFailure.value?.locale,
          equals(const Locale('fi', '')),
        );

        verify(
          () => mockLogger.error(
            'SettingsController',
            'Failed to update theme mode',
            any(),
            any(),
          ),
        ).called(1);
        verify(
          () => mockLogger.error(
            'SettingsController',
            'Failed to update locale',
            any(),
            any(),
          ),
        ).called(1);
      },
    );
  });
}
