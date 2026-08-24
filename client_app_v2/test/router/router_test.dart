import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('targetRouteForUser Tests', () {
    test('returns /admin for root and admin roles', () {
      expect(targetRouteForUser(UserRole.root), '/admin');
      expect(targetRouteForUser(UserRole.admin), '/admin');
    });

    test(
      'returns /dashboard for member, manager, viewer, and unknown roles',
      () {
        expect(targetRouteForUser(UserRole.member), '/dashboard');
        expect(targetRouteForUser(UserRole.manager), '/dashboard');
        expect(targetRouteForUser(UserRole.viewer), '/dashboard');
        expect(targetRouteForUser(UserRole.unknown), '/dashboard');
      },
    );
  });

  group('TypedGoRoute Data Structures & Instantiation Tests', () {
    test('instantiates all authentication and app shell routes', () {
      const loginRoute = LoginRoute();
      expect(loginRoute, isNotNull);

      const splashRoute = SplashRoute();
      expect(splashRoute, isNotNull);

      const dashboardRoute = DashboardRoute();
      expect(dashboardRoute, isNotNull);

      const executionRoute = ExecutionRoute(executionId: 'exec_abc123');
      expect(executionRoute.executionId, 'exec_abc123');

      const executionReportRoute = ExecutionReportRoute(
        executionId: 'exec_abc123',
        variant: 'detailed',
      );
      expect(executionReportRoute.executionId, 'exec_abc123');
      expect(executionReportRoute.variant, 'detailed');

      const newExecutionRoute = NewExecutionRoute();
      expect(newExecutionRoute, isNotNull);

      const settingsRoute = SettingsRoute();
      expect(settingsRoute, isNotNull);

      const rootRoute = RootRoute();
      expect(rootRoute, isNotNull);
    });

    test('instantiates all Studio and Admin TypedGoRoutes', () {
      const adminShellRoute = AdminShellRoute();
      expect(adminShellRoute, isNotNull);

      const wfNew = WorkflowNewRoute();
      expect(wfNew, isNotNull);

      const wfEdit = WorkflowEditRoute(id: 'wf_1', slug: 'alpha-flow');
      expect(wfEdit.id, 'wf_1');
      expect(wfEdit.slug, 'alpha-flow');

      const pbNew = PromptBlockNewRoute();
      expect(pbNew, isNotNull);

      const pbEdit = PromptBlockEditRoute(id: 'pb_1', slug: 'block-one');
      expect(pbEdit.id, 'pb_1');
      expect(pbEdit.slug, 'block-one');

      const stepNew = StepNewRoute();
      expect(stepNew, isNotNull);

      const stepEdit = StepEditRoute(id: 'step_1');
      expect(stepEdit.id, 'step_1');

      const profEdit = ProfileEditorRoute(workflowId: 'wf_99');
      expect(profEdit.workflowId, 'wf_99');

      const outProfNew = OutputProfileNewRoute();
      expect(outProfNew, isNotNull);

      const outProfEdit = OutputProfileEditRoute(id: 'op_1');
      expect(outProfEdit.id, 'op_1');

      const mrNew = ModelRegistryNewRoute();
      expect(mrNew, isNotNull);

      const mrEdit = ModelRegistryEditRoute(id: 'mr_1');
      expect(mrEdit.id, 'mr_1');

      const mcpNew = McpGatewayNewRoute();
      expect(mcpNew, isNotNull);

      const mcpEdit = McpGatewayEditRoute(id: 'gw_1');
      expect(mcpEdit.id, 'gw_1');

      const matNew = MatrixNewRoute();
      expect(matNew, isNotNull);

      const matEdit = MatrixEditRoute(id: 'mat_1');
      expect(matEdit.id, 'mat_1');
    });
  });

  group('SafeNavigationFallback Widget Tests', () {
    testWidgets('renders fallback snackbar and navigates to dashboard', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final testRouter = GoRouter(
        initialLocation: '/unknown-route',
        errorBuilder: (context, state) => SafeNavigationFallback(state: state),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (context, state) => const Scaffold(
              body: Center(child: Text('Dashboard View Placeholder')),
            ),
          ),
        ],
      );

      await tester.pumpWidget(
        MaterialApp.router(
          routerConfig: testRouter,
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: const [Locale('en')],
        ),
      );

      await tester.pumpAndSettle();

      // Should show the fallback snackbar and land on dashboard
      expect(find.text('Dashboard View Placeholder'), findsOneWidget);
      expect(find.byType(SnackBar), findsOneWidget);

      // Drain the SnackBar display timer before test finishes
      await tester.pump(const Duration(seconds: 5));
    });
  });
}
