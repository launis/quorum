import 'package:client_app/features/studio/presentation/widgets/sdui/code_editor_field.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CodeEditorField', () {
    testWidgets('renders correctly with label and initial value', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CodeEditorField(
              label: 'Test Label',
              initialValue: 'Initial Code',
              onChanged: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Test Label'), findsOneWidget);
      expect(find.text('Initial Code'), findsOneWidget);
      expect(find.byType(TextFormField), findsOneWidget);
    });

    testWidgets('calls onChanged when text is entered', (tester) async {
      String? updatedValue;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CodeEditorField(
              label: 'Editor',
              onChanged: (val) => updatedValue = val,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), 'New Code');
      expect(updatedValue, 'New Code');
    });

    testWidgets('uses monospaced font style', (tester) async {
       await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CodeEditorField(
              label: 'Editor',
              onChanged: (_) {},
            ),
          ),
        ),
      );
      
      final textField = tester.widget<TextField>(find.byType(TextField));
      final style = textField.style;
      
      // We can't easily check exact font loading in test without setup,
      // but we can check if the style properties match what we set.
      expect(style?.fontFamily, 'Courier New');
    });
  });
}
