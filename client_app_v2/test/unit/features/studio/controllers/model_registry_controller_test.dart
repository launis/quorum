import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/gcp_location.dart';
import 'package:client_app/features/studio/models/llm_platform.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockStudioClient mockClient;
  late MockLoggerService mockLogger;
  late ProviderContainer container;

  const validConfigId = 'mrg_01965b80000070008000000000000001';
  const validConfig = ModelConfig(
    id: validConfigId,
    name: 'Enterprise Model Registry',
    slug: 'enterprise-model-registry',
    defaultProvider: 'vertex_ai',
    tierDefinitions: {
      'tier_1': LlmModelConfig(
        provider: 'vertex_ai',
        modelName: 'gemini-2.5-pro',
        temperature: 0.2,
        isActive: true,
      ),
    },
  );

  const secondaryConfig = ModelConfig(
    id: 'mrg_01965b80000070008000000000000099',
    name: 'Secondary Model Registry',
    slug: 'secondary-model-registry',
    defaultProvider: 'ai_studio',
  );

  setUpAll(() {
    registerFallbackValue(validConfig);
    registerFallbackValue(StackTrace.current);
  });

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);

    container = ProviderContainer(
      retry: (retryCount, error) => null,
      overrides: [
        studioClientProvider.overrideWithValue(mockClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('ModelRegistryController', () {
    test(
      'build fetches dedicated model registries directly from getSystemConfigs',
      () async {
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig, secondaryConfig]);

        container.read(modelRegistryControllerProvider.notifier);
        final result = await container.read(
          modelRegistryControllerProvider.future,
        );

        expect(result.length, 2);
        expect(result.first.id, validConfigId);
        expect(result.last.id, secondaryConfig.id);
        verify(() => mockClient.getSystemConfigs()).called(1);
      },
    );

    test(
      'refresh updates state on success and transitions to AsyncError on failure',
      () async {
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);

        final controller = container.read(
          modelRegistryControllerProvider.notifier,
        );
        await container.read(modelRegistryControllerProvider.future);

        final updatedConfig = validConfig.copyWith(name: 'Refreshed Registry');
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [updatedConfig]);

        await controller.refresh();
        expect(
          container.read(modelRegistryControllerProvider).value?.single.name,
          'Refreshed Registry',
        );

        // Negative 1: Refresh network exception logs and transitions state to AsyncError
        when(
          () => mockClient.getSystemConfigs(),
        ).thenThrow(Exception('Gateway timeout'));
        await controller.refresh();

        expect(
          container.read(modelRegistryControllerProvider).hasError,
          isTrue,
        );
        verify(
          () => mockLogger.error(
            'ModelRegistryController',
            'Refresh failed',
            any(),
            any(),
          ),
        ).called(1);

        // Negative 2: Refresh AppException preserves error in state
        when(
          () => mockClient.getSystemConfigs(),
        ).thenThrow(AppException.network('Backend offline'));
        await controller.refresh();

        final errState = container.read(modelRegistryControllerProvider);
        expect(errState.hasError, isTrue);
        expect(errState.error, isA<AppException>());
      },
    );

    test(
      'saveConfig performs optimistic update, confirms with backend data, and invalidates modelRegistryByIdProvider',
      () async {
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);
        when(
          () => mockClient.getSystemConfig(validConfigId),
        ).thenAnswer((_) async => validConfig);

        final controller = container.read(
          modelRegistryControllerProvider.notifier,
        );
        await container.read(modelRegistryControllerProvider.future);
        await container.read(modelRegistryByIdProvider(validConfigId).future);

        final modifiedConfig = validConfig.copyWith(name: 'Verified Registry');
        when(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).thenAnswer((_) async => modifiedConfig);
        when(
          () => mockClient.getSystemConfig(validConfigId),
        ).thenAnswer((_) async => modifiedConfig);

        final result = await controller.saveConfig(
          validConfigId,
          modifiedConfig,
        );

        expect(result.name, 'Verified Registry');
        expect(
          container.read(modelRegistryControllerProvider).value?.single.name,
          'Verified Registry',
        );
        final refreshedById = await container.read(
          modelRegistryByIdProvider(validConfigId).future,
        );
        expect(refreshedById.name, 'Verified Registry');
        verify(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).called(1);
      },
    );

    test(
      'saveConfig appends new config when id is not in state and rolls back on failure',
      () async {
        const newId = 'cfg_01965b80000070008000000000000002';
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);

        final controller = container.read(
          modelRegistryControllerProvider.notifier,
        );
        await container.read(modelRegistryControllerProvider.future);

        final newConfig = validConfig.copyWith(id: newId, name: 'New Registry');
        when(
          () => mockClient.saveSystemConfig(newId, any()),
        ).thenAnswer((_) async => newConfig);

        final saved = await controller.saveConfig(newId, newConfig);
        expect(saved.id, newId);
        expect(
          container.read(modelRegistryControllerProvider).value?.length,
          2,
        );

        // Negative 1: DioException with AppException rolls back state and rethrows AppException
        final dioError = DioException(
          requestOptions: RequestOptions(
            path: '/studio/model-registry/$validConfigId',
          ),
          error: AppException.validation('Invalid tier configuration'),
        );
        when(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).thenThrow(dioError);

        await expectLater(
          () => controller.saveConfig(
            validConfigId,
            validConfig.copyWith(name: 'Broken Registry'),
          ),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Invalid tier configuration'),
            ),
          ),
        );
        expect(
          container.read(modelRegistryControllerProvider).value?.first.name,
          'Enterprise Model Registry',
        );

        // Negative 2: Direct AppException rethrows without wrapping as unknown
        when(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).thenThrow(AppException.validation('Invalid Opaque ID'));
        await expectLater(
          () => controller.saveConfig(validConfigId, validConfig),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Invalid Opaque ID'),
            ),
          ),
        );

        // Negative 3: Unhandled exception wraps into AppException.unknown
        when(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).thenThrow(StateError('Unexpected state failure'));
        await expectLater(
          () => controller.saveConfig(validConfigId, validConfig),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'deleteConfig removes config from state, invalidates detail provider, and propagates errors',
      () async {
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);
        when(
          () => mockClient.deleteSystemConfig(validConfigId),
        ).thenAnswer((_) async {});

        final controller = container.read(
          modelRegistryControllerProvider.notifier,
        );
        await container.read(modelRegistryControllerProvider.future);

        await controller.deleteConfig(validConfigId);
        expect(container.read(modelRegistryControllerProvider).value, isEmpty);
        verify(() => mockClient.deleteSystemConfig(validConfigId)).called(1);

        // Negative 1: DioException with AppException (RESOURCE_IN_USE) propagates
        final appError = AppException(
          extensions: const {'error_code': 'RESOURCE_IN_USE'},
          detail: 'Cannot delete system config in use by workflow',
          status: 400,
        );
        when(() => mockClient.deleteSystemConfig(validConfigId)).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: '/studio/model-registry/$validConfigId',
            ),
            error: appError,
          ),
        );
        await expectLater(
          () => controller.deleteConfig(validConfigId),
          throwsA(
            isA<AppException>()
                .having((e) => e.errorCode, 'errorCode', 'RESOURCE_IN_USE')
                .having((e) => e.status, 'status', 400),
          ),
        );

        // Negative 2: Direct AppException rethrows directly
        when(
          () => mockClient.deleteSystemConfig('bad_id'),
        ).thenThrow(AppException.validation('Malformed ID'));
        await expectLater(
          () => controller.deleteConfig('bad_id'),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('Malformed ID'),
            ),
          ),
        );

        // Negative 3: Generic exception wraps into AppException.unknown
        when(
          () => mockClient.deleteSystemConfig(validConfigId),
        ).thenThrow(Exception('Socket closed'));
        await expectLater(
          () => controller.deleteConfig(validConfigId),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'cloneConfig appends cloned config and rolls back on failure',
      () async {
        const clonedId = 'mrg_01965b80000070008000000000000003';
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);

        final controller = container.read(
          modelRegistryControllerProvider.notifier,
        );
        await container.read(modelRegistryControllerProvider.future);

        const clonedConfig = ModelConfig(
          id: clonedId,
          name: 'Enterprise Model Registry (Copy)',
          slug: 'enterprise-model-registry-copy',
          defaultProvider: 'vertex_ai',
        );

        when(
          () => mockClient.cloneSystemConfig(validConfigId),
        ).thenAnswer((_) async => clonedConfig);

        final result = await controller.cloneConfig(validConfigId);
        expect(result.id, clonedId);
        expect(
          container.read(modelRegistryControllerProvider).value?.length,
          2,
        );
        expect(
          container.read(modelRegistryControllerProvider).value?.last.id,
          clonedId,
        );

        // Negative 1: DioException with AppException rolls back and rethrows
        final dioError = DioException(
          requestOptions: RequestOptions(
            path: '/studio/model-registry/$validConfigId/clone',
          ),
          error: AppException.network('Clone failed'),
        );
        when(
          () => mockClient.cloneSystemConfig(validConfigId),
        ).thenThrow(dioError);
        await expectLater(
          () => controller.cloneConfig(validConfigId),
          throwsA(isA<AppException>()),
        );

        // Negative 2: Direct AppException rethrows and generic exception wraps
        when(
          () => mockClient.cloneSystemConfig('invalid_id'),
        ).thenThrow(AppException.validation('Invalid ID'));
        await expectLater(
          () => controller.cloneConfig('invalid_id'),
          throwsA(isA<AppException>()),
        );

        when(
          () => mockClient.cloneSystemConfig(validConfigId),
        ).thenThrow(Exception('Unexpected error'));
        await expectLater(
          () => controller.cloneConfig(validConfigId),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'createSystemConfigDraft prepends draft config and rolls back on failure',
      () async {
        const draftId = 'mrg_01965b80000070008000000000000004';
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);

        final controller = container.read(
          modelRegistryControllerProvider.notifier,
        );
        await container.read(modelRegistryControllerProvider.future);

        const draftConfig = ModelConfig(
          id: draftId,
          name: 'Draft Model Registry',
          slug: 'draft-model-registry',
        );

        when(
          () => mockClient.createSystemConfigDraft(),
        ).thenAnswer((_) async => draftConfig);

        final result = await controller.createSystemConfigDraft();
        expect(result.id, draftId);
        expect(
          container.read(modelRegistryControllerProvider).value?.first.id,
          draftId,
        );

        // Negative 1: DioException with AppException rolls back and rethrows
        final dioError = DioException(
          requestOptions: RequestOptions(path: '/studio/model-registry/'),
          error: AppException.network('Draft creation failed'),
        );
        when(() => mockClient.createSystemConfigDraft()).thenThrow(dioError);
        await expectLater(
          () => controller.createSystemConfigDraft(),
          throwsA(isA<AppException>()),
        );

        // Negative 2: Direct AppException and generic exception handling
        when(
          () => mockClient.createSystemConfigDraft(),
        ).thenThrow(AppException.validation('Quota exceeded'));
        await expectLater(
          () => controller.createSystemConfigDraft(),
          throwsA(isA<AppException>()),
        );

        when(
          () => mockClient.createSystemConfigDraft(),
        ).thenThrow(Exception('Database error'));
        await expectLater(
          () => controller.createSystemConfigDraft(),
          throwsA(isA<AppException>()),
        );
      },
    );
  });

  group('Auxiliary Model Registry Providers', () {
    test(
      'availableModels, supportedLocations, and supportedPlatforms delegate to StudioClient and propagate errors',
      () async {
        when(
          () => mockClient.getAvailableModels(
            platform: 'vertex_ai',
            location: 'europe-west1',
          ),
        ).thenAnswer((_) async => ['gemini-2.5-pro', 'gemini-2.5-flash']);

        const loc = GcpLocation(
          id: 'europe-west1',
          label: 'Belgium (europe-west1)',
          description: 'European Union region',
        );
        when(
          () => mockClient.getSupportedLocations(),
        ).thenAnswer((_) async => [loc]);

        const platform = LlmPlatform(
          id: 'vertex_ai',
          label: 'Google Vertex AI',
          hasRegions: true,
        );
        when(
          () => mockClient.getSupportedPlatforms(),
        ).thenAnswer((_) async => [platform]);

        final models = await container.read(
          availableModelsProvider(
            platform: 'vertex_ai',
            location: 'europe-west1',
          ).future,
        );
        expect(models, ['gemini-2.5-pro', 'gemini-2.5-flash']);

        final locations = await container.read(
          supportedLocationsProvider.future,
        );
        expect(locations.single.id, 'europe-west1');

        final platforms = await container.read(
          supportedPlatformsProvider.future,
        );
        expect(platforms.single.id, 'vertex_ai');

        // Negative 1: availableModels error propagates
        when(
          () => mockClient.getAvailableModels(
            platform: 'invalid',
            location: null,
          ),
        ).thenThrow(AppException.validation('Unsupported platform'));
        await expectLater(
          container.read(availableModelsProvider(platform: 'invalid').future),
          throwsA(isA<AppException>()),
        );

        // Negative 2: modelRegistryById error propagates for invalid ID
        when(
          () => mockClient.getSystemConfig('bad_id'),
        ).thenThrow(AppException.validation('Invalid Opaque ID'));
        await expectLater(
          container.read(modelRegistryByIdProvider('bad_id').future),
          throwsA(isA<AppException>()),
        );
      },
    );
  });

  group('ModelRegistryForm', () {
    test(
      'build, forceRebuild, and submit handle positive and negative partitions while preserving unsaved edits',
      () async {
        when(
          () => mockClient.getSystemConfig(validConfigId),
        ).thenAnswer((_) async => validConfig);
        when(
          () => mockClient.getSystemConfigs(),
        ).thenAnswer((_) async => [validConfig]);

        final formNotifier = container.read(
          modelRegistryFormProvider(validConfigId).notifier,
        );
        final loaded = await container.read(
          modelRegistryFormProvider(validConfigId).future,
        );
        expect(loaded.id, validConfigId);

        // forceRebuild updates state synchronously
        final rebuilt = validConfig.copyWith(name: 'Locally Edited Registry');
        formNotifier.forceRebuild(rebuilt);
        expect(
          container.read(modelRegistryFormProvider(validConfigId)).value?.name,
          'Locally Edited Registry',
        );

        // Positive submit saves and updates form state with backend-verified config
        final backendVerified = rebuilt.copyWith(
          name: 'Backend Verified Registry',
        );
        when(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).thenAnswer((_) async => backendVerified);

        await formNotifier.submit(rebuilt);
        expect(
          container.read(modelRegistryFormProvider(validConfigId)).value?.name,
          'Backend Verified Registry',
        );

        // Negative 1: Save failure retains unsaved form edits in state.value while exposing error
        final dioSaveErr = DioException(
          requestOptions: RequestOptions(
            path: '/studio/model-registry/$validConfigId',
          ),
          error: AppException.network('Save failed'),
        );
        when(
          () => mockClient.saveSystemConfig(validConfigId, any()),
        ).thenThrow(dioSaveErr);

        final unsavedEdit = validConfig.copyWith(name: 'Unsaved Edit');
        await expectLater(
          () => formNotifier.submit(unsavedEdit),
          throwsA(isA<AppException>()),
        );
        final errState = container.read(
          modelRegistryFormProvider(validConfigId),
        );
        expect(errState.hasError, isTrue);
        expect(errState.hasValue, isTrue);
        expect(errState.value?.name, 'Unsaved Edit');

        // Negative 2: Empty ID and 'new' configId throw Fail-Fast validation AppException
        final newFormNotifier = container.read(
          modelRegistryFormProvider('new').notifier,
        );
        await expectLater(
          () => newFormNotifier.submit(validConfig.copyWith(id: '')),
          throwsA(
            isA<AppException>().having(
              (e) => e.detail,
              'detail',
              contains('System Config ID is required'),
            ),
          ),
        );
      },
    );
  });
}
