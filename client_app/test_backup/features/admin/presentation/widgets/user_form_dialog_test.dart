import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';
import 'package:client_app/features/admin/presentation/widgets/user_form_dialog.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/mock_user_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// Explaining the "Fake Values" question:
// Q: "Do we need mock values if we test with a fake DB?"
// A: Yes, for WIDGET tests like this one. We want to test the UI logic in isolation
//    without spinning up the backend (real or fake). This ensures tests are fast and flaky-free.
//    For INTEGRATION tests, we would use the real Repository + Fake DB.

class MockAdminRepository extends Mock implements AdminRepository {}

// Fake implementation of MockUser to inject auth state
class FakeMockUser extends MockUser {
  final User? initial;
  FakeMockUser(this.initial);
  @override
  User? build() => initial;
}

void main() {
  late MockAdminRepository mockRepo;

  setUpAll(() {
    registerFallbackValue(
      UserCreateDto(
        email: 'fallback@example.com',
        password: 'password',
        displayName: 'Fallback',
        role: UserRole.member,
      ),
    );
    registerFallbackValue(
      UserUpdateDto(displayName: 'Fallback', role: UserRole.member),
    );
  });

  setUp(() {
    mockRepo = MockAdminRepository();
    // Default stubs to prevent UI crashes
    when(
      () => mockRepo.fetchAssignableRoles(),
    ).thenAnswer((_) async => const Right(UserRole.values));
  });

  Widget createSubject({User? user}) {
    return ProviderScope(
      overrides: [
        adminRepositoryProvider.overrideWith((ref) => mockRepo),
        // Override mockUserProvider to safely control AuthController state
        // This prevents the real AuthController from trying to reach Firebase
        mockUserProvider.overrideWith(() => FakeMockUser(user)),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: Builder(
            builder: (context) {
              return ElevatedButton(
                onPressed: () {
                  showDialog<void>(
                    context: context,
                    builder: (c) => UserFormDialog(orgId: 'org-1', user: user),
                  );
                },
                child: const Text('Show Dialog'),
              );
            },
          ),
        ),
      ),
    );
  }

  group('UserFormDialog', () {
    testWidgets('renders Create mode correctly', (tester) async {
      await tester.pumpWidget(createSubject());
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      // "Create User" is the actual string from app_en.arb (key: createUser)
      expect(find.text('Create User'), findsOneWidget);
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Display Name'), findsOneWidget);
      expect(find.text('Password'), findsOneWidget);
      expect(find.text('Role'), findsOneWidget);
      expect(find.text('Save'), findsOneWidget);
    });

    testWidgets('renders Edit mode correctly', (tester) async {
      const user = User(
        uid: 'user-1',
        email: 'test@example.com',
        displayName: 'Existing User',
        role: UserRole.member,
      );

      await tester.pumpWidget(createSubject(user: user));
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      expect(find.text('Edit User'), findsOneWidget);
      expect(find.text('Existing User'), findsOneWidget);
      expect(find.text('test@example.com'), findsOneWidget);
      expect(find.text('Password'), findsNothing);
      expect(find.text('Save'), findsOneWidget);
    });

    testWidgets('calls createUser on submit in Create mode', (tester) async {
      when(
        () => mockRepo.createUser(any()),
      ).thenAnswer((_) async => const Right(null));

      await tester.pumpWidget(createSubject());
      await tester.tap(find.text('Show Dialog'));
      await tester.pumpAndSettle();

      await tester.enterText(
        find.widgetWithText(TextFormField, 'Email'),
        'new@example.com',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Display Name'),
        'New User',
      );
      await tester.enterText(
        find.widgetWithText(TextFormField, 'Password'),
        'password123',
      );

      await tester.tap(find.text('Save'));
      await tester.pumpAndSettle();

      // Verify with Explicit DTO to avoid 'any()' matcher issues
      final expectedDto = UserCreateDto(
        email: 'new@example.com',
        password: 'password123',
        displayName: 'New User',
        role: UserRole.member,
        organizationId: 'org-1',
      );

      verify(() => mockRepo.createUser(expectedDto)).called(1);
    });
  });
}
