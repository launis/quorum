import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/error/app_exception.dart';

void main() {
  group('Workflow Title Resolution Regression Tests', () {
    test(
      'proves that legacy default_locale indexing fails on modern I18nText JSON',
      () {
        final Map<String, dynamic> rawWorkflow = {
          'id': 'wf_9d68c573802341db',
          'name': {
            'translations': {
              'fi': 'Kokonaisvaltainen Auditointi',
              'en': 'Holistic Audit',
            },
          },
        };

        final nameMapRaw = rawWorkflow['name'];
        final nameMap = nameMapRaw is Map ? nameMapRaw : {};

        // Legacy indexing:
        final buggyResolved =
            nameMap['translations']?[nameMap['default_locale']] ??
            nameMap['default_locale'];
        expect(
          buggyResolved,
          isNull,
          reason:
              'default_locale is no longer present in modern I18nText payloads',
        );

        // The buggy code executed `throw AppException.validation('Fail-Fast: Missing required translation.')`
        expect(
          () {
            if (buggyResolved == null) {
              throw AppException.validation(
                'Fail-Fast: Missing required translation.',
              );
            }
          },
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

    test(
      'verifies that I18nText.fromJson safely and strictly resolves modern workflow name',
      () {
        final Map<String, dynamic> rawWorkflow = {
          'id': 'wf_9d68c573802341db',
          'name': {
            'translations': {
              'fi': 'Kokonaisvaltainen Auditointi',
              'en': 'Holistic Audit',
            },
          },
        };

        final nameMapRaw = rawWorkflow['name'];
        final i18n = I18nText.fromJson(
          Map<String, dynamic>.from(nameMapRaw as Map),
        );

        // Localized resolution:
        expect(i18n.get('fi'), equals('Kokonaisvaltainen Auditointi'));
        expect(i18n.get('en'), equals('Holistic Audit'));
        // Fallback resolution for unsupported locales:
        expect(i18n.get('sv'), equals('Holistic Audit'));
      },
    );

    test(
      'verifies that I18nText throws AppException when translation is truly missing',
      () {
        final emptyMap = <String, dynamic>{'translations': <String, String>{}};
        final i18n = I18nText.fromJson(emptyMap);

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
  });
}
