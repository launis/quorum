import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/mcp_gateway_view.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:mocktail/mocktail.dart';

class MockLoggerService extends Mock implements LoggerService {}

class MockMcpGatewayFormController extends McpGatewayForm {
  final McpGateway initialGateway;
  final bool simulateError;
  final bool simulateDiscoverError;
  bool discoverCalled = false;

  MockMcpGatewayFormController(
    this.initialGateway, {
    this.simulateError = false,
    this.simulateDiscoverError = false,
  });

  @override
  FutureOr<McpGateway> build(String gatewayId) async {
    if (simulateError) {
      throw AppException.notFound('Gateway not found: $gatewayId');
    }
    return initialGateway;
  }

  @override
  Future<void> discoverTools([McpGateway? updatedData]) async {
    discoverCalled = true;
    if (simulateDiscoverError) {
      throw AppException.network('Discovery endpoint unreachable');
    }
    final current = updatedData ?? state.value ?? initialGateway;
    final discovered = current.copyWith(
      tools: [
        ...current.tools,
        const AllowedMcpTool(
          toolId: 'discovered_reader',
          capability: ToolCapability.documentReader,
          enabled: true,
          name: I18nText(
            translations: {'en': 'Discovered Reader', 'fi': 'Löydetty lukija'},
          ),
          description: 'Read external documents over MCP',
          inputSchema: McpToolInputSchemaDto(
            properties: {
              'url': McpToolSchemaPropertyDto(
                type: JsonSchemaPropertyType.string,
                description: 'Document URL to fetch',
              ),
            },
            requiredFields: ['url'],
          ),
        ),
      ],
    );
    state = AsyncData(discovered);
  }
}

void main() {
  Widget createTestWidget({
    required McpGateway gateway,
    bool simulateError = false,
    bool simulateDiscoverError = false,
    MockMcpGatewayFormController? customController,
  }) {
    final controller =
        customController ??
        MockMcpGatewayFormController(
          gateway,
          simulateError: simulateError,
          simulateDiscoverError: simulateDiscoverError,
        );
    final mockLogger = MockLoggerService();
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        mcpGatewayFormProvider(gateway.id).overrideWith(() => controller),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        home: McpGatewayView(id: gateway.id),
      ),
    );
  }

  group('McpGatewayView Widget Tests', () {
    const testGateway = McpGateway(
      id: 'gw_search',
      slug: 'search_gateway',
      type: 'mcp_gateways',
      endpointUrl: 'https://mcp.example.com/v1',
      transportType: McpTransportType.streamableHttp,
      authType: McpAuthType.bearer,
      authEnvVar: 'TAVILY_API_KEY',
      timeoutSeconds: 30,
      tools: [
        AllowedMcpTool(
          toolId: 'mcp_tavily_search',
          capability: ToolCapability.search,
          enabled: true,
          name: I18nText(
            translations: {'en': 'Tavily Search', 'fi': 'Tavily Haku'},
          ),
          description: 'Search the web using Tavily API',
          inputSchema: McpToolInputSchemaDto(
            properties: {
              'query': McpToolSchemaPropertyDto(
                type: JsonSchemaPropertyType.string,
                description: 'Search query string',
              ),
            },
            requiredFields: ['query'],
          ),
        ),
      ],
    );

    testWidgets(
      'renders gateway metadata, 1200px ConstrainedBox, connection card, parameter DataTable, and tools properly',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1200);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(createTestWidget(gateway: testGateway));
        await tester.pumpAndSettle();

        expect(find.text('gw_search'), findsOneWidget);
        expect(find.text('search_gateway'), findsOneWidget);
        expect(find.text('mcp_gateways'), findsOneWidget);
        expect(find.text('https://mcp.example.com/v1'), findsOneWidget);
        expect(find.text('TAVILY_API_KEY'), findsOneWidget);
        expect(find.text('Tool: mcp_tavily_search'), findsOneWidget);
        expect(find.text('Search the web using Tavily API'), findsOneWidget);

        // Verify 1200px ConstrainedBox canvas containment
        final constrainedFinder = find.byWidgetPredicate(
          (w) => w is ConstrainedBox && w.constraints.maxWidth == 1200,
        );
        expect(constrainedFinder, findsOneWidget);

        // Verify Parameter Schema Preview DataTable
        expect(find.byType(DataTable), findsOneWidget);
        expect(find.text('query'), findsOneWidget);
        expect(find.text('Search query string'), findsOneWidget);
      },
    );

    testWidgets(
      'triggers live tool discovery via Connect and Discover Tools button and updates tool list',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1200);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final controller = MockMcpGatewayFormController(testGateway);
        await tester.pumpWidget(
          createTestWidget(gateway: testGateway, customController: controller),
        );
        await tester.pumpAndSettle();

        final discoverBtn = find.text('Connect and Discover Tools');
        expect(discoverBtn, findsOneWidget);
        await tester.tap(discoverBtn);
        await tester.pumpAndSettle();

        expect(controller.discoverCalled, isTrue);
        expect(find.text('Tool: discovered_reader'), findsOneWidget);
      },
    );

    testWidgets('allows toggling tool allowlist SwitchListTile', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final controller = MockMcpGatewayFormController(testGateway);
      await tester.pumpWidget(
        createTestWidget(gateway: testGateway, customController: controller),
      );
      await tester.pumpAndSettle();

      final switchFinder = find.byType(SwitchListTile);
      expect(switchFinder, findsOneWidget);
      expect(tester.widget<SwitchListTile>(switchFinder).value, isTrue);

      await tester.tap(switchFinder);
      await tester.pumpAndSettle();

      expect(tester.widget<SwitchListTile>(switchFinder).value, isFalse);
      expect(controller.state.value!.tools.first.enabled, isFalse);
    });

    testWidgets('allows adding a new tool', (tester) async {
      tester.view.physicalSize = const Size(1920, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(createTestWidget(gateway: testGateway));
      await tester.pumpAndSettle();

      final addToolFinder = find.byIcon(Icons.add);
      expect(addToolFinder, findsOneWidget);
      await tester.tap(addToolFinder);
      await tester.pumpAndSettle();

      expect(find.text('Tool: new_tool'), findsOneWidget);
    });

    testWidgets('allows removing an existing tool', (tester) async {
      tester.view.physicalSize = const Size(1920, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(createTestWidget(gateway: testGateway));
      await tester.pumpAndSettle();

      final toolDeleteFinder = find.descendant(
        of: find.byType(ExpansionTile),
        matching: find.byType(IconButton),
      );
      expect(toolDeleteFinder, findsOneWidget);

      await tester.ensureVisible(toolDeleteFinder);
      await tester.tap(toolDeleteFinder);
      await tester.pumpAndSettle();

      expect(find.text('Tool: mcp_tavily_search'), findsNothing);
      expect(find.text('No tools defined for this gateway.'), findsOneWidget);
    });

    testWidgets(
      'negative ISTQB partition: invalid timeoutSeconds input triggers validation error',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1200);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(createTestWidget(gateway: testGateway));
        await tester.pumpAndSettle();

        final timeoutField = find.widgetWithText(
          TextFormField,
          'Timeout (seconds)',
        );
        expect(timeoutField, findsOneWidget);

        await tester.ensureVisible(timeoutField);
        await tester.enterText(timeoutField, '0');
        await tester.pumpAndSettle();

        final saveFinder = find.byIcon(Icons.save);
        await tester.tap(saveFinder);
        await tester.pumpAndSettle();

        expect(find.text('Invalid JSON'), findsOneWidget);
      },
    );

    testWidgets(
      'negative ISTQB partition: discovery failure displays MaterialBanner error message',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1200);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          createTestWidget(gateway: testGateway, simulateDiscoverError: true),
        );
        await tester.pumpAndSettle();

        final discoverBtn = find.text('Connect and Discover Tools');
        await tester.tap(discoverBtn);
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsOneWidget);
        expect(
          find.textContaining('Discovery endpoint unreachable'),
          findsOneWidget,
        );
      },
    );

    testWidgets('negative ISTQB partition: error state renders ErrorView', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(gateway: testGateway, simulateError: true),
      );
      await tester.pumpAndSettle();

      expect(find.byType(ErrorView), findsOneWidget);
    });
  });
}
