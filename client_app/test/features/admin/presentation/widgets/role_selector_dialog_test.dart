import 'package:client_app/features/admin/presentation/widgets/role_selector_dialog.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/admin/presentation/providers/admin_providers.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'dart:async';

// Removed GenerateMocks to avoid build_runner dependency for this simple fake
// import 'role_selector_dialog_test.mocks.dart';

// Using a Fake is clearer for implementation inheritance
class FakeUserRoleController extends AsyncNotifier<void>
    implements UserRoleController {
  @override
  FutureOr<void> build() {}

  @override
  Future<bool> updateRole({
    required String orgId,
    required String userId,
    required UserRole newRole,
  }) async {
    // Mimic successful update
    return true;
  }
}

void main() {
  const tUserAdmin = User(
    uid: 'admin-1',
    email: 'admin@test.com',
    role: UserRole.admin,
    displayName: 'Admin User',
  );

  const tUserMember = User(
    uid: 'member-1',
    email: 'member@test.com',
    role: UserRole.member,
    displayName: 'Member User',
  );

  Widget createSubject(User user, {UserRoleController? mockController}) {
    return ProviderScope(
      overrides: [
        userRoleControllerProvider.overrideWith(
          () => mockController ?? FakeUserRoleController(),
        ),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: Builder(
            builder:
                (context) => ElevatedButton(
                  onPressed: () {
                    showDialog<void>(
                      context: context,
                      builder:
                          (ctx) =>
                              RoleSelectorDialog(user: user, orgId: 'org-1'),
                    );
                  },
                  child: const Text('Open Dialog'),
                ),
          ),
        ),
      ),
    );
  }

  group('RoleSelectorDialog', () {
    testWidgets('shows all roles', (tester) async {
      await tester.pumpWidget(createSubject(tUserMember));
      await tester.tap(find.text('Open Dialog'));
      await tester.pumpAndSettle();

      expect(find.text('ADMIN'), findsOneWidget);
      expect(find.text('MEMBER'), findsOneWidget);
      expect(
        find.text('ROOT'),
        findsWidgets,
      ); // Might appear multiple times? No, unique keys.
    });

    testWidgets('selects current role initially', (tester) async {
      await tester.pumpWidget(createSubject(tUserMember));
      await tester.tap(find.text('Open Dialog'));
      await tester.pumpAndSettle();

      final radioFinder = find.byWidgetPredicate(
        (widget) =>
            // ignore: deprecated_member_use
            widget is Radio<UserRole> &&
            // ignore: deprecated_member_use
            widget.groupValue == UserRole.member &&
            widget.value == UserRole.member,
      );
      expect(radioFinder, findsOneWidget);
    });

    testWidgets('shows warning when demoting Admin -> Member', (tester) async {
      await tester.pumpWidget(createSubject(tUserAdmin));
      await tester.tap(find.text('Open Dialog'));
      await tester.pumpAndSettle();

      // Initial state: Admin selected. Warning should NOT be there.
      expect(find.textContaining('Warning:'), findsNothing);

      // Select Member
      await tester.tap(find.text('MEMBER'));
      await tester.pump();

      // Warning should appear
      expect(find.textContaining('Warning:'), findsOneWidget);
      // Check for specific localized text part if possible, or key substring
      expect(find.textContaining('Admin'), findsOneWidget);
    });

    testWidgets('does NOT show warning when promoting Member -> Admin', (
      tester,
    ) async {
      await tester.pumpWidget(createSubject(tUserMember));
      await tester.tap(find.text('Open Dialog'));
      await tester.pumpAndSettle();

      // Select Admin
      await tester.tap(find.text('ADMIN'));
      await tester.pump();

      expect(find.textContaining('Warning:'), findsNothing);
    });

    // We skip deep mocking verification of the controller method call in Widget tests
    // unless we use a Mockito mock. Using a custom subclass above is easier for "fake" behavior.
  });
}
