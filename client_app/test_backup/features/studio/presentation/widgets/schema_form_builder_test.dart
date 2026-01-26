import 'package:client_app/features/studio/domain/models/json_schema.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/schema_form_builder.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('SchemaFormBuilder renders fields based on schema', (tester) async {
    final schema = const JsonSchema(properties: {
      'name': JsonSchema(type: 'string', title: 'Name'),
      'age': JsonSchema(type: 'integer', title: 'Age'),
      'role': JsonSchema(type: 'string', enumValues: ['Admin', 'User'], title: 'Role'),
    });

    Map<String, dynamic> formData = {};

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: SchemaFormBuilder(
          schema: schema,
          initialData: const {},
          onChanged: (val) => formData = val,
        ),
      ),
    ));

    // Verify String field
    expect(find.widgetWithText(TextFormField, 'Name'), findsOneWidget);
    
    // Verify Integer field
    expect(find.widgetWithText(TextFormField, 'Age'), findsOneWidget);
    
    // Verify Enum field (Dropdown)
    expect(find.widgetWithText(DropdownButtonFormField, 'Role'), findsOneWidget);

    // Enter Text
    await tester.enterText(find.widgetWithText(TextFormField, 'Name'), 'Alice');
    await tester.pump();
    expect(formData['name'], equals('Alice'));

    // Enter Number
    await tester.enterText(find.widgetWithText(TextFormField, 'Age'), '30');
    await tester.pump();
    expect(formData['age'], equals(30));
  });
}
