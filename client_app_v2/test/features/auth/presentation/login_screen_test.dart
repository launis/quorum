import 'dart:async';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/presentation/login_screen.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations_en.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _FakeAuthController extends AuthController {
  String? lastSignInEmail;
  String? lastSignInPassword;
  String? lastChallengeTotp;
  String? lastEnrollmentTotp;
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
}

void main() {
  final l10n = AppLocalizationsEn();

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

  group('LoginScreen Widget & ISTQB Boundary Tests', () {
    testWidgets(
      'Positive 1: renders primary Email + Password login form and submits trimmed credentials',
      (WidgetTester tester) async {
        final fakeAuth = _FakeAuthController();
        await tester.pumpWidget(buildTestApp(authController: fakeAuth));
        await tester.pumpAndSettle();

        expect(find.text(l10n.loginBrandTitle), findsOneWidget);
        expect(find.text(l10n.signInSubtitle), findsOneWidget);
        expect(find.byType(TextFormField), findsNWidgets(2));
        expect(find.text(l10n.devToolsHeader), findsNothing);

        // Enter valid email with surrounding whitespace and password
        final fields = find.byType(TextFormField);
        await tester.enterText(fields.at(0), '  coach@quorum.ai  ');
        await tester.enterText(fields.at(1), 'SecretPass123!');
        await tester.tap(find.text(l10n.signInButton));
        await tester.pumpAndSettle();

        expect(fakeAuth.lastSignInEmail, equals('coach@quorum.ai'));
        expect(fakeAuth.lastSignInPassword, equals('SecretPass123!'));
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
      'Negative 2 (Runtime Auth Exceptions): renders ErrorView on signIn and MFA verification failures',
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

        // 2. Trigger MFA challenge error -> renders ErrorView in challenge form
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
        await tester.enterText(challengeField, '123456');
        await tester.tap(find.text(l10n.mfaVerifyBtn));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
      },
    );
  });
}
