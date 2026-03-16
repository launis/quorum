import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/step_builder_view.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
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

      final mockPromptBlocks = [
        {'id': 'block_a', 'name': 'Block A'},
        {'id': 'block_b', 'name': 'Block B'},
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

class MockPromptBlocksController
    extends AsyncNotifier<List<Map<String, dynamic>>>
    implements PromptBlocksController {
  final List<Map<String, dynamic>> initialData;
  MockPromptBlocksController(this.initialData);

  @override
  Future<List<Map<String, dynamic>>> build() async {
    return initialData;
  }

  @override
  Future<void> refresh() async {}

  @override
  Future<Map<String, dynamic>> savePromptBlock(
    String id,
    Map<String, dynamic> payload,
  ) async {
    return payload;
  }

  @override
  Future<void> deletePromptBlock(String id) async {}
}
