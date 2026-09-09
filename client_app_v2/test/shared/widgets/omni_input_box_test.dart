import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/omni_input_box.dart';
import 'package:client_app/shared/widgets/pdf_export_guide_dialog.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  Widget createOmniBox({
    required String keyName,
    required String label,
    dynamic currentValue,
    Function(dynamic)? onChanged,
  }) {
    return MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      locale: const Locale('fi'),
      home: Scaffold(
        body: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: OmniInputBox(
              keyName: keyName,
              label: label,
              currentValue: currentValue,
              onChanged: onChanged ?? (_) {},
            ),
          ),
        ),
      ),
    );
  }

  testWidgets(
    'OmniInputBox renders with help button and opens PdfExportGuideDialog on tap',
    (tester) async {
      await tester.pumpWidget(
        createOmniBox(keyName: 'chat_log', label: 'Keskusteluhistoria'),
      );
      await tester.pumpAndSettle();

      expect(find.text('Keskusteluhistoria'), findsOneWidget);
      expect(find.byIcon(Icons.help_outline), findsOneWidget);

      // Tap help button
      await tester.tap(find.byIcon(Icons.help_outline));
      await tester.pumpAndSettle();

      // Dialog must be open
      expect(find.byType(PdfExportGuideDialog), findsOneWidget);
      expect(find.text('Keskustelun tuominen Quorumiin'), findsOneWidget);

      // Close dialog
      await tester.tap(find.text('Sulje'));
      await tester.pumpAndSettle();
      expect(find.byType(PdfExportGuideDialog), findsNothing);
    },
  );

  testWidgets(
    'OmniInputBox displays truncation warning banner when file mode is selected for chat_log',
    (tester) async {
      await tester.pumpWidget(
        createOmniBox(keyName: 'chat_log', label: 'Keskusteluhistoria'),
      );
      await tester.pumpAndSettle();

      // Initially in paste text mode: warning banner is NOT visible
      expect(find.byIcon(Icons.warning_amber_rounded), findsNothing);
      expect(find.textContaining('leikkautuneet poikki'), findsNothing);

      // Switch to upload file mode
      await tester.tap(find.byIcon(Icons.upload_file));
      await tester.pumpAndSettle();

      // Truncation warning banner is now visible
      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      expect(find.textContaining('leikkautuneet poikki'), findsOneWidget);
    },
  );

  testWidgets(
    'OmniInputBox does not display truncation warning banner for non-chat keys in file mode',
    (tester) async {
      await tester.pumpWidget(
        createOmniBox(keyName: 'product_text', label: 'Lopputuote'),
      );
      await tester.pumpAndSettle();

      // Switch to upload file mode
      await tester.tap(find.byIcon(Icons.upload_file));
      await tester.pumpAndSettle();

      // Warning banner must NOT be shown for non-chat keys
      expect(find.byIcon(Icons.warning_amber_rounded), findsNothing);
      expect(find.textContaining('leikkautuneet poikki'), findsNothing);
    },
  );
}
