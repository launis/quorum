import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/pdf_export_guide_dialog.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  Widget createDialogWidget({Locale locale = const Locale('fi')}) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: locale,
      home: Scaffold(
        body: Builder(
          builder: (context) => Center(
            child: ElevatedButton(
              onPressed: () {
                showDialog<void>(
                  context: context,
                  builder: (_) => const PdfExportGuideDialog(),
                );
              },
              child: const Text('Open Dialog'),
            ),
          ),
        ),
      ),
    );
  }

  testWidgets('PdfExportGuideDialog renders all provider tabs in Finnish and switches correctly', (tester) async {
    await tester.pumpWidget(createDialogWidget(locale: const Locale('fi')));
    await tester.pumpAndSettle();

    // Open the dialog
    await tester.tap(find.text('Open Dialog'));
    await tester.pumpAndSettle();

    // Verify dialog title and tabs exist
    expect(find.text('Keskustelun tuominen Quorumiin'), findsOneWidget);
    expect(find.text('ChatGPT'), findsOneWidget);
    expect(find.text('Google Gemini'), findsOneWidget);
    expect(find.text('Claude'), findsOneWidget);

    // ChatGPT tab content (active by default)
    expect(find.text('Suositeltu ja nopein tapa (Leikepöytä)'), findsOneWidget);
    expect(find.textContaining('1. Valitse Quorumin syöttötavaksi'), findsOneWidget);
    expect(find.textContaining('Huom! Jos tulostat PDF:ksi'), findsOneWidget);

    // Switch to Gemini tab
    await tester.tap(find.text('Google Gemini'));
    await tester.pumpAndSettle();

    expect(find.text('Suositeltu tapa (Tallenna PDF tai Leikepöytä)'), findsOneWidget);
    expect(find.textContaining('Paina Gemini-keskustelussa'), findsOneWidget);
    expect(find.textContaining('Geminissä kaikki kehotteet'), findsOneWidget);

    // Switch to Claude tab
    await tester.tap(find.text('Claude'));
    await tester.pumpAndSettle();

    expect(find.textContaining('Paina Claude-keskustelussa'), findsOneWidget);

    // Close the dialog via close button
    await tester.tap(find.text('Sulje'));
    await tester.pumpAndSettle();

    expect(find.byType(PdfExportGuideDialog), findsNothing);
  });

  testWidgets('PdfExportGuideDialog renders correctly in English', (tester) async {
    await tester.pumpWidget(createDialogWidget(locale: const Locale('en')));
    await tester.pumpAndSettle();

    // Open the dialog
    await tester.tap(find.text('Open Dialog'));
    await tester.pumpAndSettle();

    // Verify English title and content
    expect(find.text('Importing Conversation to Quorum'), findsOneWidget);
    expect(find.text('Recommended & Fastest Method (Clipboard)'), findsOneWidget);
    expect(find.textContaining('1. Select \'Paste Text\' mode'), findsOneWidget);
    expect(find.textContaining('Notice: If printing to PDF'), findsOneWidget);

    // Close via close icon button
    await tester.tap(find.byIcon(Icons.close));
    await tester.pumpAndSettle();

    expect(find.byType(PdfExportGuideDialog), findsNothing);
  });
}
