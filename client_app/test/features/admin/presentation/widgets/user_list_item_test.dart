import 'package:client_app/features/admin/presentation/widgets/user_list_item.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

// Fake AuthController to mock the provider
class FakeAuthController extends AuthController {
  final User? initialUser;
  FakeAuthController({this.initialUser});

  @override
  Stream<User?> build() {
    return Stream.value(initialUser);
  }
}

void main() {
  Widget createSubject({
    required User user,
    VoidCallback? onEdit,
    VoidCallback? onDelete,
    String? currentUserId,
    double width = 800,
  }) {
    User? authenticatedUser;
    if (currentUserId != null) {
      authenticatedUser = User(
        uid: currentUserId,
        email: 'auth@example.com',
        role: UserRole.admin,
        displayName: 'Auth User',
      );
    }

    return ProviderScope(
      overrides: [
        authControllerProvider.overrideWith(() {
          return FakeAuthController(initialUser: authenticatedUser);
        }),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: Center(
            child: SizedBox(
              width: width,
              child: UserListItem(
                user: user,
                onEdit: onEdit,
                onDelete: onDelete,
              ),
            ),
          ),
        ),
      ),
    );
  }

  const tUser = User(
    uid: 'target-user',
    email: 'target@test.com',
    role: UserRole.member,
    displayName: 'Target User',
  );

  group('UserListItem', () {
    testWidgets('renders Desktop layout when width > 600', (tester) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user',
          width: 800,
          onEdit: () {},
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Target User'), findsOneWidget);
      expect(find.text('target@test.com'), findsOneWidget);
      expect(find.text('MEMBER'), findsOneWidget);
      expect(find.byType(ListTile), findsNothing);
    });

    testWidgets('renders Mobile layout when width < 600', (tester) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user',
          width: 400,
          onEdit: () {},
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(ListTile), findsOneWidget);
      expect(find.text('Target User'), findsOneWidget);
      expect(
        find.textContaining('Role: MEMBER', findRichText: true),
        findsOneWidget,
      );
    });

    testWidgets('shows actions menu when current user is NOT target user', (
      tester,
    ) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user', // Different ID
          onEdit: () {},
          width: 800,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.more_vert), findsOneWidget);
    });

    testWidgets(
      'hides actions menu when current user IS target user (Safety)',
      (tester) async {
        await tester.pumpWidget(
          createSubject(
            user: tUser,
            currentUserId: 'target-user', // Same ID
            onEdit: () {},
            width: 800,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.more_vert), findsNothing);
      },
    );

    testWidgets('hides actions menu when onEdit is null (view only)', (
      tester,
    ) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user',
          onEdit: null, // No callback
          width: 800,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.more_vert), findsNothing);
    });
  });
}
