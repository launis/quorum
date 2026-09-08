import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/views/model_registry_view.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  final List<Map<String, dynamic>> mockPlatforms = <Map<String, dynamic>>[
    {'id': 'vertex_ai', 'label': 'Google Vertex AI', 'has_regions': true},
    {'id': 'ai_studio', 'label': 'Google AI Studio', 'has_regions': false},
    {'id': 'openai', 'label': 'OpenAI', 'has_regions': false},
    {'id': 'anthropic', 'label': 'Anthropic', 'has_regions': false},
  ];

  group('ModelRegistryView Widget Tests', () {
    testWidgets(
      'renders standard model with sampling controls visible and no reasoning banner',
      (WidgetTester tester) async {
        final mockModels = ['gpt-4o', 'gpt-3.5-turbo'];

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith(
                (ref, _) async => mockModels,
              ),
              supportedLocationsProvider.overrideWith(
                (ref) async => [
                  {
                    'id': 'europe-north1',
                    'label': 'Hamina, Finland (europe-north1)',
                  },
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
                      provider: 'openai',
                      temperature: 0.7,
                      topP: 0.9,
                      topK: 40,
                      frequencyPenalty: 0.0,
                      presencePenalty: 0.0,
                      maxTokens: 4096,
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

        await tester.runAsync(() async {
          await Future.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // Verify model name appears
        expect(find.text('gpt-4o'), findsWidgets);

        // Reasoning notice should NOT be present for standard gpt-4o
        expect(find.byIcon(Icons.psychology), findsNothing);

        // Sampling controls MUST be visible for standard models
        expect(find.text('Temperature'), findsOneWidget);
        expect(find.text('Top-P (Nucleus Sampling)'), findsOneWidget);
        expect(find.text('Top-K (Candidates)'), findsOneWidget);
        expect(find.text('Frequency Penalty'), findsOneWidget);
        expect(find.text('Presence Penalty'), findsOneWidget);

        // Non-sampling controls are visible
        expect(find.text('Max Tokens'), findsOneWidget);
        expect(find.text('Parsing Mode'), findsOneWidget);
      },
    );

    testWidgets(
      'renders properly when vertex_location is raw env template or unmapped string',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith(
                (ref, _) async => ['vertex_ai/gemini-2.5-pro'],
              ),
              supportedLocationsProvider.overrideWith(
                (ref) async => [
                  {
                    'id': 'europe-north1',
                    'label': 'Hamina, Finland (europe-north1)',
                  },
                  {
                    'id': 'europe-west1',
                    'label': 'St. Ghislain, Belgium (europe-west1)',
                  },
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
                        'platform': 'vertex_ai',
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

        // Location dropdown should be rendered for vertex_ai
        expect(find.byType(DropdownButtonFormField<String>), findsWidgets);
        expect(find.text('Location / Region'), findsOneWidget);
      },
    );

    testWidgets(
      'renders reasoning notice and hides sampling fields for Gemini 3.8 Flash',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith(
                (ref, _) async => ['gemini/gemini-3.8-flash'],
              ),
              supportedLocationsProvider.overrideWith(
                (ref) async => [
                  {
                    'id': 'europe-north1',
                    'label': 'Hamina, Finland (europe-north1)',
                  },
                ],
              ),
              modelRegistryByIdProvider('syscfg_gemini38').overrideWith(
                (ref) async => const ModelConfig(
                  id: 'syscfg_gemini38',
                  slug: 'syscfg_gemini38_slug',
                  type: 'model_registry',
                  models: {
                    'reasoning': LlmModelConfig(
                      modelName: 'gemini/gemini-3.8-flash',
                      provider: 'google',
                      thinkingBudgetTokens: 8192,
                      additionalParams: {'platform': 'ai_studio'},
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
              home: const ModelRegistryView(id: 'syscfg_gemini38'),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // 1. Verify reasoning notice icon and text are present
        expect(find.byIcon(Icons.psychology), findsOneWidget);

        // 2. Verify thinking budget field is present with initial value
        expect(find.text('8192'), findsOneWidget);
        expect(find.text('Thinking Budget Tokens'), findsOneWidget);

        // 3. Verify ALL sampling controls are HIDDEN for reasoning models
        expect(find.text('Temperature'), findsNothing);
        expect(find.text('Top-P (Nucleus Sampling)'), findsNothing);
        expect(find.text('Top-K (Candidates)'), findsNothing);
        expect(find.text('Frequency Penalty'), findsNothing);
        expect(find.text('Presence Penalty'), findsNothing);

        // 4. Verify non-sampling controls REMAIN visible
        expect(find.text('Max Tokens'), findsOneWidget);
        expect(find.text('Parsing Mode'), findsOneWidget);

        // 5. Verify Location dropdown is NOT rendered for AI Studio
        expect(find.text('Location / Region'), findsNothing);
      },
    );
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
            provider: 'openai',
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
