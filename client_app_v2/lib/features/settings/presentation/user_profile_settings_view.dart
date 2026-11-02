import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

/// Displays user identity, read-only tenant attributes, UI preferences, and session security controls.
class UserProfileSettingsView extends HookConsumerWidget {
  const UserProfileSettingsView({super.key});

  static const double _mediumBreakpoint = 800.0;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final authState = ref.watch(authControllerProvider);

    return AppErrorBoundary(
      child: Scaffold(
        appBar: AppBar(title: Text(l10n.profileViewTitle)),
        body: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: switch (authState) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
              ),
              AsyncData(:final value) =>
                value == null
                    ? Center(child: Text(l10n.errorUnauthorized))
                    : _ProfileBody(
                        user: value,
                        l10n: l10n,
                        theme: theme,
                        mediumBreakpoint: _mediumBreakpoint,
                      ),
            },
          ),
        ),
      ),
    );
  }
}

class _ProfileBody extends HookConsumerWidget {
  final User user;
  final AppLocalizations l10n;
  final ThemeData theme;
  final double mediumBreakpoint;

  const _ProfileBody({
    required this.user,
    required this.l10n,
    required this.theme,
    required this.mediumBreakpoint,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nameController = useTextEditingController(text: user.name ?? '');
    final emailController = useTextEditingController(text: user.email);
    final orgIdController = useTextEditingController(
      text: user.organizationId ?? '',
    );
    final selectedLanguage = useState<String>(user.language ?? 'en');
    final selectedThemeMode = useState<String>(user.themeMode ?? 'system');
    final saveMutation = useMutation<void>();
    final signOutMutation = useMutation<void>();

    useEffect(() {
      nameController.text = user.name ?? '';
      emailController.text = user.email;
      orgIdController.text = user.organizationId ?? '';
      selectedLanguage.value = user.language ?? 'en';
      selectedThemeMode.value = user.themeMode ?? 'system';
      return null;
    }, [user.id, user.name, user.language, user.themeMode]);

    Future<void> saveProfile() async {
      final previousUser = user;
      final trimmedName = nameController.text.trim();
      final nextName = trimmedName.isEmpty ? null : trimmedName;
      final nextLanguage = selectedLanguage.value;
      final nextTheme = selectedThemeMode.value;

      final optimisticUser = user.copyWith(
        name: nextName,
        language: nextLanguage,
        themeMode: nextTheme,
      );

      await saveMutation.mutate(() async {
        // Optimistic UI update across AuthController and SettingsController
        ref
            .read(authControllerProvider.notifier)
            .setOptimisticUser(optimisticUser);
        await ref
            .read(settingsControllerProvider.notifier)
            .syncFromUserProfile(language: nextLanguage, themeMode: nextTheme);

        final result = await ref
            .read(userRepositoryProvider)
            .updateUser(
              user.id,
              UserUpdate(
                name: nextName,
                language: nextLanguage,
                themeMode: nextTheme,
              ),
            );

        await result.fold(
          (error) async {
            // Rollback optimistic update on failure
            ref
                .read(authControllerProvider.notifier)
                .setOptimisticUser(previousUser);
            await ref
                .read(settingsControllerProvider.notifier)
                .syncFromUserProfile(
                  language: previousUser.language,
                  themeMode: previousUser.themeMode,
                );
            if (context.mounted) {
              final hint = AppExceptionX.extractLocalizedHint(error, l10n);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(hint),
                  backgroundColor: theme.colorScheme.error,
                ),
              );
            }
            throw error;
          },
          (updatedUser) async {
            ref
                .read(authControllerProvider.notifier)
                .setOptimisticUser(updatedUser);
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(l10n.profileUpdatedSuccess)),
              );
            }
          },
        );
      });
    }

    Widget buildIdentityAndPreferencesCard() {
      return Card(
        key: const Key('profile_identity_card'),
        elevation: 2,
        margin: const EdgeInsets.only(bottom: AppSpacing.s16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
        ),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            key: const Key('profile_preferences_card'),
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      l10n.profileIdentityCardTitle,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    key: const Key('profile_role_badge'),
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.s12,
                      vertical: AppSpacing.s4,
                    ),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(AppSpacing.s12),
                    ),
                    child: Text(
                      _roleLabel(user.role),
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: theme.colorScheme.onPrimaryContainer,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              AppSpacing.h8,
              Text(
                user.email,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              AppSpacing.h16,
              Wrap(
                spacing: AppSpacing.s8,
                runSpacing: AppSpacing.s8,
                children: [
                  Container(
                    key: const Key('profile_mfa_verified_badge'),
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.s12,
                      vertical: AppSpacing.s4,
                    ),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.secondaryContainer,
                      borderRadius: BorderRadius.circular(AppSpacing.s12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.verified_user_outlined,
                          size: AppSpacing.s16,
                          color: theme.colorScheme.onSecondaryContainer,
                        ),
                        AppSpacing.w4,
                        Text(
                          l10n.profileMfaVerifiedBadge,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.onSecondaryContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              AppSpacing.h16,
              TextFormField(
                key: const Key('profile_email_readonly_field'),
                controller: emailController,
                readOnly: true,
                decoration: InputDecoration(
                  labelText: l10n.emailLabel,
                  prefixIcon: const Icon(Icons.email_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              AppSpacing.h12,
              TextFormField(
                key: const Key('profile_org_id_readonly_field'),
                controller: orgIdController,
                readOnly: true,
                decoration: InputDecoration(
                  labelText: l10n.profileOrganizationIdLabel,
                  prefixIcon: const Icon(Icons.business_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              AppSpacing.h16,
              const Divider(),
              AppSpacing.h12,
              Text(
                l10n.profilePreferencesCardTitle,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              AppSpacing.h12,
              TextFormField(
                key: const Key('profile_display_name_field'),
                controller: nameController,
                decoration: InputDecoration(
                  labelText: l10n.profileDisplayNameLabel,
                  prefixIcon: const Icon(Icons.badge_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              AppSpacing.h16,
              DropdownButtonFormField<String>(
                key: const Key('profile_language_dropdown'),
                isExpanded: true,
                initialValue:
                    (selectedLanguage.value == 'fi' ||
                        selectedLanguage.value == 'en')
                    ? selectedLanguage.value
                    : 'en',
                decoration: InputDecoration(
                  labelText: l10n.profileUiLanguageLabel,
                  prefixIcon: const Icon(Icons.language_outlined),
                  border: const OutlineInputBorder(),
                ),
                items: [
                  for (final lang in const ['fi', 'en'])
                    DropdownMenuItem(
                      value: lang,
                      child: Text(lang.toUpperCase()),
                    ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    selectedLanguage.value = val;
                  }
                },
              ),
              AppSpacing.h16,
              DropdownButtonFormField<String>(
                key: const Key('profile_theme_dropdown'),
                isExpanded: true,
                initialValue:
                    (selectedThemeMode.value == 'light' ||
                        selectedThemeMode.value == 'dark' ||
                        selectedThemeMode.value == 'system')
                    ? selectedThemeMode.value
                    : 'system',
                decoration: InputDecoration(
                  labelText: l10n.profileThemeModeLabel,
                  prefixIcon: const Icon(Icons.brightness_6_outlined),
                  border: const OutlineInputBorder(),
                ),
                items: [
                  DropdownMenuItem(
                    value: 'system',
                    child: Text(
                      l10n.profileThemeSystem,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'light',
                    child: Text(
                      l10n.profileThemeLight,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  DropdownMenuItem(
                    value: 'dark',
                    child: Text(
                      l10n.profileThemeDark,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
                onChanged: (val) {
                  if (val != null) {
                    selectedThemeMode.value = val;
                  }
                },
              ),
              AppSpacing.h16,
              if (saveMutation.hasError) ...[
                ErrorView(error: saveMutation.error!, compact: true),
                AppSpacing.h12,
              ],
              OutlinedButton.icon(
                key: const Key('profile_save_preferences_btn'),
                onPressed: saveMutation.isLoading ? null : saveProfile,
                icon: const Icon(Icons.save_outlined),
                label: Text(l10n.profileSaveNameBtn),
              ),
            ],
          ),
        ),
      );
    }

    Widget buildSessionAndSecurityCard() {
      return Card(
        key: const Key('profile_session_card'),
        elevation: 2,
        margin: const EdgeInsets.only(bottom: AppSpacing.s16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
        ),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                l10n.profileSessionSecurityCardTitle,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              AppSpacing.h16,
              OutlinedButton.icon(
                key: const Key('profile_sign_out_btn'),
                onPressed: signOutMutation.isLoading
                    ? null
                    : () => signOutMutation.mutate(() async {
                        await ref
                            .read(authControllerProvider.notifier)
                            .signOut(revokeAllSessions: false);
                      }),
                icon: const Icon(Icons.logout),
                label: Text(l10n.signOutBtn),
              ),
              AppSpacing.h12,
              TextButton.icon(
                key: const Key('profile_sign_out_all_devices_btn'),
                onPressed: signOutMutation.isLoading
                    ? null
                    : () => signOutMutation.mutate(() async {
                        await ref
                            .read(authControllerProvider.notifier)
                            .signOut(revokeAllSessions: true);
                      }),
                icon: const Icon(Icons.phonelink_erase),
                label: Text(l10n.signOutAllDevicesBtn),
              ),
            ],
          ),
        ),
      );
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= mediumBreakpoint;
        return SingleChildScrollView(
          padding: AppSpacing.p24,
          child: isWide
              ? Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 1, child: buildIdentityAndPreferencesCard()),
                    AppSpacing.w16,
                    Expanded(flex: 1, child: buildSessionAndSecurityCard()),
                  ],
                )
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    buildIdentityAndPreferencesCard(),
                    buildSessionAndSecurityCard(),
                  ],
                ),
        );
      },
    );
  }

  String _roleLabel(UserRole role) => switch (role) {
    UserRole.root => 'ROOT',
    UserRole.admin => 'ADMIN',
    UserRole.manager => 'MANAGER',
    UserRole.member => 'MEMBER',
    UserRole.viewer => 'VIEWER',
    UserRole.unknown => 'UNKNOWN',
  };
}
