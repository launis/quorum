import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/settings/presentation/widgets/admin_limit_controls.dart';
import 'package:client_app/features/settings/usage_stats_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class MockAuthController extends AuthController {
  final User? initialUser;
  MockAuthController(this.initialUser);
  @override
  Stream<User?> build() {
    return Stream.value(initialUser);
  }
}

void main() {
  testWidgets('AdminLimitControls renders for ROOT user', (tester) async {
    final mockUser = User(
      email: 'root@example.com',
      role: UserRole.root,
      organizationId: 'org-1',
      uid: 'root-123',
    );

    final mockStats = UsageStats(
      usedCost: 10.0,
      costLimit: 100.0,
      tpmLimit: 50000,
      rpmLimit: 60,
      percentage: 0.1,
      period: '2026-01',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            () => MockAuthController(mockUser),
          ),
          usageStatsProvider.overrideWith((ref) => Future.value(mockStats)),
        ],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(body: AdminLimitControls()),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Admin Controls'), findsOneWidget);
    expect(find.text('50000'), findsOneWidget); // TPM initial value
  });

  testWidgets('AdminLimitControls hides for MEMBER user', (tester) async {
    final mockUser = User(
      email: 'member@example.com',
      role: UserRole.member,
      organizationId: 'org-1',
      uid: 'member-123',
    );

    final mockStats = UsageStats(
      usedCost: 0,
      costLimit: 1,
      tpmLimit: 0,
      rpmLimit: 0,
      percentage: 0,
      period: '',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            () => MockAuthController(mockUser),
          ),
          usageStatsProvider.overrideWith((ref) => Future.value(mockStats)),
        ],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(body: AdminLimitControls()),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Admin Controls'), findsNothing);
  });
}
