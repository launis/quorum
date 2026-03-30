import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/step_builder_view.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('StepBuilderView Dropdown Tests', () {
    testWidgets('renders prompt_blocks dropdown with correct options', (
      WidgetTester tester,
    ) async {
      final mockStep = {
        'id': 'test_step_1',
        'prompt_blocks': ['block_a'],
      };

      final List<PromptBlock> mockPromptBlocks = [
        const PromptBlock(
          id: 'block_a',
          slug: 'block_a',
          categoryId: 'regular',
          label: I18nText(defaultLocale: 'en', translations: {'en': 'Block A'}),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Desc A'},
          ),
        ),
        const PromptBlock(
          id: 'block_b',
          slug: 'block_b',
          categoryId: 'regular',
          label: I18nText(defaultLocale: 'en', translations: {'en': 'Block B'}),
          description: I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Desc B'},
          ),
        ),
      ];

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            promptBlocksControllerProvider.overrideWith(() {
              return MockPromptBlocksController(mockPromptBlocks);
            }),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: StepBuilderView(step: mockStep),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Check for the rendered Dropdown
      // The dropdown label is "Prompt Block"
      expect(find.text('Prompt Block'), findsOneWidget);

      // Verify that 'block_a' is selected initial value
      expect(find.text('block_a'), findsWidgets);

      // Open the dropdown
      final dropdownFinder = find.byType(DropdownButtonFormField<String>).last;
      await tester.ensureVisible(dropdownFinder);
      await tester.pumpAndSettle();
      await tester.tap(dropdownFinder);
      await tester.pumpAndSettle();

      // Verify dropdown items exist
      expect(find.text('block_b').last, findsOneWidget);
    });
  });
}

class MockPromptBlocksController extends PromptBlocksController {
  final List<PromptBlock> initialData;
  MockPromptBlocksController(this.initialData);

  @override
  FutureOr<List<PromptBlock>> build() async {
    return initialData;
  }

  @override
  Future<void> refresh() async {}

  @override
  Future<PromptBlock> savePromptBlock(String id, PromptBlock payload) async {
    return payload;
  }

  @override
  Future<void> deletePromptBlock(String id) async {}

  @override
  Future<PromptBlock> clonePromptBlock(String id) async {
    return initialData.first;
  }

  @override
  Future<Map<String, dynamic>> simulatePromptBlock(
    PromptBlock payload,
    Map<String, dynamic> mockInputs,
  ) async {
    return {'rendered_prompt': 'MOCK', 'valid': true};
  }
}
