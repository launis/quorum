import 'package:client_app/features/shell/presentation/scaffold_with_nav.dart';
import 'package:client_app/features/shell/presentation/widgets/admin_sidebar.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

GoRouter _buildTestRouter() {
  return GoRouter(
    initialLocation: '/studio',
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            ScaffoldWithNav(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/studio',
                builder: (context, state) =>
                    const Center(child: Icon(Icons.hub)),
                routes: [
                  GoRoute(
                    path: 'details',
                    builder: (context, state) =>
                        const Center(child: Icon(Icons.details)),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/registry',
                builder: (context, state) =>
                    const Center(child: Icon(Icons.inventory_2)),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/analytics',
                builder: (context, state) =>
                    const Center(child: Icon(Icons.query_stats)),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/admin',
                builder: (context, state) =>
                    const Center(child: Icon(Icons.security)),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/inspector',
                builder: (context, state) =>
                    const Center(child: Icon(Icons.webhook)),
              ),
            ],
          ),
        ],
      ),
    ],
  );
}

Widget _buildTestApp(GoRouter router) {
  return MaterialApp.router(
    routerConfig: router,
    localizationsDelegates: const [
      AppLocalizations.delegate,
      GlobalMaterialLocalizations.delegate,
      GlobalWidgetsLocalizations.delegate,
      GlobalCupertinoLocalizations.delegate,
    ],
    supportedLocales: const [Locale('en')],
  );
}

void main() {
  group('ScaffoldWithNav (Admin Shell) Hardening Tests', () {
    testWidgets(
      'Positive & Boundary (800dp): renders AdminSidebar with NavigationRail on wide screens and switches branches cleanly',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(800, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final router = _buildTestRouter();
        addTearDown(router.dispose);

        await tester.pumpWidget(_buildTestApp(router));
        await tester.pumpAndSettle();

        expect(find.byType(AdminSidebar), findsOneWidget);
        expect(find.byType(NavigationRail), findsOneWidget);
        expect(find.byType(NavigationBar), findsNothing);
        expect(find.byIcon(Icons.hub), findsOneWidget);

        await tester.tap(find.byIcon(Icons.schema_outlined));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.inventory_2), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 1 (799dp): omits AdminSidebar and renders bottom NavigationBar when viewport width is below 800dp',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(799, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final router = _buildTestRouter();
        addTearDown(router.dispose);

        await tester.pumpWidget(_buildTestApp(router));
        await tester.pumpAndSettle();

        expect(find.byType(AdminSidebar), findsNothing);
        expect(find.byType(NavigationRail), findsNothing);
        expect(find.byType(NavigationBar), findsOneWidget);

        await tester.tap(find.byIcon(Icons.api_outlined));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.webhook), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 2: re-tapping active branch resets branch to initialLocation while preserving shell layout',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final router = _buildTestRouter();
        addTearDown(router.dispose);

        await tester.pumpWidget(_buildTestApp(router));
        await tester.pumpAndSettle();

        router.go('/studio/details');
        await tester.pumpAndSettle();
        expect(find.byIcon(Icons.details), findsOneWidget);

        await tester.tap(find.byIcon(Icons.auto_graph));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.hub), findsOneWidget);
        expect(find.byIcon(Icons.details), findsNothing);
      },
    );
  });
}
