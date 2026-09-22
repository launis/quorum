import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/shared/models/i18n_text.dart';
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

  const validTool = AllowedMcpTool(
    toolId: 'test_tool',
    name: I18nText(translations: {'en': 'Test Tool'}),
    description: 'A test tool',
  );

  const validGateway = McpGateway(
    id: 'mcp_0123456789abcdef',
    type: 'mcp_gateways',
    slug: 'default-mcp',
    tools: [validTool],
  );

  setUpAll(() {
    registerFallbackValue(validGateway);
    registerFallbackValue(StackTrace.current);
  });

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    container = ProviderContainer(
      overrides: [
        studioClientProvider.overrideWithValue(mockClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('McpGatewaysController', () {
    test('build fetches gateways from StudioClient', () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      final result = await container.read(mcpGatewaysControllerProvider.future);

      expect(result.length, 1);
      expect(result.first.id, 'mcp_0123456789abcdef');
      verify(() => mockClient.getMcpGateways()).called(1);
    });

    test('refresh updates state on success and logs on failure', () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      await container.read(mcpGatewaysControllerProvider.future);

      // Successful refresh
      final updatedGateway = validGateway.copyWith(slug: 'updated-slug');
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [updatedGateway]);

      await controller.refresh();
      expect(container.read(mcpGatewaysControllerProvider).value?.first.slug,
          'updated-slug');

      // Negative: refresh failure logs error
      when(() => mockClient.getMcpGateways())
          .thenThrow(Exception('Network timeout'));
      await controller.refresh();

      expect(container.read(mcpGatewaysControllerProvider).hasError, isTrue);
      verify(() => mockLogger.error(
            'McpGatewaysController',
            'Refresh failed',
            any(),
            any(),
          )).called(1);
    });

    test('saveGateway performs optimistic update and confirms with backend data',
        () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      await container.read(mcpGatewaysControllerProvider.future);

      final modifiedGateway = validGateway.copyWith(slug: 'saved-slug');
      when(() => mockClient.saveMcpGateway(
            'mcp_0123456789abcdef',
            any(),
          )).thenAnswer((_) async => modifiedGateway);

      final result = await controller.saveGateway(
        'mcp_0123456789abcdef',
        modifiedGateway,
      );

      expect(result.slug, 'saved-slug');
      expect(container.read(mcpGatewaysControllerProvider).value?.first.slug,
          'saved-slug');
      verify(() => mockClient.saveMcpGateway(
            'mcp_0123456789abcdef',
            any(),
          )).called(1);
    });

    test('saveGateway reverts to previous state on network error (Fail-Fast rollback)',
        () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      await container.read(mcpGatewaysControllerProvider.future);

      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v2/studio/mcp_gateways'),
        error: AppException.network('Backend failure'),
      );

      when(() => mockClient.saveMcpGateway(
            'mcp_0123456789abcdef',
            any(),
          )).thenThrow(dioError);

      final modified = validGateway.copyWith(slug: 'failing-slug');
      expect(
        () => controller.saveGateway('mcp_0123456789abcdef', modified),
        throwsA(isA<AppException>()),
      );

      // Verify rollback occurred
      expect(container.read(mcpGatewaysControllerProvider).value?.first.slug,
          'default-mcp');
      verify(() => mockLogger.error(
            'McpGatewaysController',
            'Save failed',
            any(),
            any(),
          )).called(1);
    });

    test('deleteGateway removes gateway from list and throws on failure', () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      await container.read(mcpGatewaysControllerProvider.future);

      when(() => mockClient.deleteMcpGateway('mcp_0123456789abcdef'))
          .thenAnswer((_) async {});

      await controller.deleteGateway('mcp_0123456789abcdef');
      expect(container.read(mcpGatewaysControllerProvider).value, isEmpty);

      // Negative: delete failure
      final dioError = DioException(
        requestOptions: RequestOptions(path: '/api/v2/studio/mcp_gateways'),
        error: AppException.validation('Cannot delete active gateway'),
      );
      when(() => mockClient.deleteMcpGateway('non_existent')).thenThrow(dioError);

      expect(
        () => controller.deleteGateway('non_existent'),
        throwsA(isA<AppException>()),
      );
      verify(() => mockLogger.error(
            'McpGatewaysController',
            'Delete failed',
            any(),
            any(),
          )).called(1);
    });

    test('cloneGateway calls client and appends cloned gateway', () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      await container.read(mcpGatewaysControllerProvider.future);

      const cloned = McpGateway(
        id: 'mcp_cloned12345678',
        type: 'mcp_gateways',
        slug: 'default-mcp-copy',
        tools: [validTool],
      );

      when(() => mockClient.cloneMcpGateway('mcp_0123456789abcdef'))
          .thenAnswer((_) async => cloned);

      final result = await controller.cloneGateway('mcp_0123456789abcdef');
      expect(result.id, 'mcp_cloned12345678');
      expect(container.read(mcpGatewaysControllerProvider).value?.length, 2);

      // Negative: clone failure rolls back and throws
      when(() => mockClient.cloneMcpGateway('fail_id'))
          .thenThrow(Exception('Server error'));
      expect(
        () => controller.cloneGateway('fail_id'),
        throwsA(isA<AppException>()),
      );
      verify(() => mockLogger.error(
            'McpGatewaysController',
            'Clone failed',
            any(),
            any(),
          )).called(1);
    });

    test('createMcpGatewayDraft creates draft and prepends to list', () async {
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);

      final controller = container.read(mcpGatewaysControllerProvider.notifier);
      await container.read(mcpGatewaysControllerProvider.future);

      const draft = McpGateway(
        id: 'mcp_draft123456789',
        type: 'mcp_gateways',
        slug: 'draft-gateway',
        tools: [],
      );

      when(() => mockClient.createMcpGatewayDraft())
          .thenAnswer((_) async => draft);

      final result = await controller.createMcpGatewayDraft();
      expect(result.id, 'mcp_draft123456789');
      expect(
          container.read(mcpGatewaysControllerProvider).value?.first.id,
          'mcp_draft123456789');

      // Negative: create draft failure rolls back and throws
      when(() => mockClient.createMcpGatewayDraft())
          .thenThrow(Exception('Draft creation failed'));
      expect(
        () => controller.createMcpGatewayDraft(),
        throwsA(isA<AppException>()),
      );
      verify(() => mockLogger.error(
            'McpGatewaysController',
            'Create draft failed',
            any(),
            any(),
          )).called(1);
    });
  });

  group('mcpGatewayByIdProvider', () {
    test('fetches single gateway by ID', () async {
      when(() => mockClient.getMcpGateway('mcp_0123456789abcdef'))
          .thenAnswer((_) async => validGateway);

      final result = await container
          .read(mcpGatewayByIdProvider('mcp_0123456789abcdef').future);
      expect(result.id, 'mcp_0123456789abcdef');
      verify(() => mockClient.getMcpGateway('mcp_0123456789abcdef')).called(1);
    });
  });

  group('McpGatewayForm', () {
    test('addTool, removeTool, and forceRebuild mutate form state correctly',
        () async {
      when(() => mockClient.getMcpGateway('mcp_0123456789abcdef'))
          .thenAnswer((_) async => validGateway);

      final formNotifier = container.read(
        mcpGatewayFormProvider('mcp_0123456789abcdef').notifier,
      );
      await container
          .read(mcpGatewayFormProvider('mcp_0123456789abcdef').future);

      expect(
        container
            .read(mcpGatewayFormProvider('mcp_0123456789abcdef'))
            .value
            ?.tools
            .length,
        1,
      );

      // Add tool
      formNotifier.addTool();
      expect(
        container
            .read(mcpGatewayFormProvider('mcp_0123456789abcdef'))
            .value
            ?.tools
            .length,
        2,
      );

      // Remove tool
      formNotifier.removeTool(1);
      expect(
        container
            .read(mcpGatewayFormProvider('mcp_0123456789abcdef'))
            .value
            ?.tools
            .length,
        1,
      );

      // Force rebuild
      const modified = McpGateway(
        id: 'mcp_0123456789abcdef',
        type: 'mcp_gateways',
        slug: 'rebuilt-gateway',
        tools: [],
      );
      formNotifier.forceRebuild(modified);
      expect(
        container
            .read(mcpGatewayFormProvider('mcp_0123456789abcdef'))
            .value
            ?.slug,
        'rebuilt-gateway',
      );
    });

    test('submit calls saveGateway and updates form state', () async {
      when(() => mockClient.getMcpGateway('mcp_0123456789abcdef'))
          .thenAnswer((_) async => validGateway);
      when(() => mockClient.getMcpGateways())
          .thenAnswer((_) async => [validGateway]);
      when(() => mockClient.saveMcpGateway('mcp_0123456789abcdef', any()))
          .thenAnswer((_) async => validGateway);

      final formNotifier = container.read(
        mcpGatewayFormProvider('mcp_0123456789abcdef').notifier,
      );
      await container
          .read(mcpGatewayFormProvider('mcp_0123456789abcdef').future);

      await formNotifier.submit(validGateway);

      expect(
        container
            .read(mcpGatewayFormProvider('mcp_0123456789abcdef'))
            .value
            ?.id,
        'mcp_0123456789abcdef',
      );
    });
  });
}
