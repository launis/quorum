import 'dart:async';

import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

class _StubAuthController extends AuthController {
  final AsyncValue<User?> _initialState;

  _StubAuthController(this._initialState);

  @override
  FutureOr<User?> build() {
    state = _initialState;
    return switch (_initialState) {
      AsyncData(:final value) => value,
      AsyncError(:final error, :final stackTrace) => Future<User?>.error(
        error,
        stackTrace,
      ),
      AsyncLoading() => Completer<User?>().future,
    };
  }
}

GoRouter _buildTestRouter() {
  return GoRouter(
    initialLocation: '/dashboard',
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) =>
            ScaffoldWithNav(navigationShell: navigationShell),
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/dashboard',
                builder: (context, state) =>
                    const Center(child: Text('Branch 0: Dashboard')),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/orchestration/new',
                builder: (context, state) =>
                    const Center(child: Text('Branch 1: New Analysis')),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/settings',
                builder: (context, state) =>
                    const Center(child: Text('Branch 2: Settings')),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/organization',
                builder: (context, state) =>
                    const Center(child: Text('Branch 3: Organization')),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: '/admin',
        builder: (context, state) =>
            const Scaffold(body: Center(child: Text('Admin Studio View'))),
      ),
    ],
  );
}

Widget _buildTestApp({
  required GoRouter router,
  required AsyncValue<User?> authState,
}) {
  return ProviderScope(
    overrides: [
      authControllerProvider.overrideWith(() => _StubAuthController(authState)),
    ],
    child: MaterialApp.router(
      routerConfig: router,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en')],
    ),
  );
}

void main() {
  const adminUser = User(
    id: 'usr_01960000000070008000000000000001',
    email: 'admin@quorum.ai',
    role: UserRole.admin,
    organizationId: 'org_01960000000070008000000000000001',
  );

  const memberUser = User(
    id: 'usr_01960000000070008000000000000002',
    email: 'member@quorum.ai',
    role: UserRole.member,
    organizationId: 'org_01960000000070008000000000000001',
  );

  group('ScaffoldWithNav Positive, Negative & Boundary Widget Tests', () {
    testWidgets(
      'positive & boundary (800dp): renders NavigationRail with Admin destination on wide screens for admin user and navigates across branches and /admin',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(800, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final router = _buildTestRouter();
        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            authState: const AsyncData<User?>(adminUser),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(NavigationRail), findsOneWidget);
        expect(find.byType(NavigationBar), findsNothing);
        expect(
          find.byIcon(Icons.admin_panel_settings_outlined),
          findsOneWidget,
        );
        expect(find.text('Branch 0: Dashboard'), findsOneWidget);

        // Tap Branch 1 (New Analysis)
        await tester.tap(find.byIcon(Icons.add_circle_outline));
        await tester.pumpAndSettle();
        expect(find.text('Branch 1: New Analysis'), findsOneWidget);

        // Tap Admin destination (index 3) -> navigates to /admin
        await tester.tap(find.byIcon(Icons.admin_panel_settings_outlined));
        await tester.pumpAndSettle();
        expect(find.text('Admin Studio View'), findsOneWidget);
      },
    );

    testWidgets(
      'boundary (799dp) & negative role check: renders bottom NavigationBar without Admin destination for member user on narrow screens',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(799, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final router = _buildTestRouter();
        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            authState: const AsyncData<User?>(memberUser),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(NavigationBar), findsOneWidget);
        expect(find.byType(NavigationRail), findsNothing);
        expect(find.byIcon(Icons.admin_panel_settings_outlined), findsNothing);

        // Tap Profile destination (index 2) on NavigationBar
        await tester.tap(find.byIcon(Icons.person_outline));
        await tester.pumpAndSettle();
        expect(find.text('Branch 2: Settings'), findsOneWidget);
      },
    );

    testWidgets(
      'negative: suppresses Admin destination when authControllerProvider is in AsyncError or null user state',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final router = _buildTestRouter();
        await tester.pumpWidget(
          _buildTestApp(
            router: router,
            authState: const AsyncData<User?>(null),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(NavigationRail), findsOneWidget);
        expect(find.byIcon(Icons.admin_panel_settings_outlined), findsNothing);
      },
    );
  });
}
