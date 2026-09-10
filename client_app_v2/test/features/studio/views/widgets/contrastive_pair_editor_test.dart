import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/contrastive_pair_editor.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child, {Size size = const Size(800, 600)}) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en')],
      home: Scaffold(
        body: Center(
          child: SizedBox(width: size.width, height: size.height, child: child),
        ),
      ),
    );
  }

  group('ContrastivePairEditor Widget Tests', () {
    testWidgets(
      'renders acceptable and rejected fields with live character counters',
      (tester) async {
        ContrastivePairDTO? result;
        await tester.pumpWidget(
          createTestWidget(
            ContrastivePairEditor(
              initialValue: const ContrastivePairDTO(
                acceptable: 'Valid acceptable text',
                rejected: 'Short',
              ),
              onChanged: (val) => result = val,
            ),
          ),
        );

        expect(find.text('Approved Example (Acceptable)'), findsOneWidget);
        expect(find.text('Rejected Counterpart (Rejected)'), findsOneWidget);
        expect(find.text('21/10 chars'), findsOneWidget);
        expect(find.text('5/10 chars'), findsOneWidget);
        expect(result, isNull); // No mutation yet
      },
    );

    testWidgets('ISTQB Negative: flags duplicate entries with warning banner', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          ContrastivePairEditor(
            initialValue: const ContrastivePairDTO(
              acceptable: 'Identical sentence here',
              rejected: 'Identical sentence here',
            ),
            onChanged: (_) {},
          ),
        ),
      );

      expect(
        find.text('Approved and rejected examples cannot be identical.'),
        findsOneWidget,
      );
    });

    testWidgets('renders side-by-side on wide containers (>= 520px)', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          ContrastivePairEditor(
            initialValue: const ContrastivePairDTO(
              acceptable: 'Acceptable exemplar text',
              rejected: 'Rejected counter exemplar',
            ),
            onChanged: (_) {},
          ),
          size: const Size(600, 400),
        ),
      );

      expect(find.byType(Row), findsWidgets);
    });

    testWidgets('renders vertically stacked on narrow containers (< 520px)', (
      tester,
    ) async {
      await tester.pumpWidget(
        createTestWidget(
          ContrastivePairEditor(
            initialValue: const ContrastivePairDTO(
              acceptable: 'Acceptable exemplar text',
              rejected: 'Rejected counter exemplar',
            ),
            onChanged: (_) {},
          ),
          size: const Size(400, 400),
        ),
      );

      // In narrow mode, the LayoutBuilder returns a Column instead of a Row
      final fields = find.byType(TextFormField);
      expect(fields, findsNWidgets(2));
      final firstPos = tester.getTopLeft(fields.first);
      final secondPos = tester.getTopLeft(fields.last);
      expect(
        firstPos.dx,
        equals(secondPos.dx),
      ); // Stacked vertically with identical X coordinate
      expect(secondPos.dy, greaterThan(firstPos.dy));
    });
  });
}
