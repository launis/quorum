import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/views/model_registry_view.dart';
import 'package:client_app/features/studio/controllers/model_registry_controller.dart';
import 'package:client_app/features/studio/models/gcp_location.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import 'package:client_app/features/studio/models/llm_platform.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  const List<GcpLocation> mockLocations = [
    GcpLocation(
      id: 'europe-north1',
      label: 'Hamina, Finland (europe-north1)',
      description: 'Google Cloud Vertex AI region: Hamina, Finland',
    ),
    GcpLocation(
      id: 'europe-west1',
      label: 'St. Ghislain, Belgium (europe-west1)',
      description: 'Google Cloud Vertex AI region: St. Ghislain, Belgium',
    ),
  ];

  const List<LlmPlatform> mockPlatforms = [
    LlmPlatform(id: 'vertex_ai', label: 'Google Vertex AI', hasRegions: true),
    LlmPlatform(id: 'ai_studio', label: 'Google AI Studio', hasRegions: false),
    LlmPlatform(id: 'openai', label: 'OpenAI', hasRegions: false),
    LlmPlatform(id: 'anthropic', label: 'Anthropic', hasRegions: false),
  ];

  const String kStdId = 'cfg_0195f000000070008000000000000001';
  const String kRawId = 'cfg_0195f000000070008000000000000002';
  const String kGemId = 'cfg_0195f000000070008000000000000003';
  const String kDirtyId = 'cfg_0195f000000070008000000000000004';
  const String kCloneId = 'cfg_0195f000000070008000000000000005';
  const String kDynId = 'cfg_0195f000000070008000000000000006';
  const String kSwitchId = 'cfg_0195f000000070008000000000000007';
  const String kErrId = 'cfg_0195f000000070008000000000000008';
  const String kValErrId = 'cfg_0195f000000070008000000000000009';

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
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kStdId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kStdId,
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
              home: const ModelRegistryView(id: kStdId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
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
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kRawId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kRawId,
                  slug: 'syscfg_raw_slug',
                  type: 'model_registry',
                  defaultProvider: 'vertex_ai',
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
                      provider: 'vertex_ai',
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
              home: const ModelRegistryView(id: kRawId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
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
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kGemId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kGemId,
                  slug: 'syscfg_gemini38_slug',
                  type: 'model_registry',
                  defaultProvider: 'ai_studio',
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
                      provider: 'ai_studio',
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
              home: const ModelRegistryView(id: kGemId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
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
          initialLocation: '/edit/$kDirtyId',
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
              modelRegistryByIdProvider(kDirtyId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kDirtyId,
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
          await Future<void>.delayed(const Duration(milliseconds: 100));
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

    testWidgets('in-view clone button triggers cloneConfig on controller', (
      WidgetTester tester,
    ) async {
      final mockController = MockModelRegistryController();

      final router = GoRouter(
        initialLocation: '/studio/model-registry/edit/$kCloneId',
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
            modelRegistryByIdProvider(kCloneId).overrideWith(
              (ref) async => const ModelConfig(
                id: kCloneId,
                slug: 'syscfg_clone_slug',
                type: 'model_registry',
                name: 'Stack to Clone',
                defaultProvider: 'openai',
                tierDefinitions: {},
              ),
            ),
            modelRegistryControllerProvider.overrideWith(() => mockController),
          ],
          child: MaterialApp.router(
            routerConfig: router,
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
          ),
        ),
      );

      await tester.runAsync(() async {
        await Future<void>.delayed(const Duration(milliseconds: 100));
      });
      await tester.pumpAndSettle();

      // Find Clone button in AppBar
      final cloneButton = find.byTooltip('Clone Stack');
      expect(cloneButton, findsOneWidget);

      await tester.tap(cloneButton);
      await tester.pumpAndSettle();

      expect(mockController.cloneCalled, isTrue);
      expect(mockController.clonedId, kCloneId);
    });

    testWidgets(
      'dynamically populates model items from availableModelsProvider in tier dropdown and updates selection',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 1000);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final mockModels = ['gemini-2.5-flash', 'gemini-2.5-pro'];
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
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kDynId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kDynId,
                  slug: 'syscfg_dynamic_slug',
                  type: 'model_registry',
                  defaultProvider: 'vertex_ai',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'gemini-2.5-flash',
                      provider: 'vertex_ai',
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
              home: const ModelRegistryView(id: kDynId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // 1. Verify fast model dropdown is present and has current value
        final fastDropdown = find.byKey(const ValueKey('fast_model_name'));
        expect(fastDropdown, findsOneWidget);
        await tester.ensureVisible(fastDropdown);
        await tester.pumpAndSettle();
        expect(find.text('gemini-2.5-flash'), findsWidgets);

        // 2. Open dropdown and select 'gemini-2.5-pro'
        await tester.tap(fastDropdown);
        await tester.pumpAndSettle();

        final optionPro = find.text('gemini-2.5-pro').last;
        await tester.tap(optionPro);
        await tester.pumpAndSettle();

        expect(find.text('gemini-2.5-pro'), findsWidgets);
      },
    );

    testWidgets(
      'renders location dropdown conditionally when switching defaultProvider to vertex_ai',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1200, 1000);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final mockController = MockModelRegistryController();

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith(
                (ref, _) async => ['gemini-2.5-flash'],
              ),
              supportedLocationsProvider.overrideWith(
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kSwitchId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kSwitchId,
                  slug: 'syscfg_switch_slug',
                  type: 'model_registry',
                  defaultProvider: 'ai_studio',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'gemini-2.5-flash',
                      provider: 'ai_studio',
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
              home: const ModelRegistryView(id: kSwitchId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // Initially ai_studio -> Location dropdown NOT rendered
        expect(
          find.byKey(const ValueKey('model_registry_location_field')),
          findsNothing,
        );

        // Tap defaultProvider dropdown
        final providerDropdown = find.byKey(
          const ValueKey('model_registry_default_provider_field'),
        );
        expect(providerDropdown, findsOneWidget);
        await tester.tap(providerDropdown);
        await tester.pumpAndSettle();

        // Select 'Google Vertex AI (Enterprise)'
        final vertexOption = find.text('Google Vertex AI (Enterprise)').last;
        await tester.tap(vertexOption);
        await tester.pumpAndSettle();

        // Location dropdown should now be rendered
        expect(
          find.byKey(const ValueKey('model_registry_location_field')),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'negative boundary: gracefully handles availableModelsProvider error state without crashing',
      (WidgetTester tester) async {
        final mockController = MockModelRegistryController();

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith(
                (ref, _) => Future<List<String>>.error(
                  Exception('Network timeout discovering models'),
                ),
              ),
              supportedLocationsProvider.overrideWith(
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kErrId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kErrId,
                  slug: 'syscfg_err_slug',
                  type: 'model_registry',
                  defaultProvider: 'vertex_ai',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'custom-model-v1',
                      provider: 'vertex_ai',
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
              home: const ModelRegistryView(id: kErrId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        // The view still renders without throwing
        expect(
          find.byKey(const ValueKey('model_registry_name_field')),
          findsOneWidget,
        );
        expect(find.text('custom-model-v1'), findsWidgets);
      },
    );

    testWidgets(
      'negative boundary: rejects non-numeric temperature and non-integer maxTokens inputs on save',
      (WidgetTester tester) async {
        final mockController = MockModelRegistryController();

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              supportedPlatformsProvider.overrideWith(
                (ref) async => mockPlatforms,
              ),
              availableModelsProvider.overrideWith(
                (ref, _) async => ['gpt-4o'],
              ),
              supportedLocationsProvider.overrideWith(
                (ref) async => mockLocations,
              ),
              modelRegistryByIdProvider(kValErrId).overrideWith(
                (ref) async => const ModelConfig(
                  id: kValErrId,
                  slug: 'syscfg_val_err_slug',
                  type: 'model_registry',
                  defaultProvider: 'openai',
                  tierDefinitions: {
                    'fast': LlmModelConfig(
                      modelName: 'gpt-4o',
                      provider: 'openai',
                      temperature: 0.5,
                      maxTokens: 2048,
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
              home: const ModelRegistryView(id: kValErrId),
            ),
          ),
        );

        await tester.runAsync(() async {
          await Future<void>.delayed(const Duration(milliseconds: 100));
        });
        await tester.pumpAndSettle();

        final tempField = find.byKey(const ValueKey('fast_temp'));
        final maxTokensField = find.byKey(const ValueKey('fast_max_tokens'));
        await tester.ensureVisible(tempField);
        await tester.enterText(tempField, 'not_a_number');
        await tester.ensureVisible(maxTokensField);
        await tester.enterText(maxTokensField, '3.14_not_int');
        await tester.pumpAndSettle();

        final saveBtn = find.text('Save');
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(find.text('Must be a number'), findsOneWidget);
        expect(find.text('Must be an integer'), findsOneWidget);
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
        id: 'cfg_0195f000000070008000000000000001',
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
      id: 'cfg_0195f000000070008000000000000010',
      slug: 'mock_draft_slug',
      type: 'model_registry',
    );
  }

  @override
  Future<ModelConfig> cloneConfig(String id) async {
    cloneCalled = true;
    clonedId = id;
    return const ModelConfig(
      id: 'cfg_0195f000000070008000000000000011',
      slug: 'cloned_slug',
      type: 'model_registry',
      name: 'Stack to Clone (Copy)',
      tierDefinitions: {},
    );
  }
}
