import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/model_registry_view.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('ModelRegistryView Widget Tests', () {
    testWidgets('renders model selection dropdown from available models', (
      WidgetTester tester,
    ) async {
      final mockModels = ['gpt-4o', 'gpt-3.5-turbo'];

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            availableModelsProvider.overrideWith((ref) async => mockModels),
            modelRegistryControllerProvider.overrideWith(
              () => MockModelRegistryController(),
            ),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: const ModelRegistryView(
              id: 'syscfg_123',
              initialData: {
                'id': 'syscfg_123',
                'models': {
                  'fast': {
                    'model_name': 'gpt-4o',
                    'provider': 'OpenAI',
                    'is_active': true,
                  },
                },
              },
            ),
          ),
        ),
      );

      // Settle loading states
      await tester.pumpAndSettle();

      // Verify the dropdown has the initial value 'gpt-4o'
      expect(find.text('gpt-4o'), findsWidgets);

      // Open the dropdown
      final dropdownFinder = find.byType(DropdownButtonFormField<String>).last;

      // Ensure the widget is visible
      await tester.ensureVisible(dropdownFinder);
      await tester.pumpAndSettle();

      await tester.tap(dropdownFinder);
      await tester.pumpAndSettle();

      // Verify that 'gpt-3.5-turbo' is available in the dropdown list
      expect(find.text('gpt-3.5-turbo').last, findsOneWidget);
    });
  });
}

class MockModelRegistryController extends AsyncNotifier<List<Map<String, dynamic>>>
    implements ModelRegistryController {
  @override
  Future<List<Map<String, dynamic>>> build() async {
    return [
      {
        'id': 'syscfg_123',
        'models': {
          'fast': {
            'model_name': 'gpt-4o',
            'provider': 'OpenAI',
            'is_active': true,
          },
        },
      }
    ];
  }

  @override
  Future<void> refresh() async {}

  @override
  Future<Map<String, dynamic>> saveConfig(String id, Map<String, dynamic> config) async {
    return config;
  }

  @override
  Future<void> deleteConfig(String id) async {}
}
