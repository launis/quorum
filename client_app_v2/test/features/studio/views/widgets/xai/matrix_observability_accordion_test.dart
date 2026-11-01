import 'package:client_app/features/studio/views/widgets/xai/matrix_observability_accordion.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets(
    'MatrixObservabilityAccordion renders atomic statistics and semantic colors correctly',
    (WidgetTester tester) async {
      const title = 'Matrix Scoring';
      const subtitle = 'Structural view';
      const trueLabel = 'Pass';
      const falseLabel = 'Fail';

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.light().copyWith(
            extensions: const <ThemeExtension<dynamic>>[
              AppSemanticColors.light,
            ],
          ),
          home: const Scaffold(
            body: MatrixObservabilityAccordion(
              trueAtomsCount: 15,
              falseAtomsCount: 3,
              titleLabel: title,
              subtitleLabel: subtitle,
              trueAtomsLabel: trueLabel,
              falseAtomsLabel: falseLabel,
            ),
          ),
        ),
      );

      expect(find.text(title), findsOneWidget);
      expect(find.text(subtitle), findsOneWidget);
      expect(find.text(trueLabel.toUpperCase()), findsOneWidget);
      expect(find.text(falseLabel.toUpperCase()), findsOneWidget);
      expect(find.text('15'), findsOneWidget);
      expect(find.text('3'), findsOneWidget);
      expect(find.byIcon(Icons.analytics_outlined), findsOneWidget);

      final passValueText = tester.widget<Text>(find.text('15'));
      expect(passValueText.style?.color, AppSemanticColors.light.success);
    },
  );

  testWidgets(
    'MatrixObservabilityAccordion handles zero boundary counts and dark semantic theme tokens',
    (WidgetTester tester) async {
      final darkTheme = ThemeData.dark().copyWith(
        extensions: const <ThemeExtension<dynamic>>[AppSemanticColors.dark],
      );

      await tester.pumpWidget(
        MaterialApp(
          theme: darkTheme,
          home: const Scaffold(
            body: MatrixObservabilityAccordion(
              trueAtomsCount: 0,
              falseAtomsCount: 0,
              titleLabel: 'Zero Boundary',
              subtitleLabel: 'Empty matrix evaluation',
              trueAtomsLabel: 'True Atoms',
              falseAtomsLabel: 'False Atoms',
            ),
          ),
        ),
      );

      expect(find.text('0'), findsNWidgets(2));
      final zeroWidgets = tester.widgetList<Text>(find.text('0')).toList();
      expect(zeroWidgets[0].style?.color, AppSemanticColors.dark.success);
      expect(zeroWidgets[1].style?.color, darkTheme.colorScheme.error);
    },
  );

  testWidgets(
    'MatrixObservabilityAccordion contains extreme label strings under narrow viewport constraints without overflow',
    (WidgetTester tester) async {
      final longText = 'A' * 300;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 180,
              child: MatrixObservabilityAccordion(
                trueAtomsCount: 999999,
                falseAtomsCount: 888888,
                titleLabel: longText,
                subtitleLabel: longText,
                trueAtomsLabel: longText,
                falseAtomsLabel: longText,
              ),
            ),
          ),
        ),
      );

      expect(tester.takeException(), isNull);
      expect(find.text('999999'), findsOneWidget);
      expect(find.text('888888'), findsOneWidget);
    },
  );
}
