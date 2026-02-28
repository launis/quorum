import 'package:client_app/features/admin/domain/models/model_registry.dart';
import 'package:client_app/features/admin/presentation/providers/model_registry_controller.dart';
import 'package:client_app/features/studio/presentation/widgets/strategy_selection_field.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

// Mock State Helper
ModelRegistryState createMockState(List<String> strategyIds) {
  return ModelRegistryState(
    providers:
        strategyIds
            .map(
              (id) => LLMProviderConfig(
                id: id,
                provider: 'mock',
                modelName: 'mock',
              ),
            )
            .toList(),
  );
}

void main() {
  testWidgets(
    'StrategySelectionField renders strategies and handles selection',
    (WidgetTester tester) async {
      String? selectedValue;

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            modelRegistryControllerProvider.overrideWith(
              () => MockModelRegistryController(),
            ),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: StrategySelectionField(
                currentStrategy: null,
                onChanged: (val) => selectedValue = val,
              ),
            ),
          ),
        ),
      );

      // Initial pump (loading or data)
      await tester.pumpAndSettle();

      // Verify Dropdown exists
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);

      // Open Dropdown
      await tester.tap(find.byType(DropdownButtonFormField<String>));
      await tester.pumpAndSettle();

      // Verify items
      expect(find.text('fast'), findsOneWidget);
      expect(find.text('deep'), findsOneWidget);
      expect(find.text('custom_1'), findsOneWidget);

      // Select 'deep'
      await tester.tap(find.text('deep').last);
      await tester.pumpAndSettle();

      expect(selectedValue, 'deep');
    },
  );
}

class MockModelRegistryController extends AsyncNotifier<ModelRegistryState>
    implements ModelRegistryController {
  @override
  Future<ModelRegistryState> build() async {
    return createMockState(['fast', 'deep', 'custom_1']);
  }

  @override
  void selectProvider(String? id) {}

  @override
  Future<void> saveConfig(String id, LLMProviderConfig config) async {}

  @override
  Future<void> deleteConfig(String id) async {}

  @override
  Future<void> runTest(AdHocTestRequest request) async {}
}
