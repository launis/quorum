import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/mcp_gateway_view.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';

class MockMcpGatewayFormController extends McpGatewayForm {
  final McpGateway initialGateway;
  final bool simulateError;

  MockMcpGatewayFormController(this.initialGateway, {this.simulateError = false});

  @override
  FutureOr<McpGateway> build(String gatewayId) async {
    if (simulateError) {
      throw AppException.notFound('Gateway not found: $gatewayId');
    }
    return initialGateway;
  }
}

void main() {
  Widget createTestWidget({
    required McpGateway gateway,
    bool simulateError = false,
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        mcpGatewayFormProvider(gateway.id).overrideWith(
          () => MockMcpGatewayFormController(gateway, simulateError: simulateError),
        ),
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
      type: 'stdio',
      tools: [
        AllowedMcpTool(
          toolId: 'tavily_search',
          name: I18nText(translations: {'en': 'Tavily Search', 'fi': 'Tavily Haku'}),
          description: 'Search the web using Tavily API',
          inputSchema: {'query': {'type': 'string'}},
        ),
      ],
    );

    testWidgets('renders gateway metadata and tools properly', (tester) async {
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
      expect(find.text('stdio'), findsOneWidget);
      expect(find.text('Tool: tavily_search'), findsOneWidget);
      expect(find.text('Search the web using Tavily API'), findsOneWidget);
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

      expect(find.text('Tool: tavily_search'), findsNothing);
      expect(find.text('No tools defined for this gateway.'), findsOneWidget);
    });

    testWidgets('negative ISTQB partition: invalid JSON schema triggers validation error', (tester) async {
      tester.view.physicalSize = const Size(1920, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(createTestWidget(gateway: testGateway));
      await tester.pumpAndSettle();

      // Find the JSON input schema field by its label text
      final jsonField = find.widgetWithText(TextFormField, 'JSON Input Schema');
      expect(jsonField, findsOneWidget);

      await tester.ensureVisible(jsonField);
      await tester.enterText(jsonField, '{invalid json syntax');
      await tester.pumpAndSettle();

      // Tap Save button in AppBar
      final saveFinder = find.byIcon(Icons.save);
      await tester.tap(saveFinder);
      await tester.pumpAndSettle();

      expect(find.text('Invalid JSON'), findsOneWidget);
    });

    testWidgets('negative ISTQB partition: error state renders ErrorView', (tester) async {
      await tester.pumpWidget(createTestWidget(gateway: testGateway, simulateError: true));
      await tester.pumpAndSettle();

      expect(find.byType(ErrorView), findsOneWidget);
    });
  });
}
