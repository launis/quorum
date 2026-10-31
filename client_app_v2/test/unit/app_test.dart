import 'dart:async';

import 'package:client_app/app.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/features/settings/domain/models/app_settings_state.dart';
import 'package:client_app/features/settings/presentation/settings_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';

class _StubSettingsController extends AsyncNotifier<AppSettingsState>
    implements SettingsController {
  final FutureOr<AppSettingsState> Function() _onBuild;

  _StubSettingsController(this._onBuild);

  @override
  FutureOr<AppSettingsState> build() => _onBuild();

  @override
  Future<void> updateThemeMode(ThemeMode newMode) async {
    final current = state.value;
    if (current != null) {
      state = AsyncData(current.copyWith(themeMode: newMode));
    }
  }

  @override
  Future<void> updateLocale(Locale newLocale) async {
    final current = state.value;
    if (current != null) {
      state = AsyncData(current.copyWith(locale: newLocale));
    }
  }
}

void main() {
  late ErrorWidgetBuilder originalErrorBuilder;

  setUp(() {
    originalErrorBuilder = ErrorWidget.builder;
  });

  tearDown(() {
    ErrorWidget.builder = originalErrorBuilder;
  });

  GoRouter createTestRouter() {
    return GoRouter(
      initialLocation: '/home',
      routes: [
        GoRoute(
          path: '/home',
          builder: (context, state) => Scaffold(
            appBar: AppBar(title: Text(AppLocalizations.of(context)!.appTitle)),
            body: const Center(child: Icon(Icons.verified_user)),
          ),
        ),
      ],
    );
  }

  group('App Root Shell Hardening Tests', () {
    testWidgets(
      'Positive: renders MaterialApp.router with AppExceptionBoundary, localized title, and active settings when hydrated',
      (WidgetTester tester) async {
        final testRouter = createTestRouter();
        addTearDown(testRouter.dispose);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              routerProvider.overrideWithValue(testRouter),
              settingsControllerProvider.overrideWith(
                () => _StubSettingsController(
                  () => const AppSettingsState(
                    themeMode: ThemeMode.dark,
                    locale: Locale('en'),
                  ),
                ),
              ),
            ],
            child: const App(),
          ),
        );

        await tester.pumpAndSettle();

        expect(find.byType(AppExceptionBoundary), findsOneWidget);
        expect(find.byIcon(Icons.verified_user), findsOneWidget);
        expect(find.text('Cognitive Quorum Client'), findsOneWidget);

        final materialApp = tester.widget<MaterialApp>(
          find.byType(MaterialApp),
        );
        expect(materialApp.themeMode, equals(ThemeMode.dark));
        expect(materialApp.locale, equals(const Locale('en')));
      },
    );

    testWidgets(
      'Negative/Boundary 1: renders SplashScreen while settingsControllerProvider is in initial AsyncLoading state',
      (WidgetTester tester) async {
        final completer = Completer<AppSettingsState>();
        final testRouter = createTestRouter();
        addTearDown(testRouter.dispose);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              routerProvider.overrideWithValue(testRouter),
              settingsControllerProvider.overrideWith(
                () => _StubSettingsController(() => completer.future),
              ),
            ],
            child: const App(),
          ),
        );

        await tester.pump();

        expect(find.byType(SplashScreen), findsOneWidget);
        expect(find.byIcon(Icons.verified_user), findsNothing);

        completer.complete(
          const AppSettingsState(
            themeMode: ThemeMode.light,
            locale: Locale('fi'),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(SplashScreen), findsNothing);
        expect(find.byIcon(Icons.verified_user), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 2: renders ErrorView instead of crashing on unguarded requireValue when settingsControllerProvider fails and recovers on retry',
      (WidgetTester tester) async {
        var attempt = 0;
        final testRouter = createTestRouter();
        addTearDown(testRouter.dispose);

        await tester.pumpWidget(
          ProviderScope(
            retry: (retryCount, error) => null,
            overrides: [
              routerProvider.overrideWithValue(testRouter),
              settingsControllerProvider.overrideWith(
                () => _StubSettingsController(() {
                  attempt++;
                  if (attempt == 1) {
                    return Future<AppSettingsState>.error(
                      AppException.validation(
                        'Corrupted local settings storage',
                      ),
                    );
                  }
                  return const AppSettingsState(
                    themeMode: ThemeMode.system,
                    locale: Locale('en'),
                  );
                }),
              ),
            ],
            child: const App(),
          ),
        );

        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byIcon(Icons.error_outline), findsOneWidget);

        await tester.tap(find.byIcon(Icons.refresh));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsNothing);
        expect(find.byIcon(Icons.verified_user), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 3: buildAppBoundary renders Fail-Fast ErrorView instead of SizedBox.shrink when child is null',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            localizationsDelegates: App.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Builder(
              builder: (context) => buildAppBoundary(context, null),
            ),
          ),
        );

        await tester.pumpAndSettle();

        expect(find.byType(AppExceptionBoundary), findsOneWidget);
        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byIcon(Icons.error_outline), findsOneWidget);
      },
    );
  });
}
