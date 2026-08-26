import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/riverpod.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';

// Mock controller to intercept saveProfile and prevent API calls
class MockOutputProfilesController extends OutputProfilesController {
  @override
  Future<OutputProfile> saveProfile(String id, OutputProfile payload) async {
    // Just return the payload without making network calls
    return payload;
  }
}

void main() {
  group('OutputProfileForm Sanitization Tests', () {
    test(
      'submit sanitizes empty I18nText fields across all optional properties',
      () async {
        final container = ProviderContainer(
          overrides: [
            outputProfilesControllerProvider.overrideWith(
              () => MockOutputProfilesController(),
            ),
          ],
        );

        final emptyI18n = const I18nText(translations: {'en': ''});
        final profile = OutputProfile(
          id: 'test_id',
          workflowId: 'wf_1',
          name: const I18nText(translations: {'en': 'Valid Name'}),
          description: emptyI18n,
          userRoleLabel: emptyI18n,
          customPreface: emptyI18n,
          toneInstruction: emptyI18n,
          maxExtensionItems: 3,
          displayScale: DisplayScale.original,
          extensionLabels: {'ext1': emptyI18n},
          synthesis: SynthesisConfigDTO(
            preambleText: emptyI18n,
            toneInstruction: emptyI18n,
          ),
          layouts: [
            OutputLayoutBlock(
              title: emptyI18n,
              description: emptyI18n,
              presetView: PresetView.defaultView,
              textDeliveryMode: TextDeliveryMode.full,
              matrixColumnLabels: {'col1': emptyI18n},
            ),
          ],
        );

        final formProvider = outputProfileFormProvider('test_id');
        final formNotifier = container.read(formProvider.notifier);

        await formNotifier.submit(profile);
        final sanitized = formNotifier.state.value!;
        expect(
          sanitized.description,
          isNull,
          reason: 'description should be sanitized',
        );
        expect(
          sanitized.userRoleLabel,
          isNull,
          reason: 'userRoleLabel should be sanitized',
        );
        expect(
          sanitized.customPreface,
          isNull,
          reason: 'customPreface should be sanitized',
        );
        expect(
          sanitized.toneInstruction,
          isNull,
          reason: 'toneInstruction should be sanitized',
        );
        expect(
          sanitized.extensionLabels,
          isEmpty,
          reason: 'profile.extensionLabels should be sanitized to empty map',
        );
        expect(
          sanitized.synthesis?.preambleText,
          isNull,
          reason: 'profile.synthesis.preambleText should be sanitized',
        );
        expect(
          sanitized.synthesis?.toneInstruction,
          isNull,
          reason: 'profile.synthesis.toneInstruction should be sanitized',
        );
        expect(
          sanitized.maxExtensionItems,
          3,
          reason: 'maxExtensionItems should be preserved as 3',
        );
        expect(
          sanitized.displayScale,
          DisplayScale.original,
          reason: 'displayScale should be preserved as original',
        );

        final layout = sanitized.layouts.first;
        expect(
          layout.title,
          isNull,
          reason: 'layout.title should be sanitized',
        );
        expect(
          layout.description,
          isNull,
          reason: 'layout.description should be sanitized',
        );
        expect(
          layout.matrixColumnLabels,
          isEmpty,
          reason: 'layout.matrixColumnLabels should be sanitized to empty map',
        );
      },
    );

    group('Custom Scale Validation Partition Tests', () {
      test(
        'Negative Partition 1: submit sets AppException state when displayScale is custom but customScaleMin or customScaleMax is null',
        () async {
          final container = ProviderContainer(
            overrides: [
              outputProfilesControllerProvider.overrideWith(
                () => MockOutputProfilesController(),
              ),
            ],
          );

          final profileMissingBounds = OutputProfile(
            id: 'test_id',
            workflowId: 'wf_1',
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: null,
            customScaleMax: null,
          );

          final formProvider = outputProfileFormProvider('test_id');
          final formNotifier = container.read(formProvider.notifier);

          await formNotifier.submit(profileMissingBounds);

          final state = container.read(formProvider);
          expect(state.hasError, isTrue);
          expect(
            state.error,
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Custom Scale Min and Custom Scale Max are required'),
            ),
          );
        },
      );

      test(
        'Negative Partition 2: submit sets AppException state when customScaleMax is less than customScaleMin (inverted)',
        () async {
          final container = ProviderContainer(
            overrides: [
              outputProfilesControllerProvider.overrideWith(
                () => MockOutputProfilesController(),
              ),
            ],
          );

          final profileInvertedBounds = OutputProfile(
            id: 'test_id',
            workflowId: 'wf_1',
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: 10.0,
            customScaleMax: 4.0,
          );

          final formProvider = outputProfileFormProvider('test_id');
          final formNotifier = container.read(formProvider.notifier);

          await formNotifier.submit(profileInvertedBounds);

          final state = container.read(formProvider);
          expect(state.hasError, isTrue);
          expect(
            state.error,
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Custom Scale Max must be strictly greater'),
            ),
          );
        },
      );

      test(
        'Negative Partition 3: submit sets AppException state when customScaleMax is equal to customScaleMin',
        () async {
          final container = ProviderContainer(
            overrides: [
              outputProfilesControllerProvider.overrideWith(
                () => MockOutputProfilesController(),
              ),
            ],
          );

          final profileEqualBounds = OutputProfile(
            id: 'test_id',
            workflowId: 'wf_1',
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: 5.0,
            customScaleMax: 5.0,
          );

          final formProvider = outputProfileFormProvider('test_id');
          final formNotifier = container.read(formProvider.notifier);

          await formNotifier.submit(profileEqualBounds);

          final state = container.read(formProvider);
          expect(state.hasError, isTrue);
          expect(
            state.error,
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Custom Scale Max must be strictly greater'),
            ),
          );
        },
      );

      test(
        'Positive Partition: submit succeeds when customScaleMin and customScaleMax are valid and max > min',
        () async {
          final container = ProviderContainer(
            overrides: [
              outputProfilesControllerProvider.overrideWith(
                () => MockOutputProfilesController(),
              ),
            ],
          );

          final validCustomProfile = OutputProfile(
            id: 'test_id',
            workflowId: 'wf_1',
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: 4.0,
            customScaleMax: 10.0,
          );

          final formProvider = outputProfileFormProvider('test_id');
          final formNotifier = container.read(formProvider.notifier);

          await formNotifier.submit(validCustomProfile);

          final state = container.read(formProvider);
          expect(state.hasError, isFalse);
          expect(state.value?.customScaleMin, 4.0);
          expect(state.value?.customScaleMax, 10.0);
        },
      );
    });
  });
}
