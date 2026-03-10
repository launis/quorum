import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('PromptBlockBuilderView Widget Tests', () {
    testWidgets('renders fields correctly from payload', (WidgetTester tester) async {
      final mockPromptBlock = {
        'id': 'test_block_1',
        'strictness_level': 75.0,
        'criteria': [
          {
            'slug': 'test_criterion',
            'theory_url': 'https://example.com/theory',
            'citation_tag': 'TEST_CIT',
          }
        ]
      };

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: PromptBlockBuilderView(promptBlock: mockPromptBlock),
          ),
        ),
      );

      // Wait for rendering
      await tester.pumpAndSettle();

      // Verify ID Field
      expect(find.byType(TextField), findsWidgets);
      expect(find.text('test_block_1'), findsOneWidget);

      // Verify Strictness level is somewhat visible or present (via slider)
      final sliderFinder = find.byType(Slider);
      expect(sliderFinder, findsOneWidget);
      final slider = tester.widget<Slider>(sliderFinder);
      expect(slider.value, 75.0);

      // Verify Criteria
      expect(find.text('Row 1'), findsOneWidget);
      expect(find.text('test_criterion'), findsOneWidget); // slug
      expect(find.text('https://example.com/theory'), findsOneWidget); // theory_url
      expect(find.text('TEST_CIT'), findsOneWidget); // citation_tag
    });

    testWidgets('adds a new criterion row when Add Row is clicked', (WidgetTester tester) async {
       final mockPromptBlock = <String, dynamic>{
        'id': 'empty_test',
        'strictness_level': 50.0,
        'criteria': []
      };

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: PromptBlockBuilderView(promptBlock: mockPromptBlock),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Initially zero rows
      expect(find.text('Row 1'), findsNothing);

      // Click Add Row
      final addRowButton = find.widgetWithText(OutlinedButton, 'Add Row');
      expect(addRowButton, findsOneWidget);
      await tester.tap(addRowButton);
      await tester.pumpAndSettle();

      // Now Row 1 should exist
      expect(find.text('Row 1'), findsOneWidget);
    });
  });
}
