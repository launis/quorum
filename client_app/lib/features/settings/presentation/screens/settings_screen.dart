import 'package:client_app/features/settings/theme_provider.dart';
import 'package:client_app/features/settings/locale_provider.dart';
import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final localizations = AppLocalizations.of(context)!;
    final locale = ref.watch(localeProvider);

    return Scaffold(
      appBar: AppBar(title: Text(localizations.settings)),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.language),
            title: Text(localizations.language),
            subtitle: Text(locale.languageCode == 'fi' ? 'Suomi' : 'English'),
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
                DropdownMenuItem(value: Locale('en'), child: Text('English')),
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
                  ref.read(themeModeProvider.notifier).setThemeMode(newMode);
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
