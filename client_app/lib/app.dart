import 'package:client_app/l10n/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/features/settings/theme_provider.dart';
import 'package:client_app/features/settings/locale_provider.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:firebase_ui_localizations/firebase_ui_localizations.dart';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

///
/// The entry point of the Flutter application.
///
/// **Responsibilities**:
/// - Initializes [MaterialApp.router].
/// - Connects the Riverpod [routerProvider] to the standard Flutter navigation system.
/// - Applies Global Theming logic (FlexColorScheme).
class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 1. Watch Router
    // We watch the router provider so that if the router itself changes (rare),
    // the app rebuilds. The router internal state changes (navigation) are handled
    // by the routerDelegate.
    final goRouter = ref.watch(routerProvider);

    // 2. Watch Theme Mode
    // 2. Watch Theme Mode
    final themeMode = ref.watch(themeModeProvider);
    final locale = ref.watch(localeProvider);

    return MaterialApp.router(
      title: 'Cognitive Quorum',
      locale: locale,

      // 3. Navigation
      routerConfig: goRouter,

      // 4. Theming
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,

      // 4. Localization
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        FirebaseUILocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,

      // 5. Debugging
      debugShowCheckedModeBanner: false,
    );
  }
}
