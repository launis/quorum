import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/mcp_gateways_master_view.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockMcpGatewaysController extends McpGatewaysController {
  final List<McpGateway> gateways;
  final Future<McpGateway> Function(String id)? onClone;
  MockMcpGatewaysController(this.gateways, {this.onClone});

  @override
  FutureOr<List<McpGateway>> build() async {
    return gateways;
  }

  @override
  Future<McpGateway> cloneGateway(String id) async {
    if (onClone != null) {
      return await onClone!(id);
    }
    return McpGateway(id: '${id}_clone');
  }
}

void main() {
  Widget createTestWidget(
    List<McpGateway> gateways, {
    Future<McpGateway> Function(String id)? onClone,
    Size screenSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        mcpGatewaysControllerProvider.overrideWith(
          () => MockMcpGatewaysController(gateways, onClone: onClone),
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
        home: MediaQuery(
          data: MediaQueryData(size: screenSize),
          child: const Scaffold(body: McpGatewaysMasterView()),
        ),
      ),
    );
  }

  group('McpGatewaysMasterView Widget Tests', () {
    testWidgets('test_mcp_gateways_master_view_search_and_clone', (
      tester,
    ) async {
      String clonedId = '';
      final gateways = [
        const McpGateway(id: 'gw_web_search'),
        const McpGateway(id: 'gw_database_query'),
      ];

      await tester.pumpWidget(
        createTestWidget(
          gateways,
          onClone: (id) async {
            clonedId = id;
            return McpGateway(id: '${id}_clone');
          },
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('gw_web_search'), findsOneWidget);
      expect(find.text('gw_database_query'), findsOneWidget);
      expect(find.text('Showing 2 of 2 items'), findsOneWidget);

      // Search for 'database'
      await tester.enterText(find.byType(TextField), 'database');
      await tester.pumpAndSettle();

      expect(find.text('gw_web_search'), findsNothing);
      expect(find.text('gw_database_query'), findsOneWidget);
      expect(find.text('Showing 1 of 2 items'), findsOneWidget);

      // Click Clone button (CloneEntityButton renders Icons.copy)
      final cloneButtonFinder = find.byIcon(Icons.copy);
      expect(cloneButtonFinder, findsOneWidget);
      await tester.tap(cloneButtonFinder);
      await tester.pumpAndSettle();

      expect(clonedId, 'gw_database_query');
    });

    testWidgets('test_master_views_4k_display_containment', (tester) async {
      tester.view.physicalSize = const Size(3840, 2160);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final gateways = [const McpGateway(id: 'gw_1')];
      await tester.pumpWidget(
        createTestWidget(gateways, screenSize: const Size(3840, 2160)),
      );
      await tester.pumpAndSettle();

      final constrainedBoxFinder = find.byWidgetPredicate(
        (widget) =>
            widget is ConstrainedBox && widget.constraints.maxWidth == 1200.0,
      );
      expect(constrainedBoxFinder, findsOneWidget);

      final box = tester.renderObject(constrainedBoxFinder) as RenderBox;
      expect(box.size.width, lessThanOrEqualTo(1200.0));
    });

    testWidgets('test_mcp_gateways_master_view_virtualized_rendering', (
      tester,
    ) async {
      final mockList = List.generate(
        30,
        (i) => McpGateway(id: 'gw_${i.toString().padLeft(3, '0')}'),
      );

      await tester.pumpWidget(createTestWidget(mockList));
      await tester.pumpAndSettle();

      final listViewFinder = find.byType(ListView);
      expect(listViewFinder, findsOneWidget);

      final listView = tester.widget<ListView>(listViewFinder);
      expect(listView.prototypeItem, isNotNull);

      final visibleTiles = find.byType(ListTile);
      expect(visibleTiles.evaluate().length, lessThan(30));
      expect(visibleTiles.evaluate().length, greaterThan(0));

      expect(find.text('Showing 30 of 30 items'), findsOneWidget);
    });

    testWidgets('renders zero-state when no gateways defined', (tester) async {
      await tester.pumpWidget(createTestWidget([]));
      await tester.pumpAndSettle();

      expect(find.text('No MCP gateways defined.'), findsOneWidget);
      expect(find.text('Showing 0 of 0 items'), findsOneWidget);
    });

    testWidgets('renders search miss when query matches 0 items', (
      tester,
    ) async {
      final gateways = [const McpGateway(id: 'gw_1')];
      await tester.pumpWidget(createTestWidget(gateways));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'UnknownGateway');
      await tester.pumpAndSettle();

      expect(find.text('No matching items found.'), findsOneWidget);
      expect(find.text('Showing 0 of 1 items'), findsOneWidget);
    });
  });
}
