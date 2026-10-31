import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:firebase_ui_localizations/firebase_ui_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Wraps the routed widget hierarchy in [AppExceptionBoundary] while rejecting null router children via [ErrorView].
Widget buildAppBoundary(BuildContext context, Widget? child) {
  return AppExceptionBoundary(
    child:
        child ??
        Scaffold(
          body: ErrorView(
            error: AppException.validation(
              AppLocalizations.of(context)!.errorUnknown,
            ),
          ),
        ),
  );
}

/// Root Flutter application widget binding GoRouter, FlexColorScheme themes, and ARB localizations.
class App extends ConsumerWidget {
  const App({super.key});

  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = [
    AppLocalizations.delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    FirebaseUILocalizations.delegate,
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final goRouter = ref.watch(routerProvider);
    final settingsAsync = ref.watch(settingsControllerProvider);

    return switch (settingsAsync) {
      AsyncValue(:final value?) => MaterialApp.router(
        onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
        locale: value.locale,
        builder: buildAppBoundary,
        routerConfig: goRouter,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        themeMode: value.themeMode,
        localizationsDelegates: localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        debugShowCheckedModeBanner: false,
      ),
      AsyncError(:final error, :final stackTrace) => MaterialApp(
        onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        localizationsDelegates: localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        debugShowCheckedModeBanner: false,
        home: Scaffold(
          body: AppExceptionBoundary(
            child: ErrorView(
              error: error,
              stackTrace: stackTrace,
              onRetry: () => ref.invalidate(settingsControllerProvider),
            ),
          ),
        ),
      ),
      _ => MaterialApp(
        onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        localizationsDelegates: localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: const SplashScreen(),
        debugShowCheckedModeBanner: false,
      ),
    };
  }
}
