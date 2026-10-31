import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:riverpod/riverpod.dart';

class _FakeStudioClient extends StudioClient {
  final List<OutputProfile> _store;
  bool shouldFailWithDioAppException = false;
  bool shouldFailWithGenericError = false;

  _FakeStudioClient(List<OutputProfile> initialProfiles)
    : _store = List<OutputProfile>.from(initialProfiles),
      super(Dio());

  Never _throwError(String path) {
    if (shouldFailWithDioAppException) {
      throw DioException(
        requestOptions: RequestOptions(path: path),
        error: AppException.validation('Backend validation rejected $path'),
      );
    }
    throw StateError('Simulated network error on $path');
  }

  @override
  Future<List<OutputProfile>> getOutputProfiles() async {
    if (shouldFailWithDioAppException || shouldFailWithGenericError) {
      _throwError('output-profiles/');
    }
    return List<OutputProfile>.from(_store);
  }

  @override
  Future<OutputProfile> getOutputProfile(String id) async {
    if (shouldFailWithDioAppException || shouldFailWithGenericError) {
      _throwError('output-profiles/$id');
    }
    return _store.firstWhere(
      (p) => p.id == id,
      orElse: () => throw AppException.validation('Profile not found: $id'),
    );
  }

  @override
  Future<OutputProfile> saveOutputProfile(String id, OutputProfile data) async {
    if (shouldFailWithDioAppException || shouldFailWithGenericError) {
      _throwError('output-profiles/$id');
    }
    final index = _store.indexWhere((p) => p.id == id);
    if (index >= 0) {
      _store[index] = data;
    } else {
      _store.add(data);
    }
    return data;
  }

  @override
  Future<void> deleteOutputProfile(String id) async {
    if (shouldFailWithDioAppException || shouldFailWithGenericError) {
      _throwError('output-profiles/$id');
    }
    _store.removeWhere((p) => p.id == id);
  }

  @override
  Future<OutputProfile> cloneOutputProfile(String id) async {
    if (shouldFailWithDioAppException || shouldFailWithGenericError) {
      _throwError('output-profiles/$id/clone');
    }
    final source = await getOutputProfile(id);
    final cloned = source.copyWith(id: generateOpaqueUuid7('prf'));
    _store.insert(0, cloned);
    return cloned;
  }

  @override
  Future<OutputProfile> createOutputProfileDraft() async {
    if (shouldFailWithDioAppException || shouldFailWithGenericError) {
      _throwError('output-profiles/');
    }
    final draft = OutputProfile(
      id: generateOpaqueUuid7('prf'),
      workflowId: generateOpaqueUuid7('wkf'),
      name: const I18nText(translations: {'en': 'Draft Profile'}),
    );
    _store.insert(0, draft);
    return draft;
  }
}

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

  OutputProfile buildValidProfile({
    String? id,
    String? workflowId,
    I18nText? name,
    DisplayScale displayScale = DisplayScale.original,
    double? customScaleMin,
    double? customScaleMax,
  }) {
    return OutputProfile(
      id: id ?? validProfileId,
      workflowId: workflowId ?? validWorkflowId,
      name: name ?? const I18nText(translations: {'en': 'Valid Name'}),
      displayScale: displayScale,
      customScaleMin: customScaleMin,
      customScaleMax: customScaleMax,
    );
  }

  group('OutputProfileForm Sanitization & State Tests', () {
    test(
      'build loads profile via isolate and supports forceRebuild and updatePayload',
      () async {
        final seeded = buildValidProfile();
        final fakeClient = _FakeStudioClient([seeded]);
        final container = ProviderContainer(
          overrides: [studioClientProvider.overrideWithValue(fakeClient)],
        );
        addTearDown(container.dispose);

        final formProvider = outputProfileFormProvider(validProfileId);
        final sub = container.listen(formProvider, (_, _) {});
        addTearDown(sub.close);

        final built = await container.read(formProvider.future);
        expect(built.id, validProfileId);

        final notifier = container.read(formProvider.notifier);
        notifier.forceRebuild();
        expect(container.read(formProvider).value?.id, validProfileId);

        final updated = seeded.copyWith(slug: 'updated-slug');
        notifier.updatePayload(updated);
        expect(container.read(formProvider).value?.slug, 'updated-slug');
      },
    );

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
        expect(sanitized.description, isNull);
        expect(sanitized.userRoleLabel, isNull);
        expect(sanitized.customPreface, isNull);
        expect(sanitized.toneInstruction, isNull);
        expect(sanitized.maxExtensionItems, 3);
        expect(sanitized.displayScale, DisplayScale.original);
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

          final profileMissingBounds = buildValidProfile(
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

          final profileInvertedBounds = buildValidProfile(
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
        },
      );

      test(
        'Negative Partition 3 (Boundary): submit sets AppException state when customScaleMax is equal to customScaleMin',
        () async {
          final container = ProviderContainer(
            overrides: [
              outputProfilesControllerProvider.overrideWith(
                MockOutputProfilesController.new,
              ),
            ],
          );
          addTearDown(container.dispose);

          final profileEqualBounds = buildValidProfile(
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

          final validCustomProfile = buildValidProfile(
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

  group('OutputProfilesController & Providers Unit Tests', () {
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
      'CRUD lifecycle: build, saveProfile, cloneProfile, createOutputProfileDraft, deleteProfile, and refresh succeed',
      () async {
        final initial = buildValidProfile();
        final fakeClient = _FakeStudioClient([initial]);
        final container = ProviderContainer(
          overrides: [studioClientProvider.overrideWithValue(fakeClient)],
        );
        addTearDown(container.dispose);

        final initialList = await container.read(
          outputProfilesControllerProvider.future,
        );
        expect(initialList.length, 1);

        final notifier = container.read(
          outputProfilesControllerProvider.notifier,
        );

        // Update existing profile
        final updated = initial.copyWith(slug: 'updated');
        final saved = await notifier.saveProfile(validProfileId, updated);
        expect(saved.slug, 'updated');
        expect(
          container.read(outputProfilesControllerProvider).value!.first.slug,
          'updated',
        );

        // Insert new profile via saveProfile
        final newId = generateOpaqueUuid7('prf');
        final added = buildValidProfile(id: newId);
        await notifier.saveProfile(newId, added);
        expect(
          container.read(outputProfilesControllerProvider).value!.length,
          2,
        );

        // Clone profile
        final cloned = await notifier.cloneProfile(validProfileId);
        expect(cloned.id, isNot(equals(validProfileId)));
        expect(
          container.read(outputProfilesControllerProvider).value!.first.id,
          cloned.id,
        );

        // Create draft
        final draft = await notifier.createOutputProfileDraft();
        expect(
          container.read(outputProfilesControllerProvider).value!.first.id,
          draft.id,
        );

        // Delete profile
        await notifier.deleteProfile(newId);
        expect(
          container
              .read(outputProfilesControllerProvider)
              .value!
              .any((p) => p.id == newId),
          isFalse,
        );

        // Refresh
        await notifier.refresh();
        expect(
          container.read(outputProfilesControllerProvider).hasValue,
          isTrue,
        );
      },
    );

    test(
      'Negative: saveProfile, cloneProfile, createOutputProfileDraft roll back state and rethrow AppException on failure',
      () async {
        final initial = buildValidProfile();
        final fakeClient = _FakeStudioClient([initial]);
        final container = ProviderContainer(
          overrides: [studioClientProvider.overrideWithValue(fakeClient)],
        );
        addTearDown(container.dispose);

        await container.read(outputProfilesControllerProvider.future);
        final notifier = container.read(
          outputProfilesControllerProvider.notifier,
        );

        fakeClient.shouldFailWithDioAppException = true;

        await expectLater(
          notifier.saveProfile(
            validProfileId,
            initial.copyWith(slug: 'failed-save'),
          ),
          throwsA(isA<AppException>()),
        );
        expect(
          container.read(outputProfilesControllerProvider).value!.first.slug,
          initial.slug,
        );

        await expectLater(
          notifier.cloneProfile(validProfileId),
          throwsA(isA<AppException>()),
        );
        expect(
          container.read(outputProfilesControllerProvider).value!.length,
          1,
        );

        await expectLater(
          notifier.createOutputProfileDraft(),
          throwsA(isA<AppException>()),
        );
        expect(
          container.read(outputProfilesControllerProvider).value!.length,
          1,
        );

        fakeClient.shouldFailWithDioAppException = false;
        fakeClient.shouldFailWithGenericError = true;

        await expectLater(
          notifier.deleteProfile(validProfileId),
          throwsA(isA<AppException>()),
        );

        await notifier.refresh();
        expect(
          container.read(outputProfilesControllerProvider).hasError,
          isTrue,
        );
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

        final invalidProfile = buildValidProfile(id: '');

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

        final noNameProfile = buildValidProfile(
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

        final validProfile = buildValidProfile();

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
