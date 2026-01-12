import 'dart:async';
import 'package:client_app/features/admin/presentation/providers/admin_providers.dart';
import 'package:client_app/features/admin/presentation/screens/user_management_screen.dart';
import 'package:client_app/features/admin/presentation/widgets/role_selector_dialog.dart';
import 'package:client_app/features/admin/presentation/widgets/user_list_item.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class FakeAuthController extends AuthController {
  final Stream<User?> _stream;
  FakeAuthController(this._stream);

  @override
  Stream<User?> build() => _stream;
}

class FakeAuthLoadingController extends AuthController {
  @override
  Stream<User?> build() => StreamController<User?>().stream;
}

void main() {
  const testOrgId = 'org-123';
  const testUser = User(
    uid: 'user-1',
    email: 'admin@example.com',
    role: UserRole.admin,
    organizationId: testOrgId,
  );

  const testUser2 = User(
    uid: 'user-2',
    email: 'member@example.com',
    role: UserRole.member,
    organizationId: testOrgId,
  );

  testWidgets('UserManagementScreen shows loading state initially', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            () => FakeAuthLoadingController(),
          ),
        ],
        child: const MaterialApp(
          localizationsDelegates: [AppLocalizations.delegate],
          supportedLocales: AppLocalizations.supportedLocales,
          home: UserManagementScreen(),
        ),
      ),
    );

    // Initial state is loading
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('UserManagementScreen shows user list when data is available', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            () => FakeAuthController(Stream.value(testUser)),
          ),
          orgUsersProvider(
            testOrgId,
          ).overrideWith((ref) async => [testUser, testUser2]),
        ],
        child: const MaterialApp(
          localizationsDelegates: [AppLocalizations.delegate],
          supportedLocales: AppLocalizations.supportedLocales,
          home: UserManagementScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    expect(find.text('Organization Members'), findsOneWidget);
    expect(find.byType(UserListItem), findsNWidgets(2));

    // Check if texts are found.
    expect(find.text('admin@example.com'), findsOneWidget);
    expect(find.text('member@example.com'), findsOneWidget);
  });

  testWidgets('UserManagementScreen opens RoleSelectorDialog on edit', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authControllerProvider.overrideWith(
            () => FakeAuthController(Stream.value(testUser)),
          ),
          orgUsersProvider(
            testOrgId,
          ).overrideWith((ref) async => [testUser, testUser2]),
        ],
        child: const MaterialApp(
          localizationsDelegates: [AppLocalizations.delegate],
          supportedLocales: AppLocalizations.supportedLocales,
          home: UserManagementScreen(),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Tap the edit action. Use byIcon to support both mobile (IconButton) and desktop (OutlinedButton)
    final editIcons = find.byIcon(Icons.edit);
    expect(editIcons, findsOneWidget);

    await tester.tap(editIcons.first);
    await tester.pumpAndSettle();

    expect(find.byType(RoleSelectorDialog), findsOneWidget);
  });
}
