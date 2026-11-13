import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/views/mcp_gateways_master_view.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockLoggerService extends Mock implements LoggerService {}

class MockMcpGatewaysController extends McpGatewaysController {
  final AsyncValue<List<McpGateway>> initialState;
  final Future<McpGateway> Function(String id)? onClone;
  final Future<McpGateway> Function()? onCreateDraft;
  final Future<void> Function()? onRefresh;

  MockMcpGatewaysController(
    List<McpGateway> gateways, {
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  }) : initialState = AsyncData(gateways);

  MockMcpGatewaysController.fromAsync(
    this.initialState, {
    this.onClone,
    this.onCreateDraft,
    this.onRefresh,
  });

  @override
  FutureOr<List<McpGateway>> build() async {
    return switch (initialState) {
      AsyncData(:final value) => value,
      AsyncError(:final error, :final stackTrace) => Error.throwWithStackTrace(
        error,
        stackTrace,
      ),
      _ => Completer<List<McpGateway>>().future,
    };
  }

  @override
  Future<McpGateway> cloneGateway(String id) async {
    if (onClone != null) {
      return await onClone!(id);
    }
    return McpGateway(
      id: '${id}_clone',
      organizationId: 'org_0195f3a0000070008000000000000001',
      name: '${id}_clone',
    );
  }

  @override
  Future<McpGateway> createMcpGatewayDraft() async {
    if (onCreateDraft != null) {
      return await onCreateDraft!();
    }
    return const McpGateway(
      id: 'mcp_01950000000070008000000000000099',
      organizationId: 'org_0195f3a0000070008000000000000001',
      name: 'New MCP Gateway Draft',
      slug: 'draft-gateway',
    );
  }

  @override
  Future<void> refresh() async {
    if (onRefresh != null) {
      await onRefresh!();
    }
  }
}

void main() {
  late MockLoggerService mockLogger;

  setUp(() {
    mockLogger = MockLoggerService();
    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    when(() => mockLogger.info(any(), any())).thenReturn(null);
  });

  Widget createTestWidget(
    List<McpGateway> gateways, {
    Future<McpGateway> Function(String id)? onClone,
    Future<McpGateway> Function()? onCreateDraft,
    Future<void> Function()? onRefresh,
    Size screenSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        mcpGatewaysControllerProvider.overrideWith(
          () => MockMcpGatewaysController(
            gateways,
            onClone: onClone,
            onCreateDraft: onCreateDraft,
            onRefresh: onRefresh,
          ),
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

  Widget createAsyncTestWidget(
    AsyncValue<List<McpGateway>> asyncState, {
    Future<void> Function()? onRefresh,
  }) {
    return ProviderScope(
      key: UniqueKey(),
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        mcpGatewaysControllerProvider.overrideWith(
          () => MockMcpGatewaysController.fromAsync(
            asyncState,
            onRefresh: onRefresh,
          ),
        ),
      ],
      child: const MaterialApp(
        localizationsDelegates: [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: [Locale('en'), Locale('fi')],
        home: Scaffold(body: McpGatewaysMasterView()),
      ),
    );
  }

  group('McpGatewaysMasterView Widget Tests', () {
    testWidgets('test_mcp_gateways_master_view_search_and_clone', (
      tester,
    ) async {
      String clonedId = '';
      final gateways = [
        const McpGateway(
          id: 'gw_web_search',
          organizationId: 'org_0195f3a0000070008000000000000001',
          name: 'gw_web_search',
          slug: 'web-search-gateway',
        ),
        const McpGateway(
          id: 'gw_database_query',
          organizationId: 'org_0195f3a0000070008000000000000001',
          name: 'gw_database_query',
          slug: 'db-query-gateway',
        ),
      ];

      await tester.pumpWidget(
        createTestWidget(
          gateways,
          onClone: (id) async {
            clonedId = id;
            return McpGateway(
              id: '${id}_clone',
              organizationId: 'org_0195f3a0000070008000000000000001',
              name: '${id}_clone',
            );
          },
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(AppErrorBoundary), findsOneWidget);
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

      final gateways = [
        const McpGateway(
          id: 'gw_1',
          organizationId: 'org_0195f3a0000070008000000000000001',
          name: 'gw_1',
        ),
      ];
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
        (i) => McpGateway(
          id: 'gw_${i.toString().padLeft(3, '0')}',
          organizationId: 'org_0195f3a0000070008000000000000001',
          name: 'gw_${i.toString().padLeft(3, '0')}',
        ),
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
      final gateways = [
        const McpGateway(
          id: 'gw_1',
          organizationId: 'org_0195f3a0000070008000000000000001',
          name: 'gw_1',
        ),
      ];
      await tester.pumpWidget(createTestWidget(gateways));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'UnknownGateway');
      await tester.pumpAndSettle();

      expect(find.text('No matching items found.'), findsOneWidget);
      expect(find.text('Showing 0 of 1 items'), findsOneWidget);
    });

    testWidgets(
      'renders ErrorView on AsyncError and triggers refresh on retry',
      (tester) async {
        bool refreshCalled = false;
        final error = AppException.validation('Backend fetch failure');

        await tester.pumpWidget(
          createAsyncTestWidget(
            AsyncError(error, StackTrace.current),
            onRefresh: () async {
              refreshCalled = true;
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(AppErrorBoundary), findsOneWidget);
        expect(find.byType(ErrorView), findsOneWidget);

        final retryButton = find.byIcon(Icons.refresh);
        expect(retryButton, findsOneWidget);
        await tester.tap(retryButton);
        await tester.pumpAndSettle();

        expect(refreshCalled, isTrue);
      },
    );

    testWidgets(
      'displays MaterialBanner and logs error when draft creation fails, and dismisses on cancel',
      (tester) async {
        await tester.pumpWidget(
          createTestWidget(
            [],
            onCreateDraft: () async {
              throw AppException.validation('Minting failed');
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.add));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsOneWidget);
        verify(
          () => mockLogger.error(
            'McpGatewaysMasterView',
            'Failed to mint',
            any(),
            any(),
          ),
        ).called(1);

        await tester.tap(find.text('Cancel'));
        await tester.pumpAndSettle();

        expect(find.byType(MaterialBanner), findsNothing);
      },
    );

    testWidgets(
      'displays error SnackBar and logs telemetry when cloneGateway fails',
      (tester) async {
        final gateways = [
          const McpGateway(
            id: 'gw_web_search',
            organizationId: 'org_0195f3a0000070008000000000000001',
            name: 'gw_web_search',
          ),
        ];

        await tester.pumpWidget(
          createTestWidget(
            gateways,
            onClone: (id) async {
              throw AppException.validation('Duplicate failure');
            },
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.copy));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'CloneEntityButton',
            'Clone operation failed',
            any(),
          ),
        ).called(1);
        expect(find.byType(SnackBar), findsOneWidget);
      },
    );

    testWidgets(
      'crashes Fail-Fast into AppErrorBoundary when gateway ID is empty',
      (tester) async {
        final originalOnError = FlutterError.onError;
        FlutterError.onError = (FlutterErrorDetails details) {};
        try {
          final gateways = [
            const McpGateway(
              id: '',
              organizationId: 'org_0195f3a0000070008000000000000001',
              name: 'Empty ID Gateway',
            ),
          ];

          await tester.pumpWidget(createTestWidget(gateways));
          await tester.pumpAndSettle();

          expect(find.byIcon(Icons.report_problem), findsOneWidget);
          expect(
            find.textContaining('Fail-Fast: MCP Gateway ID is missing.'),
            findsOneWidget,
          );
        } finally {
          FlutterError.onError = originalOnError;
        }
      },
    );
  });
}
