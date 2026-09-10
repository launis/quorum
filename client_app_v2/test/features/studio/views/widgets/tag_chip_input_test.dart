import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/widgets/tag_chip_input.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  Widget createTestWidget(Widget child) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en')],
      home: Scaffold(body: child),
    );
  }

  group('TagChipInput Widget Tests', () {
    testWidgets('submitting text via Enter commits trimmed chip', (tester) async {
      List<String> tags = [];
      await tester.pumpWidget(
        createTestWidget(
          TagChipInput(
            onChanged: (val) => tags = val,
          ),
        ),
      );

      final input = find.byType(TextField);
      await tester.enterText(input, 'kausaalisuus');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      await tester.pumpAndSettle();

      expect(find.text('kausaalisuus'), findsOneWidget);
      expect(tags, ['kausaalisuus']);
      expect(find.widgetWithText(TextField, ''), findsOneWidget);
    });

    testWidgets('typing comma commits trimmed chip', (tester) async {
      List<String> tags = [];
      await tester.pumpWidget(
        createTestWidget(
          TagChipInput(
            onChanged: (val) => tags = val,
          ),
        ),
      );

      final input = find.byType(TextField);
      await tester.enterText(input, 'syntaksi,');
      await tester.pumpAndSettle();

      expect(find.text('syntaksi'), findsOneWidget);
      expect(tags, ['syntaksi']);
    });

    testWidgets('pressing backspace in empty field deletes trailing chip', (tester) async {
      List<String> tags = ['alpha', 'beta'];
      await tester.pumpWidget(
        createTestWidget(
          TagChipInput(
            initialTags: tags,
            onChanged: (val) => tags = val,
          ),
        ),
      );

      expect(find.text('alpha'), findsOneWidget);
      expect(find.text('beta'), findsOneWidget);

      final input = find.byType(TextField);
      await tester.tap(input);
      await tester.pumpAndSettle();

      await tester.sendKeyEvent(LogicalKeyboardKey.backspace);
      await tester.pumpAndSettle();

      expect(find.text('alpha'), findsOneWidget);
      expect(find.text('beta'), findsNothing);
      expect(tags, ['alpha']);
    });

    testWidgets('enforces bounded chip layout maxWidth 240 and tooltip', (tester) async {
      const longText = 'extremely_lengthy_syntactic_anchor_token_that_would_normally_overflow_horizontal_layouts';
      await tester.pumpWidget(
        createTestWidget(
          const TagChipInput(
            initialTags: [longText],
          ),
        ),
      );

      final constrainedBox = tester.widget<ConstrainedBox>(
        find.ancestor(
          of: find.text(longText),
          matching: find.byType(ConstrainedBox),
        ).first,
      );

      expect(constrainedBox.constraints.maxWidth, 240);
      expect(find.byTooltip(longText), findsOneWidget);
    });

    testWidgets('uncommitted buffer is flushed and committed on Form.save()', (tester) async {
      final formKey = GlobalKey<FormState>();
      List<String>? savedTags;

      await tester.pumpWidget(
        createTestWidget(
          Form(
            key: formKey,
            child: TagChipInput(
              onSaved: (val) => savedTags = val,
            ),
          ),
        ),
      );

      final input = find.byType(TextField);
      await tester.enterText(input, 'uncommitted_token');
      await tester.pumpAndSettle();

      formKey.currentState!.save();
      await tester.pumpAndSettle();

      expect(savedTags, isNotNull);
      expect(savedTags, contains('uncommitted_token'));
    });

    testWidgets('uncommitted buffer is auto-committed on focus loss', (tester) async {
      List<String> tags = [];
      final focusNode = FocusNode();

      await tester.pumpWidget(
        createTestWidget(
          Column(
            children: [
              TagChipInput(
                onChanged: (val) => tags = val,
              ),
              TextField(focusNode: focusNode),
            ],
          ),
        ),
      );

      final chipInput = find.byType(TextField).first;
      await tester.enterText(chipInput, 'lost_focus_token');
      await tester.pumpAndSettle();

      // Shift focus to the other text field
      await tester.tap(find.byType(TextField).last);
      await tester.pumpAndSettle();

      expect(tags, contains('lost_focus_token'));
    });

    testWidgets('ISTQB Negative: duplicate token entry triggers inline validation error and halts commit', (tester) async {
      final formKey = GlobalKey<FormState>();
      await tester.pumpWidget(
        createTestWidget(
          Form(
            key: formKey,
            child: const TagChipInput(
              initialTags: ['existing_anchor'],
            ),
          ),
        ),
      );

      final input = find.byType(TextField);
      await tester.enterText(input, 'existing_anchor');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      await tester.pumpAndSettle();

      expect(find.text('Keyword has already been added.'), findsOneWidget);
    });
  });
}
