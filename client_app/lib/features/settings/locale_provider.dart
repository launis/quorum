import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'locale_provider.g.dart';

/// **Locale Provider**
///
/// Manages the application's [Locale] (en, fi).
/// Persists the user's preference using [SharedPreferences].
@riverpod
class LocaleNotifier extends _$LocaleNotifier {
  static const _storageKey = 'locale_preference';

  @override
  Locale build() {
    // 1. Default Fallback
    // Note: We rely on App.dart to sync User Profile locale.
    // Future: Restore _loadLocale logic using listener or proper initialization.
    return const Locale('en');
  }

  Future<void> setLocale(Locale locale) async {
    state = locale;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_storageKey, locale.languageCode);

    // Sync to Backend
    final user = ref.read(authControllerProvider).value;
    if (user != null) {
      try {
        final api = ref.read(apiClientProvider);
        await api.patch<Map<String, dynamic>>(
          '/auth/users/${user.id}',
          data: {'language': locale.languageCode},
        );
      } catch (e) {
        debugPrint('Failed to sync locale to backend: $e');
      }
    }
  }
}
