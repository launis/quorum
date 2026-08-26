import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/error/app_exception.dart';

void main() {
  group('I18nText Freezed Model Tests', () {
    // TC-I18N-FLUTTER-01: Target locale resolution
    test('TC-I18N-FLUTTER-01: resolves target locale directly', () {
      const i18n = I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'});
      expect(i18n.get('fi'), equals('Käyttäjä'));
      expect(i18n.get('fi-FI'), equals('Käyttäjä'));
    });

    // TC-I18N-FLUTTER-02: Fallback to en
    test(
      'TC-I18N-FLUTTER-02: falls back to en when target locale is unavailable',
      () {
        const i18n = I18nText(translations: {'fi': 'Käyttäjä', 'en': 'User'});
        expect(i18n.get('sv'), equals('User'));
      },
    );

    // TC-I18N-FLUTTER-03: Missing translation throws AppException
    test(
      'TC-I18N-FLUTTER-03: throws AppException.validation when neither target nor fallback exists',
      () {
        const i18n = I18nText(translations: {'de': 'Benutzer'});
        expect(
          () => i18n.get('fr', fallback: 'es'),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );

    // TC-I18N-FLUTTER-04: Whitespace-only translation throws AppException
    test(
      'TC-I18N-FLUTTER-04: throws AppException.validation on whitespace-only translation',
      () {
        const i18n = I18nText(translations: {'fi': '   ', 'en': ''});
        expect(
          () => i18n.get('fi'),
          throwsA(
            isA<AppException>().having(
              (e) => e.errorCode,
              'errorCode',
              equals('VALIDATION_FAILED'),
            ),
          ),
        );
      },
    );

    // TC-I18N-FLUTTER-05: isEmpty, isNotEmpty, has helpers
    test(
      'TC-I18N-FLUTTER-05: verifies isEmpty, isNotEmpty, and has helpers',
      () {
        const emptyI18n = I18nText(translations: {'en': '   '});
        expect(emptyI18n.isEmpty, isTrue);
        expect(emptyI18n.isNotEmpty, isFalse);
        expect(emptyI18n.has('en'), isFalse);

        const populatedI18n = I18nText(
          translations: {'en': 'User', 'fi': 'Käyttäjä'},
        );
        expect(populatedI18n.isEmpty, isFalse);
        expect(populatedI18n.isNotEmpty, isTrue);
        expect(populatedI18n.has('en'), isTrue);
        expect(populatedI18n.has('fi'), isTrue);
        expect(populatedI18n.has('sv'), isFalse);
        expect(populatedI18n.has(null), isFalse);
      },
    );

    // TC-I18N-FLUTTER-06: fromJson throws on legacy default_locale
    test(
      'TC-I18N-FLUTTER-06: fromJson rejects legacy default_locale (disallowUnrecognizedKeys)',
      () {
        const legacyJsonStr =
            '{"default_locale": "en", "translations": {"en": "Text"}}';
        final dynamic rawJson = jsonDecode(legacyJsonStr);
        expect(
          () => I18nText.fromJson(rawJson as Map<String, dynamic>),
          throwsA(isA<Exception>()),
        );
      },
    );

    // TC-I18N-FLUTTER-07: fromJson throws on missing translations
    test(
      'TC-I18N-FLUTTER-07: fromJson rejects missing or null translations',
      () {
        expect(
          () => I18nText.fromJson(<String, dynamic>{}),
          throwsA(isA<Exception>()),
        );
        expect(
          () => I18nText.fromJson(<String, dynamic>{'translations': null}),
          throwsA(isA<Exception>()),
        );
      },
    );
  });
}
