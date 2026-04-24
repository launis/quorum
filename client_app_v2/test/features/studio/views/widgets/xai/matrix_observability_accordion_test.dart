import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/views/widgets/xai/matrix_observability_accordion.dart';

void main() {
  testWidgets(
    'MatrixObservabilityAccordion renders atomic statistics correctly',
    (WidgetTester tester) async {
      const title = 'Matrix Scoring';
      const subtitle = 'Structural view';
      const trueLabel = 'Pass';
      const falseLabel = 'Fail';

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
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
    },
  );
}
