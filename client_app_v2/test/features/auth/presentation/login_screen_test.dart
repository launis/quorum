import 'dart:async';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/presentation/login_screen.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations_en.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAuthController extends AuthController {
  String? lastSignInEmail;
  String? lastSignInPassword;
  String? lastChallengeTotp;
  String? lastEnrollmentTotp;
  String? lastMockLoginId;
  bool cancelledMfa = false;
  AppException? errorToThrow;

  @override
  FutureOr<User?> build() async => null;

  @override
  Future<void> signIn(String email, String password) async {
    lastSignInEmail = email;
    lastSignInPassword = password;
    if (errorToThrow != null) throw errorToThrow!;
  }

  @override
  Future<void> verifyMfaChallenge(String totpCode) async {
    lastChallengeTotp = totpCode;
    if (errorToThrow != null) throw errorToThrow!;
  }

  @override
  Future<void> completeMfaEnrollment(String totpCode) async {
    lastEnrollmentTotp = totpCode;
    if (errorToThrow != null) throw errorToThrow!;
  }

  @override
  Future<void> cancelMfaFlow() async {
    cancelledMfa = true;
    ref.read(mfaSessionControllerProvider.notifier).reset();
  }

  @override
  Future<void> debugMockLogin(String id) async {
    lastMockLoginId = id;
    if (errorToThrow != null) throw errorToThrow!;
  }
}

void main() {
  final l10n = AppLocalizationsEn();
  final mockRootId = generateOpaqueUuid7('usr');
  final mockAdminId = generateOpaqueUuid7('usr');
  final mockAnalystId = generateOpaqueUuid7('usr');
  final mockMemberId = generateOpaqueUuid7('usr');
  final mockViewerId = generateOpaqueUuid7('usr');

  setUp(() {
    dotenv.loadFromString(
      envString:
          'ENVIRONMENT=development\n'
          'MOCK_ROOT_USER_ID=$mockRootId\n'
          'MOCK_ADMIN_USER_ID=$mockAdminId\n'
          'MOCK_ANALYST_USER_ID=$mockAnalystId\n'
          'MOCK_MEMBER_USER_ID=$mockMemberId\n'
          'MOCK_VIEWER_USER_ID=$mockViewerId\n',
    );
  });

  Widget buildTestApp({required _FakeAuthController authController}) {
    return ProviderScope(
      overrides: [authControllerProvider.overrideWith(() => authController)],
      child: const MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: LoginScreen(),
      ),
    );
  }

  group('LoginScreen & MockLoginPanel Widget & ISTQB Boundary Tests', () {
    testWidgets(
      'Positive 1: renders primary login form and MockLoginPanel, submits trimmed email/password, and executes mock login',
      (WidgetTester tester) async {
        final fakeAuth = _FakeAuthController();
        await tester.pumpWidget(buildTestApp(authController: fakeAuth));
        await tester.pumpAndSettle();

        expect(find.text(l10n.loginBrandTitle), findsOneWidget);
        expect(find.text(l10n.signInSubtitle), findsOneWidget);
        expect(find.byType(TextFormField), findsNWidgets(3));

        // Enter valid email with surrounding whitespace and password
        final fields = find.byType(TextFormField);
        await tester.enterText(fields.at(0), '  coach@quorum.ai  ');
        await tester.enterText(fields.at(1), 'SecretPass123!');
        await tester.tap(find.text(l10n.signInButton));
        await tester.pumpAndSettle();

        expect(fakeAuth.lastSignInEmail, equals('coach@quorum.ai'));
        expect(fakeAuth.lastSignInPassword, equals('SecretPass123!'));

        // Verify Mock Login buttons and trigger Root Master mock login
        final rootButton = find.text(l10n.mockLoginRootMasterBtn);
        await tester.ensureVisible(rootButton);
        await tester.tap(rootButton);
        await tester.pumpAndSettle();

        expect(fakeAuth.lastMockLoginId, equals(mockRootId));
        expect(find.text(l10n.mockLoginSuccess), findsOneWidget);
      },
    );

    testWidgets(
      'Positive 2: switches between MFA Challenge and MFA Enrollment forms, submits 6-digit TOTP codes, and supports cancelMfaFlow',
      (WidgetTester tester) async {
        final fakeAuth = _FakeAuthController();
        await tester.pumpWidget(buildTestApp(authController: fakeAuth));
        await tester.pumpAndSettle();

        final container = ProviderScope.containerOf(
          tester.element(find.byType(LoginScreen)),
        );

        // 1. Transition to MFA Challenge state
        container
            .read(mfaSessionControllerProvider.notifier)
            .setPendingState(
              const MfaPendingState(
                type: MfaRequirementType.challenge,
                email: 'coach@quorum.ai',
                enrollmentId: 'totp_factor_01',
              ),
            );
        await tester.pumpAndSettle();

        expect(find.text(l10n.mfaChallengeTitle), findsOneWidget);
        final challengeField = find.byKey(
          const Key('mfa_challenge_totp_field'),
        );
        expect(challengeField, findsOneWidget);

        await tester.enterText(challengeField, ' 654321 ');
        await tester.tap(find.text(l10n.mfaVerifyBtn));
        await tester.pumpAndSettle();
        expect(fakeAuth.lastChallengeTotp, equals('654321'));

        // 2. Transition to MFA Enrollment state
        container
            .read(mfaSessionControllerProvider.notifier)
            .setPendingState(
              const MfaPendingState(
                type: MfaRequirementType.enrollment,
                email: 'coach@quorum.ai',
                secretKey: 'JBSWY3DPEHPK3PXP',
                provisioningUri: 'otpauth://totp/Quorum:coach@quorum.ai',
              ),
            );
        await tester.pumpAndSettle();

        expect(find.text(l10n.mfaEnrollmentTitle), findsOneWidget);
        expect(find.text('JBSWY3DPEHPK3PXP'), findsOneWidget);
        expect(
          find.text('otpauth://totp/Quorum:coach@quorum.ai'),
          findsOneWidget,
        );

        final enrollmentTotpField = find.byKey(
          const Key('mfa_enrollment_totp_field'),
        );
        await tester.enterText(enrollmentTotpField, '123456');
        await tester.tap(find.text(l10n.mfaCompleteEnrollmentBtn));
        await tester.pumpAndSettle();
        expect(fakeAuth.lastEnrollmentTotp, equals('123456'));

        // 3. Cancel MFA flow returns to primary login form
        await tester.tap(find.text(l10n.mfaBackToLoginBtn));
        await tester.pumpAndSettle();
        expect(fakeAuth.cancelledMfa, isTrue);
        expect(find.text(l10n.loginBrandTitle), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1 (Form Validation & ISTQB BVA): rejects empty/malformed email, empty password, and 5-digit (min-1) or 7-digit (max+1) TOTP codes',
      (WidgetTester tester) async {
        final fakeAuth = _FakeAuthController();
        await tester.pumpWidget(buildTestApp(authController: fakeAuth));
        await tester.pumpAndSettle();

        // 1. Submit empty primary form
        await tester.tap(find.text(l10n.signInButton));
        await tester.pumpAndSettle();

        expect(find.text(l10n.errorEmptyEmail), findsOneWidget);
        expect(find.text(l10n.errorEmptyPassword), findsOneWidget);
        expect(fakeAuth.lastSignInEmail, isNull);

        // 2. Submit email missing '@' symbol
        final fields = find.byType(TextFormField);
        await tester.enterText(fields.at(0), 'invalid-email-format');
        await tester.enterText(fields.at(1), 'ValidPass123!');
        await tester.tap(find.text(l10n.signInButton));
        await tester.pumpAndSettle();

        expect(find.text(l10n.errorInvalidEmail), findsOneWidget);
        expect(fakeAuth.lastSignInEmail, isNull);

        // 3. ISTQB BVA on MFA Challenge TOTP field: 5 digits (min-1) and 7 digits (max+1)
        final container = ProviderScope.containerOf(
          tester.element(find.byType(LoginScreen)),
        );
        container
            .read(mfaSessionControllerProvider.notifier)
            .setPendingState(
              const MfaPendingState(
                type: MfaRequirementType.challenge,
                email: 'coach@quorum.ai',
              ),
            );
        await tester.pumpAndSettle();

        final challengeField = find.byKey(
          const Key('mfa_challenge_totp_field'),
        );
        await tester.enterText(challengeField, '12345');
        await tester.tap(find.text(l10n.mfaVerifyBtn));
        await tester.pumpAndSettle();
        expect(find.text(l10n.mfaTotpCodeError), findsOneWidget);
        expect(fakeAuth.lastChallengeTotp, isNull);

        await tester.enterText(challengeField, '1234567');
        await tester.tap(find.text(l10n.mfaVerifyBtn));
        await tester.pumpAndSettle();
        expect(find.text(l10n.mfaTotpCodeError), findsOneWidget);
        expect(fakeAuth.lastChallengeTotp, isNull);
      },
    );

    testWidgets(
      'Negative 2 (Runtime Auth Exceptions): renders ErrorView on signIn failure and localized SnackBar on MockLoginPanel failure',
      (WidgetTester tester) async {
        final fakeAuth = _FakeAuthController()
          ..errorToThrow = AppException.unauthorized();
        await tester.pumpWidget(buildTestApp(authController: fakeAuth));
        await tester.pumpAndSettle();

        // 1. Trigger primary login error -> renders ErrorView
        final fields = find.byType(TextFormField);
        await tester.enterText(fields.at(0), 'coach@quorum.ai');
        await tester.enterText(fields.at(1), 'wrong-pass');
        await tester.tap(find.text(l10n.signInButton));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);

        // 2. Trigger MockLoginPanel error -> shows localized SnackBar via AppExceptionX.extractLocalizedHint
        final adminButton = find.text(l10n.mockLoginAdminBtn);
        await tester.ensureVisible(adminButton);
        await tester.tap(adminButton);
        await tester.pumpAndSettle();

        expect(find.byType(SnackBar), findsOneWidget);
        expect(
          find.text(l10n.mockLoginFailed(l10n.errorUnauthorized)),
          findsOneWidget,
        );
      },
    );
  });
}
