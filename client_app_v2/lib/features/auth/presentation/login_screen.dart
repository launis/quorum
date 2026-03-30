import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/ui/error_view.dart';

class LoginScreen extends HookConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final emailController = useTextEditingController();
    final passwordController = useTextEditingController();
    final mockIdController = useTextEditingController();
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    // Mandate 5.4: Riverpod 3.0 Mutation Object handles side effects natively without manual bool flags
    final loginMutation = useMutation<void>(
      // Success is handled by Router listening to Auth State
    );

    // Mock login state since it's a dev tool explicitly ignored from refactoring rules
    final isMockLoading = useState(false);

    Future<void> submit() async {
      if (!formKey.currentState!.validate()) return;
      await loginMutation.mutate(() async {
        await ref
            .read(authControllerProvider.notifier)
            .signIn(emailController.text.trim(), passwordController.text);
      });
    }

    Future<void> mockLogin(String id) async {
      isMockLoading.value = true;
      try {
        await ref.read(authControllerProvider.notifier).debugMockLogin(id);
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Mock Login Successful! Redirecting...'),
            ),
          );
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

    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: const EdgeInsets.all(24),
            child: Form(
              key: formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Cognitive Quorum',
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.primary,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    l10n.signInSubtitle,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),

                  // Standard Fail-Fast inline rendering for non-fatal auth errors
                  if (loginMutation.hasError) ...[
                    ErrorView(error: loginMutation.error!, compact: true),
                    const SizedBox(height: 16),
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
                  const SizedBox(height: 16),
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
                  const SizedBox(height: 24),

                  MutationButton<void>(
                    mutation: loginMutation,
                    action: () => submit(),
                    label: l10n.signInButton,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      child: Text(l10n.signInButton),
                    ),
                  ),

                  // Debug Feature: Mock Login (Ignored per user constraint rule)
                  const SizedBox(height: 24),
                  Column(
                    children: [
                      const Divider(),
                      const Text(
                        'Development Tools',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: mockIdController,
                        decoration: const InputDecoration(
                          labelText: 'Custom Mock User ID',
                          border: OutlineInputBorder(),
                          isDense: true,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TextButton(
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.teal,
                        ),
                        onPressed: isMockLoading.value
                            ? null
                            : () {
                                if (mockIdController.text.isNotEmpty) {
                                  mockLogin(mockIdController.text.trim());
                                }
                              },
                        child: const Text('Mock Login (Custom ID)'),
                      ),
                      TextButton(
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.purple,
                        ),
                        onPressed: isMockLoading.value
                            ? null
                            : () => mockLogin(
                                'usr_a3fd6b3d77c748f4', // ROOT
                              ),
                        child: const Text('Mock Login (Root Master)'),
                      ),
                      TextButton(
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.orange,
                        ),
                        onPressed: isMockLoading.value
                            ? null
                            : () => mockLogin(
                                'usr_18a0d5f6151349a5', // ADMIN
                              ),
                        child: const Text('Mock Login (Admin)'),
                      ),
                      TextButton(
                        style: TextButton.styleFrom(
                          foregroundColor: Colors.green,
                        ),
                        onPressed: isMockLoading.value
                            ? null
                            : () => mockLogin(
                                'usr_936983a7a6c643ab', // MANAGER
                              ),
                        child: const Text('Mock Login (Manager)'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
