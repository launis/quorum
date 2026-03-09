import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
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
    final goRouter = ref.watch(routerProvider);

    // 2. Default Configuration (V2 MVP)
    const themeMode = ThemeMode.system;
    const locale = Locale('fi');

    return MaterialApp.router(
      title: 'Cognitive Quorum',
      locale: locale,
      builder: (context, child) {
        return AppErrorBoundary(child: child ?? const SizedBox.shrink());
      },

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
