import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/riverpod.dart';

class MockOutputProfilesController extends OutputProfilesController {
  @override
  Future<OutputProfile> saveProfile(String id, OutputProfile payload) async {
    return payload;
  }
}

class MockOutputProfilesFailingController extends OutputProfilesController {
  @override
  Future<OutputProfile> saveProfile(String id, OutputProfile payload) async {
    throw AppException.validation('Server validation failed');
  }
}

void main() {
  final validProfileId = generateOpaqueUuid7('prf');
  final validWorkflowId = generateOpaqueUuid7('wkf');

  group('OutputProfileForm Sanitization Tests', () {
    test(
      'submit sanitizes empty I18nText fields across all optional properties',
      () async {
        final container = ProviderContainer(
          overrides: [
            outputProfilesControllerProvider.overrideWith(
              MockOutputProfilesController.new,
            ),
          ],
        );
        addTearDown(container.dispose);

        const emptyI18n = I18nText(translations: {'en': ''});
        final profile = OutputProfile(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: validProfileId,
          workflowId: validWorkflowId,
          name: const I18nText(translations: {'en': 'Valid Name'}),
          description: emptyI18n,
          userRoleLabel: emptyI18n,
          customPreface: emptyI18n,
          toneInstruction: '',
          maxExtensionItems: 3,
          displayScale: DisplayScale.original,
          matrixSynthesisGroups: const [],
        );

        final formProvider = outputProfileFormProvider(validProfileId);
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
          sanitized.maxExtensionItems,
          3,
          reason: 'maxExtensionItems should be preserved as 3',
        );
        expect(
          sanitized.displayScale,
          DisplayScale.original,
          reason: 'displayScale should be preserved as original',
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
                MockOutputProfilesController.new,
              ),
            ],
          );
          addTearDown(container.dispose);

          final profileMissingBounds = OutputProfile(
            organizationId: 'org_0195f3a0000070008000000000000001',
            id: validProfileId,
            workflowId: validWorkflowId,
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: null,
            customScaleMax: null,
          );

          final formProvider = outputProfileFormProvider(validProfileId);
          final formNotifier = container.read(formProvider.notifier);

          await expectLater(
            formNotifier.submit(profileMissingBounds),
            throwsA(
              isA<AppException>().having(
                (e) => e.detail,
                'detail',
                contains('Custom Scale Min and Custom Scale Max are required'),
              ),
            ),
          );

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
                MockOutputProfilesController.new,
              ),
            ],
          );
          addTearDown(container.dispose);

          final profileInvertedBounds = OutputProfile(
            organizationId: 'org_0195f3a0000070008000000000000001',
            id: validProfileId,
            workflowId: validWorkflowId,
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: 10.0,
            customScaleMax: 4.0,
          );

          final formProvider = outputProfileFormProvider(validProfileId);
          final formNotifier = container.read(formProvider.notifier);

          await expectLater(
            formNotifier.submit(profileInvertedBounds),
            throwsA(
              isA<AppException>().having(
                (e) => e.detail,
                'detail',
                contains('Custom Scale Max must be strictly greater'),
              ),
            ),
          );

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
                MockOutputProfilesController.new,
              ),
            ],
          );
          addTearDown(container.dispose);

          final profileEqualBounds = OutputProfile(
            organizationId: 'org_0195f3a0000070008000000000000001',
            id: validProfileId,
            workflowId: validWorkflowId,
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: 5.0,
            customScaleMax: 5.0,
          );

          final formProvider = outputProfileFormProvider(validProfileId);
          final formNotifier = container.read(formProvider.notifier);

          await expectLater(
            formNotifier.submit(profileEqualBounds),
            throwsA(
              isA<AppException>().having(
                (e) => e.detail,
                'detail',
                contains('Custom Scale Max must be strictly greater'),
              ),
            ),
          );

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
                MockOutputProfilesController.new,
              ),
            ],
          );
          addTearDown(container.dispose);

          final validCustomProfile = OutputProfile(
            organizationId: 'org_0195f3a0000070008000000000000001',
            id: validProfileId,
            workflowId: validWorkflowId,
            name: const I18nText(translations: {'en': 'Valid Name'}),
            displayScale: DisplayScale.custom,
            customScaleMin: 4.0,
            customScaleMax: 10.0,
          );

          final formProvider = outputProfileFormProvider(validProfileId);
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

  group('OutputProfilesController Unit Tests', () {
    test(
      'SelectedOutputProfileConfigSection selects and updates target section',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);
        final provider = selectedOutputProfileConfigSectionProvider(
          validProfileId,
        );

        expect(container.read(provider), isNull);

        container.read(provider.notifier).select(TargetBlockType.metadataBlock);
        expect(container.read(provider), TargetBlockType.metadataBlock);

        container.read(provider.notifier).select(null);
        expect(container.read(provider), isNull);
      },
    );

    test(
      'OutputProfileForm submit throws validation error when ID is empty or new',
      () async {
        final container = ProviderContainer(
          overrides: [
            outputProfilesControllerProvider.overrideWith(
              MockOutputProfilesController.new,
            ),
          ],
        );
        addTearDown(container.dispose);

        final invalidProfile = OutputProfile(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: '',
          workflowId: validWorkflowId,
          name: const I18nText(translations: {'en': 'Test'}),
        );

        final formProvider = outputProfileFormProvider('');
        final formNotifier = container.read(formProvider.notifier);

        await expectLater(
          formNotifier.submit(invalidProfile),
          throwsA(isA<AppException>()),
        );

        final state = container.read(formProvider);
        expect(state.hasError, isTrue);
        expect(state.error, isA<AppException>());
      },
    );

    test(
      'OutputProfileForm submit throws validation error when name is empty',
      () async {
        final container = ProviderContainer(
          overrides: [
            outputProfilesControllerProvider.overrideWith(
              MockOutputProfilesController.new,
            ),
          ],
        );
        addTearDown(container.dispose);

        final noNameProfile = OutputProfile(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: validProfileId,
          workflowId: validWorkflowId,
          name: const I18nText(translations: {}),
        );

        final formProvider = outputProfileFormProvider(validProfileId);
        final formNotifier = container.read(formProvider.notifier);

        await expectLater(
          formNotifier.submit(noNameProfile),
          throwsA(isA<AppException>()),
        );

        final state = container.read(formProvider);
        expect(state.hasError, isTrue);
        expect(state.error, isA<AppException>());
      },
    );

    test(
      'OutputProfileForm submit rethrows server AppException when saveProfile fails',
      () async {
        final container = ProviderContainer(
          overrides: [
            outputProfilesControllerProvider.overrideWith(
              MockOutputProfilesFailingController.new,
            ),
          ],
        );
        addTearDown(container.dispose);

        final validProfile = OutputProfile(
          organizationId: 'org_0195f3a0000070008000000000000001',
          id: validProfileId,
          workflowId: validWorkflowId,
          name: const I18nText(translations: {'en': 'Test'}),
        );

        final formProvider = outputProfileFormProvider(validProfileId);
        final formNotifier = container.read(formProvider.notifier);

        await expectLater(
          formNotifier.submit(validProfile),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Server validation failed'),
            ),
          ),
        );

        final state = container.read(formProvider);
        expect(state.hasError, isTrue);
        expect(state.error, isA<AppException>());
      },
    );
  });
}
