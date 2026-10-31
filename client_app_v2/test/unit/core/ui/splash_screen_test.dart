import 'package:client_app/core/ui/splash_screen.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SplashScreen Hardening Widget Tests', () {
    testWidgets(
      'Positive: renders Scaffold with centered adaptive CircularProgressIndicator under AppTheme.light',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: const SplashScreen(),
          ),
        );

        await tester.pump();

        expect(find.byType(SplashScreen), findsOneWidget);
        expect(find.byType(Scaffold), findsOneWidget);
        expect(find.byType(Center), findsOneWidget);
        expect(find.byType(CircularProgressIndicator), findsOneWidget);

        final scaffoldContext = tester.element(find.byType(Scaffold));
        expect(
          Theme.of(scaffoldContext).scaffoldBackgroundColor,
          equals(AppTheme.light.scaffoldBackgroundColor),
        );
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets(
      'Negative/Boundary 1: renders under extreme tiny viewport constraints (1x1 and 36x36) without layout overflow',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.dark,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('fi'),
            home: const Center(
              child: SizedBox(width: 1, height: 1, child: SplashScreen()),
            ),
          ),
        );

        await tester.pump();
        expect(tester.takeException(), isNull);
        expect(find.byType(CircularProgressIndicator), findsOneWidget);

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.dark,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('fi'),
            home: const Center(
              child: SizedBox(width: 36, height: 36, child: SplashScreen()),
            ),
          ),
        );

        await tester.pump();
        expect(tester.takeException(), isNull);
        expect(find.byType(CircularProgressIndicator), findsOneWidget);
      },
    );

    testWidgets(
      'Negative/Boundary 2: renders cleanly under extreme TextScaler boundaries (0.5x and 3.0x) with zero hardcoded text nodes',
      (WidgetTester tester) async {
        for (final scale in <double>[0.5, 3.0]) {
          await tester.pumpWidget(
            MaterialApp(
              theme: AppTheme.dark,
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              locale: const Locale('en'),
              builder: (context, child) => MediaQuery(
                data: MediaQuery.of(
                  context,
                ).copyWith(textScaler: TextScaler.linear(scale)),
                child: child!,
              ),
              home: const SplashScreen(),
            ),
          );

          await tester.pump();
          expect(tester.takeException(), isNull);
          expect(find.byType(Text), findsNothing);
          expect(find.byType(CircularProgressIndicator), findsOneWidget);
        }
      },
    );
  });
}
