import 'package:client_app/features/admin/presentation/widgets/user_list_item.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/auth_provider.dart';
import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([firebase_auth.User])
import 'user_list_item_test.mocks.dart';

void main() {
  late MockUser mockFirebaseUser;

  setUp(() {
    mockFirebaseUser = MockUser();
  });

  Widget createSubject({
    required User user,
    VoidCallback? onEditRole,
    String? currentUserId,
    double width = 800,
  }) {
    if (currentUserId != null) {
      when(mockFirebaseUser.uid).thenReturn(currentUserId);
    }

    return ProviderScope(
      overrides: [
        authStateProvider.overrideWith((ref) {
          return Stream.value(currentUserId != null ? mockFirebaseUser : null);
        }),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: Center(
            child: SizedBox(
              width: width,
              child: UserListItem(user: user, onEditRole: onEditRole),
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
          onEditRole: () {},
        ),
      );
      await tester.pumpAndSettle();

      // Row structure checks
      // expect(find.byType(Row), findsOneWidget); // Fragile invalid check
      expect(find.text('Target User'), findsOneWidget);
      expect(find.text('target@test.com'), findsOneWidget);
      expect(find.text('MEMBER'), findsOneWidget); // Role chip
      // Mobile specific widgets should be absent
      expect(find.byType(ListTile), findsNothing);
    });

    testWidgets('renders Mobile layout when width < 600', (tester) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user',
          width: 400,
          onEditRole: () {},
        ),
      );
      await tester.pumpAndSettle();

      // Mobile structure checks
      expect(find.byType(ListTile), findsOneWidget);
      expect(find.text('Target User'), findsOneWidget);
      // Ensure role is in subtitle
      expect(
        find.textContaining('Rooli: MEMBER', findRichText: true),
        findsNothing,
      ); // Finnish check if locale defaults?
      // Actually standard test environment usually defaults to en_US.
      // Let's check for the Role label key resolution to safe English default
      expect(
        find.textContaining('Role: MEMBER', findRichText: true),
        findsOneWidget,
      );
    });

    testWidgets('shows edit button when current user is NOT target user', (
      tester,
    ) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user', // Different ID
          onEditRole: () {},
          width: 800,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.edit), findsOneWidget);
    });

    testWidgets('hides edit button when current user IS target user (Safety)', (
      tester,
    ) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'target-user', // Same ID
          onEditRole: () {},
          width: 800,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.edit), findsNothing);
    });

    testWidgets('hides edit button when onEditRole is null', (tester) async {
      await tester.pumpWidget(
        createSubject(
          user: tUser,
          currentUserId: 'admin-user',
          onEditRole: null, // No callback
          width: 800,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.edit), findsNothing);
    });
  });
}
