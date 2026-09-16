import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
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

  group('ModelRegistryView Desktop Pro Tool UX Tests', () {
    testWidgets(
      'renders standard model with 1200px bounded canvas, name field, 4 canonical tier cards, and sampling controls',
      (WidgetTester tester) async {
        final mockModels = ['gpt-4o', 'gpt-3.5-turbo'];
        final mockController = MockModelRegistryController();

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
                  name: 'Production Sovereign Stack',
                  defaultProvider: 'openai',
                  tierDefinitions: {
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
                    'balanced': LlmModelConfig(
                      modelName: 'gpt-4o-mini',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'deep': LlmModelConfig(
                      modelName: 'o1',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'reasoning': LlmModelConfig(
                      modelName: 'o3-mini',
                      provider: 'openai',
                      thinkingBudgetTokens: 4096,
                      isActive: true,
                    ),
                  },
                ),
              ),
              modelRegistryControllerProvider.overrideWith(
                () => mockController,
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

        // 1. Verify 1200px Bounded Canvas Containment
        final constrainedBoxes = tester.widgetList<ConstrainedBox>(
          find.byType(ConstrainedBox),
        );
        expect(
          constrainedBoxes.any((cb) => cb.constraints.maxWidth == 1200),
          isTrue,
        );

        // 2. Verify Name Field with initial value
        expect(
          find.byKey(const ValueKey('model_registry_name_field')),
          findsOneWidget,
        );
        expect(find.text('Production Sovereign Stack'), findsOneWidget);

        // 3. Verify Default Provider Dropdown
        expect(
          find.byKey(const ValueKey('model_registry_default_provider_field')),
          findsOneWidget,
        );

        // 4. Verify 4 Canonical Tier Cards are present
        expect(find.byKey(const ValueKey('tier_card_fast')), findsOneWidget);
        expect(
          find.byKey(const ValueKey('tier_card_balanced')),
          findsOneWidget,
        );
        expect(find.byKey(const ValueKey('tier_card_deep')), findsOneWidget);
        expect(
          find.byKey(const ValueKey('tier_card_reasoning')),
          findsOneWidget,
        );

        // 5. Verify Sampling controls exist for standard fast/balanced tiers
        expect(find.text('gpt-4o'), findsWidgets);
        expect(find.text('Temperature'), findsWidgets);
        expect(find.text('Top-P (Nucleus Sampling)'), findsWidgets);
        expect(find.text('Top-K (Candidates)'), findsWidgets);
        expect(find.text('Frequency Penalty'), findsWidgets);
        expect(find.text('Presence Penalty'), findsWidgets);
        expect(find.text('Max Tokens'), findsWidgets);
        expect(find.text('Parsing Mode'), findsWidgets);
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
                  defaultProvider: 'google',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'gpt-4o',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'balanced': LlmModelConfig(
                      modelName: 'gpt-4o-mini',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'deep': LlmModelConfig(
                      modelName: 'vertex_ai/gemini-2.5-pro',
                      provider: 'google',
                      additionalParams: {
                        'platform': 'vertex_ai',
                        'vertex_location': r'${VERTEX_LOCATION}',
                      },
                      isActive: true,
                    ),
                    'reasoning': LlmModelConfig(
                      modelName: 'o3-mini',
                      provider: 'openai',
                      thinkingBudgetTokens: 4096,
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
                  defaultProvider: 'google',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'gpt-4o',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'balanced': LlmModelConfig(
                      modelName: 'gpt-4o-mini',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'deep': LlmModelConfig(
                      modelName: 'claude-3-5-sonnet',
                      provider: 'anthropic',
                      isActive: true,
                    ),
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

        // 1. Verify reasoning notice icon is present
        expect(find.byIcon(Icons.psychology), findsWidgets);

        // 2. Verify thinking budget field is present with initial value
        expect(find.text('8192'), findsOneWidget);
        expect(find.text('Thinking Budget Tokens'), findsOneWidget);

        // 3. Verify non-sampling controls REMAIN visible
        expect(find.text('Max Tokens'), findsWidgets);
        expect(find.text('Parsing Mode'), findsWidgets);

        // 4. Verify Location dropdown is NOT rendered for AI Studio
        expect(find.text('Location / Region'), findsNothing);
      },
    );

    testWidgets(
      'shows discard confirmation dialog on pop when dirty and retains editing on cancel',
      (WidgetTester tester) async {
        final mockController = MockModelRegistryController();

        final router = GoRouter(
          initialLocation: '/edit/syscfg_dirty',
          routes: [
            GoRoute(
              path: '/home',
              builder: (context, state) => const Scaffold(body: Text('Home')),
            ),
            GoRoute(
              path: '/edit/:id',
              builder: (context, state) =>
                  ModelRegistryView(id: state.pathParameters['id']!),
            ),
          ],
        );

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith((ref, _) async => []),
              supportedLocationsProvider.overrideWith((ref) async => []),
              modelRegistryByIdProvider('syscfg_dirty').overrideWith(
                (ref) async => const ModelConfig(
                  id: 'syscfg_dirty',
                  slug: 'syscfg_dirty_slug',
                  type: 'model_registry',
                  name: 'Initial Pristine Stack',
                  defaultProvider: 'openai',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'gpt-4o',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'balanced': LlmModelConfig(
                      modelName: 'gpt-4o-mini',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'deep': LlmModelConfig(
                      modelName: 'o1',
                      provider: 'openai',
                      isActive: true,
                    ),
                    'reasoning': LlmModelConfig(
                      modelName: 'o3-mini',
                      provider: 'openai',
                      thinkingBudgetTokens: 4096,
                      isActive: true,
                    ),
                  },
                ),
              ),
              modelRegistryControllerProvider.overrideWith(
                () => mockController,
              ),
            ],
            child: MaterialApp.router(
              routerConfig: router,
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // 1. Mutate Name to make form dirty
        final nameField = find.byKey(
          const ValueKey('model_registry_name_field'),
        );
        expect(nameField, findsOneWidget);
        await tester.enterText(nameField, 'Dirty Modified Stack Name');
        await tester.pumpAndSettle();

        // 2. Trigger back navigation via leading AppBar back button
        final backBtn = find.byIcon(Icons.arrow_back);
        expect(backBtn, findsOneWidget);
        await tester.tap(backBtn);
        await tester.pumpAndSettle();

        // 3. Confirm Discard modal appears
        expect(find.text('Discard Changes?'), findsOneWidget);
        expect(find.text('Continue Editing'), findsOneWidget);
        expect(find.text('Discard Changes'), findsOneWidget);

        // 4. Click 'Continue Editing' -> modal closes, form remains
        await tester.tap(find.text('Continue Editing'));
        await tester.pumpAndSettle();
        expect(find.text('Discard Changes?'), findsNothing);
        expect(
          find.byKey(const ValueKey('model_registry_name_field')),
          findsOneWidget,
        );

        // 5. Trigger back navigation again, click 'Discard Changes' -> leaves view
        await tester.tap(backBtn);
        await tester.pumpAndSettle();
        expect(find.text('Discard Changes?'), findsOneWidget);
        await tester.tap(find.text('Discard Changes'));
        await tester.pumpAndSettle();
        expect(find.text('Discard Changes?'), findsNothing);
      },
    );

    testWidgets(
      'in-view clone button triggers cloneConfig on controller',
      (WidgetTester tester) async {
        final mockController = MockModelRegistryController();

        final router = GoRouter(
          initialLocation: '/studio/model-registry/edit/syscfg_clone',
          routes: [
            GoRoute(
              path: '/studio/model-registry/edit/:id',
              builder: (context, state) =>
                  ModelRegistryView(id: state.pathParameters['id']!),
            ),
          ],
        );

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith((ref, _) async => []),
              supportedLocationsProvider.overrideWith((ref) async => []),
              modelRegistryByIdProvider('syscfg_clone').overrideWith(
                (ref) async => const ModelConfig(
                  id: 'syscfg_clone',
                  slug: 'syscfg_clone_slug',
                  type: 'model_registry',
                  name: 'Stack to Clone',
                  defaultProvider: 'openai',
                  tierDefinitions: {},
                ),
              ),
              modelRegistryControllerProvider.overrideWith(
                () => mockController,
              ),
            ],
            child: MaterialApp.router(
              routerConfig: router,
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // Find Clone button in AppBar
        final cloneButton = find.byTooltip('Clone Stack');
        expect(cloneButton, findsOneWidget);

        await tester.tap(cloneButton);
        await tester.pumpAndSettle();

        expect(mockController.cloneCalled, isTrue);
        expect(mockController.clonedId, 'syscfg_clone');
      },
    );
  });
}

class MockModelRegistryController extends AsyncNotifier<List<ModelConfig>>
    implements ModelRegistryController {
  bool cloneCalled = false;
  String? clonedId;

  @override
  Future<List<ModelConfig>> build() async {
    return const [
      ModelConfig(
        id: 'syscfg_123',
        slug: 'syscfg_123_slug',
        type: 'model_registry',
        name: 'Production Sovereign Stack',
        tierDefinitions: {
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
    cloneCalled = true;
    clonedId = id;
    return const ModelConfig(
      id: 'cloned',
      slug: 'cloned_slug',
      type: 'model_registry',
      name: 'Stack to Clone (Copy)',
      tierDefinitions: {},
    );
  }
}
