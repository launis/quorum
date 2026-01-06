import 'package:client_app/l10n/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:firebase_ui_localizations/firebase_ui_localizations.dart';
import 'package:flex_color_scheme/flex_color_scheme.dart';
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

    return MaterialApp.router(
      title: 'Cognitive Quorum',

      // 2. Navigation
      routerConfig: goRouter,

      // 3. Theming
      // Using FlexColorScheme for a polished look as per design mandates.
      theme: FlexThemeData.light(
        scheme: FlexScheme.deepBlue,
        useMaterial3: true,
      ),
      darkTheme: FlexThemeData.dark(
        scheme: FlexScheme.deepBlue,
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,

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
