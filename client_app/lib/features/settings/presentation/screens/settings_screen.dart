import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/settings/presentation/widgets/usage_stats_card.dart';
import 'package:client_app/features/settings/presentation/widgets/admin_limit_controls.dart';
import 'package:client_app/features/settings/theme_provider.dart';
import 'package:client_app/features/settings/locale_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final localizations = AppLocalizations.of(context)!;
    final locale = ref.watch(localeProvider);
    final authState = ref.watch(authControllerProvider);
    final user = authState.asData?.value;
    final isAdmin = user?.role == UserRole.root || user?.role == UserRole.admin;

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.settings),
        actions: [
          // Language Selector
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4.0),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<Locale>(
                value:
                    ref.watch(localeProvider).languageCode == 'fi'
                        ? const Locale('fi')
                        : const Locale('en'),
                icon: const Icon(Icons.language),
                onChanged: (Locale? newLocale) {
                  if (newLocale != null) {
                    ref.read(localeProvider.notifier).setLocale(newLocale);
                  }
                },
                items: const [
                  DropdownMenuItem(
                    value: Locale('fi'),
                     child: Text('🇫🇮 FI'),
                  ),
                  DropdownMenuItem(
                    value: Locale('en'),
                    child: Text('🇬🇧 EN'),
                  ),
                ],
              ),
            ),
          ),
          // Theme Selector
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4.0),
            child: IconButton(
              icon: Icon(
                themeMode == ThemeMode.light
                    ? Icons.light_mode
                    : themeMode == ThemeMode.dark
                        ? Icons.dark_mode
                        : Icons.brightness_auto,
              ),
              onPressed: () {
                final next =
                    themeMode == ThemeMode.system
                        ? ThemeMode.light
                        : themeMode == ThemeMode.light
                            ? ThemeMode.dark
                            : ThemeMode.system;
                ref.read(themeModeProvider.notifier).setThemeMode(next);
              },
            ),
          ),
          // User Info
          Padding(
             padding: const EdgeInsets.symmetric(horizontal: 8.0),
             child: Center(
               child: Text(
                 user?.displayName ?? "",
                 style: const TextStyle(fontWeight: FontWeight.bold),
               ),
             ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: ListView(
            children: [
              // DEBUG INFO
              if (user != null)
                ListTile(
                  title: Text('Debug: ${user.role}'),
                  subtitle: Text(
                    user.slug != null ? 'Ref: ${user.slug}' : 'Role: ${user.role.name.toUpperCase()}',
                  ),
                  tileColor: Colors.amber.withValues(alpha: 0.2),
                ),
              if (user != null) ...[
                ListTile(
                  leading: const Icon(Icons.person),
                  title: Text(user.displayName ?? 'No Name'),
                  subtitle: Text(user.email),
                  trailing: IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: () => _showEditProfileDialog(context, ref, user),
                  ),
                ),
                const Divider(),
              ],
              const UsageStatsCard(),
              const AdminLimitControls(),
              if (isAdmin) ...[
                ListTile(
                  leading: const Icon(Icons.admin_panel_settings),
                  title: Text(localizations.adminPanel),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => context.go('/admin'),
                ),
                const Divider(),
              ],
              ListTile(
                leading: const Icon(Icons.language),
                title: Text(localizations.language),
                subtitle: Text(
                  locale.languageCode == 'fi' ? 'Suomi' : 'English',
                ),
                trailing: DropdownButton<Locale>(
                  value:
                      locale.languageCode == 'fi'
                          ? const Locale('fi')
                          : const Locale('en'),
                  onChanged: (Locale? newLocale) {
                    if (newLocale != null) {
                      ref.read(localeProvider.notifier).setLocale(newLocale);
                    }
                  },
                  items: const [
                    DropdownMenuItem(
                      value: Locale('en'),
                      child: Text('English'),
                    ),
                    DropdownMenuItem(value: Locale('fi'), child: Text('Suomi')),
                  ],
                ),
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.brightness_6),
                title: Text(AppLocalizations.of(context)!.themeMode),
                subtitle: Text(_getThemeModeName(context, themeMode)),
                trailing: DropdownButton<ThemeMode>(
                  value: themeMode,
                  onChanged: (ThemeMode? newMode) {
                    if (newMode != null) {
                      ref
                          .read(themeModeProvider.notifier)
                          .setThemeMode(newMode);
                    }
                  },
                  items: [
                    DropdownMenuItem(
                      value: ThemeMode.system,
                      child: Text(AppLocalizations.of(context)!.system),
                    ),
                    DropdownMenuItem(
                      value: ThemeMode.light,
                      child: Text(AppLocalizations.of(context)!.light),
                    ),
                    DropdownMenuItem(
                      value: ThemeMode.dark,
                      child: Text(AppLocalizations.of(context)!.dark),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showEditProfileDialog(
    BuildContext context,
    WidgetRef ref,
    User user,
  ) async {
    final nameController = TextEditingController(text: user.displayName ?? '');

    await showDialog<void>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Edit Profile'),
            content: TextField(
              controller: nameController,
              decoration: const InputDecoration(labelText: 'Display Name'),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () async {
                  final newName = nameController.text.trim();
                  if (newName.isNotEmpty && newName != user.displayName) {
                    // Call Repo
                    final result = await ref
                        .read(userRepositoryProvider)
                        .updateCurrentUser(user.id, {'display_name': newName});

                    result.fold(
                      (err) => ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Update failed: $err')),
                      ),
                      (updatedUser) {
                        Navigator.of(context).pop();
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Profile updated!')),
                        );
                        // Force refresh auth state
                        ref.invalidate(authControllerProvider);
                      },
                    );
                  } else {
                    Navigator.of(context).pop();
                  }
                },
                child: const Text('Save'),
              ),
            ],
          ),
    );
  }

  String _getThemeModeName(BuildContext context, ThemeMode mode) {
    switch (mode) {
      case ThemeMode.system:
        return AppLocalizations.of(context)!.system;
      case ThemeMode.light:
        return AppLocalizations.of(context)!.light;
      case ThemeMode.dark:
        return AppLocalizations.of(context)!.dark;
    }
  }
}
