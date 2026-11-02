import 'package:client_app/core/environment/env.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Phase 6, Step 6.1: Mandatory 2FA TOTP Enrollment and 2FA Challenge resolution in LoginScreen.

class LoginScreen extends HookConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final mfaFormKey = useMemoized(() => GlobalKey<FormState>());
    final emailController = useTextEditingController();
    final passwordController = useTextEditingController();
    final totpCodeController = useTextEditingController();
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final mfaState = ref.watch(mfaSessionControllerProvider);

    final loginMutation = useMutation<void>();

    Future<void> submitPrimary() async {
      if (!formKey.currentState!.validate()) return;
      await loginMutation.mutate(() async {
        await ref
            .read(authControllerProvider.notifier)
            .signIn(emailController.text.trim(), passwordController.text);
      });
    }

    Future<void> submitMfaChallenge() async {
      if (!mfaFormKey.currentState!.validate()) return;
      await loginMutation.mutate(() async {
        await ref
            .read(authControllerProvider.notifier)
            .verifyMfaChallenge(totpCodeController.text.trim());
      });
    }

    Future<void> submitMfaEnrollment() async {
      if (!mfaFormKey.currentState!.validate()) return;
      await loginMutation.mutate(() async {
        await ref
            .read(authControllerProvider.notifier)
            .completeMfaEnrollment(totpCodeController.text.trim());
      });
    }

    return AppErrorBoundary(
      child: Scaffold(
        body: Center(
          child: SingleChildScrollView(
            child: Container(
              constraints: const BoxConstraints(maxWidth: 440),
              padding: AppSpacing.p24,
              child: switch (mfaState.type) {
                MfaRequirementType.challenge => _buildMfaChallengeForm(
                  context: context,
                  ref: ref,
                  formKey: mfaFormKey,
                  totpController: totpCodeController,
                  mutation: loginMutation,
                  onSubmit: submitMfaChallenge,
                  l10n: l10n,
                  theme: theme,
                ),
                MfaRequirementType.enrollment => _buildMfaEnrollmentForm(
                  context: context,
                  ref: ref,
                  formKey: mfaFormKey,
                  mfaState: mfaState,
                  totpController: totpCodeController,
                  mutation: loginMutation,
                  onSubmit: submitMfaEnrollment,
                  l10n: l10n,
                  theme: theme,
                ),
                MfaRequirementType.none => Form(
                  key: formKey,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        l10n.loginBrandTitle,
                        style: theme.textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.primary,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      AppSpacing.h8,
                      Text(
                        l10n.signInSubtitle,
                        style: theme.textTheme.bodyLarge?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      AppSpacing.h24,
                      if (loginMutation.hasError) ...[
                        ErrorView(error: loginMutation.error!, compact: true),
                        AppSpacing.h16,
                      ],
                      TextFormField(
                        controller: emailController,
                        decoration: InputDecoration(
                          labelText: l10n.emailLabel,
                          prefixIcon: const Icon(Icons.email_outlined),
                          border: const OutlineInputBorder(),
                        ),
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return l10n.errorEmptyEmail;
                          }
                          if (!value.contains('@')) {
                            return l10n.errorInvalidEmail;
                          }
                          return null;
                        },
                      ),
                      AppSpacing.h16,
                      TextFormField(
                        controller: passwordController,
                        decoration: InputDecoration(
                          labelText: l10n.passwordLabel,
                          prefixIcon: const Icon(Icons.lock_outlined),
                          border: const OutlineInputBorder(),
                        ),
                        obscureText: true,
                        textInputAction: TextInputAction.done,
                        onFieldSubmitted: (_) => submitPrimary(),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return l10n.errorEmptyPassword;
                          }
                          return null;
                        },
                      ),
                      AppSpacing.h24,
                      MutationButton<void>(
                        mutation: loginMutation,
                        action: submitPrimary,
                        label: l10n.signInButton,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(
                            vertical: AppSpacing.s16,
                          ),
                          child: Text(l10n.signInButton),
                        ),
                      ),
                      if (Env.allowMockTokens) ...[
                        AppSpacing.h24,
                        const MockLoginPanel(),
                      ],
                    ],
                  ),
                ),
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMfaChallengeForm({
    required BuildContext context,
    required WidgetRef ref,
    required GlobalKey<FormState> formKey,
    required TextEditingController totpController,
    required MutationState<void> mutation,
    required Future<void> Function() onSubmit,
    required AppLocalizations l10n,
    required ThemeData theme,
  }) {
    return Form(
      key: formKey,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Icon(
            Icons.security_outlined,
            size: AppSpacing.s24,
            color: theme.colorScheme.primary,
          ),
          AppSpacing.h12,
          Text(
            l10n.mfaChallengeTitle,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
            textAlign: TextAlign.center,
          ),
          AppSpacing.h8,
          Text(
            l10n.mfaChallengeSubtitle,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
          AppSpacing.h24,
          if (mutation.hasError) ...[
            ErrorView(error: mutation.error!, compact: true),
            AppSpacing.h16,
          ],
          TextFormField(
            key: const Key('mfa_challenge_totp_field'),
            controller: totpController,
            decoration: InputDecoration(
              labelText: l10n.mfaTotpCodeLabel,
              prefixIcon: const Icon(Icons.pin_outlined),
              border: const OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => onSubmit(),
            validator: (value) {
              if (value == null || value.trim().length != 6) {
                return l10n.mfaTotpCodeError;
              }
              return null;
            },
          ),
          AppSpacing.h24,
          MutationButton<void>(
            mutation: mutation,
            action: onSubmit,
            label: l10n.mfaVerifyBtn,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
              child: Text(l10n.mfaVerifyBtn),
            ),
          ),
          AppSpacing.h12,
          TextButton.icon(
            onPressed: () {
              totpController.clear();
              ref.read(authControllerProvider.notifier).cancelMfaFlow();
            },
            icon: const Icon(Icons.arrow_back),
            label: Text(l10n.mfaBackToLoginBtn),
          ),
        ],
      ),
    );
  }

  Widget _buildMfaEnrollmentForm({
    required BuildContext context,
    required WidgetRef ref,
    required GlobalKey<FormState> formKey,
    required MfaPendingState mfaState,
    required TextEditingController totpController,
    required MutationState<void> mutation,
    required Future<void> Function() onSubmit,
    required AppLocalizations l10n,
    required ThemeData theme,
  }) {
    final secretKeyController = TextEditingController(
      text: mfaState.secretKey ?? '',
    );
    final provisioningUriController = TextEditingController(
      text: mfaState.provisioningUri ?? '',
    );

    return Form(
      key: formKey,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Icon(
            Icons.qr_code_scanner_outlined,
            size: AppSpacing.s24,
            color: theme.colorScheme.primary,
          ),
          AppSpacing.h12,
          Text(
            l10n.mfaEnrollmentTitle,
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.primary,
            ),
            textAlign: TextAlign.center,
          ),
          AppSpacing.h8,
          Text(
            l10n.mfaEnrollmentSubtitle,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
          AppSpacing.h16,
          if (mutation.hasError) ...[
            ErrorView(error: mutation.error!, compact: true),
            AppSpacing.h16,
          ],
          TextFormField(
            key: const Key('mfa_enrollment_secret_key_field'),
            controller: secretKeyController,
            readOnly: true,
            decoration: InputDecoration(
              labelText: l10n.mfaSecretKeyLabel,
              prefixIcon: const Icon(Icons.vpn_key_outlined),
              border: const OutlineInputBorder(),
            ),
          ),
          AppSpacing.h12,
          TextFormField(
            key: const Key('mfa_enrollment_uri_field'),
            controller: provisioningUriController,
            readOnly: true,
            decoration: InputDecoration(
              labelText: l10n.mfaProvisioningUriLabel,
              prefixIcon: const Icon(Icons.link_outlined),
              border: const OutlineInputBorder(),
            ),
          ),
          AppSpacing.h16,
          TextFormField(
            key: const Key('mfa_enrollment_totp_field'),
            controller: totpController,
            decoration: InputDecoration(
              labelText: l10n.mfaTotpCodeLabel,
              prefixIcon: const Icon(Icons.pin_outlined),
              border: const OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
            textInputAction: TextInputAction.done,
            onFieldSubmitted: (_) => onSubmit(),
            validator: (value) {
              if (value == null || value.trim().length != 6) {
                return l10n.mfaTotpCodeError;
              }
              return null;
            },
          ),
          AppSpacing.h24,
          MutationButton<void>(
            mutation: mutation,
            action: onSubmit,
            label: l10n.mfaCompleteEnrollmentBtn,
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.s16),
              child: Text(l10n.mfaCompleteEnrollmentBtn),
            ),
          ),
          AppSpacing.h12,
          TextButton.icon(
            onPressed: () {
              totpController.clear();
              ref.read(authControllerProvider.notifier).cancelMfaFlow();
            },
            icon: const Icon(Icons.arrow_back),
            label: Text(l10n.mfaBackToLoginBtn),
          ),
        ],
      ),
    );
  }
}

class MockLoginPanel extends HookConsumerWidget {
  const MockLoginPanel({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mockIdController = useTextEditingController();
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final semanticColors = context.semanticColors;
    final isMockLoading = useState(false);

    Future<void> mockLogin(String id) async {
      isMockLoading.value = true;
      try {
        await ref.read(authControllerProvider.notifier).debugMockLogin(id);
        if (context.mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.mockLoginSuccess)));
        }
      } catch (e) {
        if (context.mounted) {
          final msg = AppExceptionX.extractLocalizedHint(e, l10n);
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.mockLoginFailed(msg))));
        }
      } finally {
        if (context.mounted) isMockLoading.value = false;
      }
    }

    return Column(
      children: [
        const Divider(),
        Text(
          l10n.devToolsHeader,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        AppSpacing.h8,
        TextFormField(
          controller: mockIdController,
          decoration: InputDecoration(
            labelText: l10n.customMockUserIdLabel,
            border: const OutlineInputBorder(),
            isDense: true,
          ),
        ),
        AppSpacing.h8,
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.secondary,
          ),
          onPressed: isMockLoading.value
              ? null
              : () {
                  if (mockIdController.text.isNotEmpty) {
                    mockLogin(mockIdController.text.trim());
                  }
                },
          child: Text(l10n.mockLoginCustomIdBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.tertiary,
          ),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(Env.mockRootUserId),
          child: Text(l10n.mockLoginRootMasterBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: semanticColors.warning),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(Env.mockAdminUserId),
          child: Text(l10n.mockLoginAdminBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: semanticColors.success),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(Env.mockAnalystUserId),
          child: Text(l10n.mockLoginAnalystBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.primary,
          ),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(Env.mockMemberUserId),
          child: Text(l10n.mockLoginMemberBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.onSurfaceVariant,
          ),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(Env.mockViewerUserId),
          child: Text(l10n.mockLoginViewerBtn),
        ),
      ],
    );
  }
}
