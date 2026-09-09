import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';

void main() {
  group('AppExceptionX Data Corruption Localization & Hints', () {
    testWidgets(
      'correctly resolves DATA_CORRUPTION to localized explanation and action hint',
      (tester) async {
        late BuildContext capturedContext;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('fi'),
            home: Builder(
              builder: (context) {
                capturedContext = context;
                return const SizedBox();
              },
            ),
          ),
        );

        final l10n = AppLocalizations.of(capturedContext)!;

        const exception = AppException(
          type: 'https://api.quorum.fi/errors/data-corruption',
          title: 'Data Corruption',
          status: 500,
          detail: 'Missing blob trace data for execution_trace.',
          extensions: {
            'error_code': 'DATA_CORRUPTION',
            'path': 'executions/exe_e0dd352d3de14418/execution_trace.json',
          },
        );

        final hint = exception.toLocalizedHint(l10n);

        expect(
          hint,
          contains(
            'Tietokannan eheysvirhe: Tähän ajoon liittyvää raskasta dataa (blobs) ei löydetty fyysiseltä levyltä. Raporttia ei voida rakentaa.',
          ),
        );
        expect(
          hint,
          contains(
            'Vihje: Sinun tulee ajaa työkalun suoritus uudelleen luodaksesi datan fyysiselle levylle.',
          ),
        );
      },
    );

    testWidgets(
      'ErrorView renders backToDashboard action button and triggers onAction callback',
      (tester) async {
        bool actionTriggered = false;

        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('fi'),
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  final l10n = AppLocalizations.of(context)!;
                  return ErrorView(
                    error: const AppException(
                      type: 'https://api.quorum.fi/errors/data-corruption',
                      title: 'Data Corruption',
                      status: 500,
                      detail: 'Missing blob trace data.',
                      extensions: {'error_code': 'DATA_CORRUPTION'},
                    ),
                    actionLabel: l10n.backToDashboard,
                    onAction: () => actionTriggered = true,
                  );
                },
              ),
            ),
          ),
        );

        await tester.pumpAndSettle();

        final buttonFinder = find.widgetWithText(
          FilledButton,
          'Palaa päänäkymään',
        );
        expect(buttonFinder, findsOneWidget);

        await tester.tap(buttonFinder);
        await tester.pumpAndSettle();

        expect(actionTriggered, isTrue);
      },
    );
  });
}
