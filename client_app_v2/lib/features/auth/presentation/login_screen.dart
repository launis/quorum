import 'package:client_app/core/environment/env.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

class LoginScreen extends HookConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final emailController = useTextEditingController();
    final passwordController = useTextEditingController();
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    // Mandate 5.4: Riverpod 3.0 Mutation Object handles side effects natively without manual bool flags
    final loginMutation = useMutation<void>(
      // Success is handled by Router listening to Auth State
    );

    Future<void> submit() async {
      if (!formKey.currentState!.validate()) return;
      await loginMutation.mutate(() async {
        await ref
            .read(authControllerProvider.notifier)
            .signIn(emailController.text.trim(), passwordController.text);
      });
    }

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: AppSpacing.p24,
            child: Form(
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

                  // Standard Fail-Fast inline rendering for non-fatal auth errors
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
                    onFieldSubmitted: (_) => submit(),
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
                    action: () => submit(),
                    label: l10n.signInButton,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        vertical: AppSpacing.s16,
                      ),
                      child: Text(l10n.signInButton),
                    ),
                  ),

                  // Debug Feature: Mock Login
                  if (Env.allowMockTokens) ...[
                    AppSpacing.h24,
                    const MockLoginPanel(),
                  ],
                ],
              ),
            ),
          ),
        ),
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
          String msg = e.toString().replaceAll('Exception: ', '');
          if (e is AppException) {
            msg = e.toLocalizedHint(l10n);
          }
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
              : () => mockLogin(
                  Env.mockRootUserId, // ROOT
                ),
          child: Text(l10n.mockLoginRootMasterBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: semanticColors.warning),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(
                  Env.mockAdminUserId, // ADMIN
                ),
          child: Text(l10n.mockLoginAdminBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: semanticColors.success),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(
                  Env.mockAnalystUserId, // ANALYST
                ),
          child: Text(l10n.mockLoginAnalystBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.primary,
          ),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(
                  Env.mockMemberUserId, // MEMBER
                ),
          child: Text(l10n.mockLoginMemberBtn),
        ),
        TextButton(
          style: TextButton.styleFrom(
            foregroundColor: theme.colorScheme.onSurfaceVariant,
          ),
          onPressed: isMockLoading.value
              ? null
              : () => mockLogin(
                  Env.mockViewerUserId, // VIEWER
                ),
          child: Text(l10n.mockLoginViewerBtn),
        ),
      ],
    );
  }
}
