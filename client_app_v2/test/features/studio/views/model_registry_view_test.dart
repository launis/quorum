import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/model_registry_view.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/model_config.dart';
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
            availableModelsProvider.overrideWith(
              (ref, _) async => mockModels,
            ),
            supportedLocationsProvider.overrideWith(
              (ref) async => [
                {'id': 'europe-north1', 'label': 'Hamina, Finland (europe-north1)'},
              ],
            ),

            modelRegistryByIdProvider('syscfg_123').overrideWith(
              (ref) async => const ModelConfig(
                id: 'syscfg_123',
                slug: 'syscfg_123_slug',
                type: 'model_registry',
                models: {
                  'fast': LlmModelConfig(
                    modelName: 'gpt-4o',
                    provider: 'OpenAI',
                    isActive: true,
                  ),
                },
              ),
            ),
            modelRegistryControllerProvider.overrideWith(
              () => MockModelRegistryController(),
            ),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: const ModelRegistryView(id: 'syscfg_123'),
          ),
        ),
      );

      // Settle loading states (Wait for Isolate.run)
      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 100));
      });
      await tester.pumpAndSettle();

      // Verify the dropdown has the initial value 'gpt-4o'
      expect(find.text('gpt-4o'), findsWidgets);

      // Open the dropdown
      final dropdownFinder = find.byType(DropdownButtonFormField<String>).last;

      // Ensure the widget is visible
      await tester.ensureVisible(dropdownFinder);
      await tester.pump(const Duration(milliseconds: 500));

      await tester.tap(dropdownFinder);
      await tester.pump(const Duration(milliseconds: 500));

      // Verify that 'gpt-3.5-turbo' is available in the dropdown list
      expect(find.text('gpt-3.5-turbo').last, findsOneWidget);
    });

    testWidgets('renders properly when vertex_location is raw env template or unmapped string', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            availableModelsProvider.overrideWith(
              (ref, _) async => ['vertex_ai/gemini-2.5-pro'],
            ),
            supportedLocationsProvider.overrideWith(
              (ref) async => [
                {'id': 'europe-north1', 'label': 'Hamina, Finland (europe-north1)'},
                {'id': 'europe-west1', 'label': 'St. Ghislain, Belgium (europe-west1)'},
              ],
            ),
            modelRegistryByIdProvider('syscfg_raw').overrideWith(
              (ref) async => const ModelConfig(
                id: 'syscfg_raw',
                slug: 'syscfg_raw_slug',
                type: 'model_registry',
                models: {
                  'deep': LlmModelConfig(
                    modelName: 'vertex_ai/gemini-2.5-pro',
                    provider: 'google',
                    additionalParams: {
                      'vertex_location': r'${VERTEX_LOCATION}',
                    },
                    isActive: true,
                  ),
                },
              ),
            ),
            modelRegistryControllerProvider.overrideWith(
              () => MockModelRegistryController(),
            ),
          ],
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: const ModelRegistryView(id: 'syscfg_raw'),
          ),
        ),
      );

      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 100));
      });
      await tester.pumpAndSettle();

      // Look for the dropdown or verify it rendered without throwing AssertionError
      expect(find.byType(DropdownButtonFormField<String>), findsWidgets);
    });
  });
}


class MockModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  @override
  Future<List<ModelConfig>> build() async {
    return const [
      ModelConfig(
        id: 'syscfg_123',
        slug: 'syscfg_123_slug',
        type: 'model_registry',
        models: {
          'fast': LlmModelConfig(
            modelName: 'gpt-4o',
            provider: 'OpenAI',
            isActive: true,
          ),
        },
      ),
    ];
  }

  @override
  Future<void> refresh() async {}

  @override
  Future<ModelConfig> saveConfig(String id, ModelConfig config) async {
    return config;
  }

  @override
  Future<void> deleteConfig(String id) async {}

  @override
  Future<ModelConfig> createSystemConfigDraft() async {
    return const ModelConfig(
      id: 'mock_draft',
      slug: 'mock_draft_slug',
      type: 'model_registry',
    );
  }

  @override
  Future<ModelConfig> cloneConfig(String id) async {
    return const ModelConfig(
      id: 'cloned',
      slug: 'cloned_slug',
      type: 'model_registry',
      models: {},
    );
  }
}
