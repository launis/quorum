import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/features/studio/views/output_profile_crud_view.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/metadata_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

class FakeOutputProfile extends Fake implements OutputProfile {}

class MockOutputProfilesController extends OutputProfilesController {
  final Future<OutputProfile> Function(String id, OutputProfile payload)?
  onSaveProfile;

  MockOutputProfilesController({this.onSaveProfile});

  @override
  Future<OutputProfile> saveProfile(String id, OutputProfile payload) async {
    if (onSaveProfile != null) {
      return onSaveProfile!(id, payload);
    }
    return payload;
  }
}

class MockWorkflowsController extends WorkflowsController {
  final List<Workflow> workflows;
  MockWorkflowsController([this.workflows = const []]);

  @override
  FutureOr<List<Workflow>> build() async {
    return workflows;
  }
}

class MockStepsController extends StepsController {
  final List<NodeStrategy> steps;
  MockStepsController([this.steps = const []]);

  @override
  FutureOr<List<NodeStrategy>> build() async {
    return steps;
  }
}

class MockPromptBlocksController extends PromptBlocksController {
  final List<PromptBlock> promptBlocks;
  MockPromptBlocksController([this.promptBlocks = const []]);

  @override
  FutureOr<List<PromptBlock>> build() async {
    return promptBlocks;
  }
}

class TestOutputProfileForm extends OutputProfileForm {
  final AsyncValue<OutputProfile> initialFormState;
  final Future<void> Function(OutputProfile updatedData)? onSubmit;

  TestOutputProfileForm(this.initialFormState, {this.onSubmit});

  @override
  Future<OutputProfile> build(String configId) async {
    return switch (initialFormState) {
      AsyncData(:final value) => value,
      AsyncError(:final error, :final stackTrace) => Error.throwWithStackTrace(
        error,
        stackTrace,
      ),
      _ => Completer<OutputProfile>().future, // Hangs for AsyncLoading
    };
  }

  @override
  Future<void> submit(OutputProfile updatedData) async {
    if (onSubmit != null) {
      await onSubmit!(updatedData);
      return;
    }
    await super.submit(updatedData);
  }
}

void main() {
  setUpAll(() {
    registerFallbackValue(FakeOutputProfile());
  });

  OutputProfile createValidProfile({
    String id = 'prf_test',
    String slug = 'exec-summary',
    String workflowId = 'wf_test',
    String nameEn = 'Executive Summary Profile',
    int maxExtensionItems = 3,
    DisplayScale displayScale = DisplayScale.original,
    int strictnessLevel = 50,
    ScoringStrategy scoringStrategy = ScoringStrategy.waterfall,
    List<String> visibleMetadata = const ['date', 'user', 'organization'],
    List<XaiExtensionType> visibleBlockExtensions = const [
      XaiExtensionType.citation,
    ],
    List<XaiExtensionType> visibleWorkflowExtensions = const [
      XaiExtensionType.varianceValidation,
    ],
    List<OutputLayoutBlock> layouts = const [],
    List<TargetBlockType> targetBlockOrder = const [
      TargetBlockType.metadataBlock,
    ],
  }) {
    return OutputProfile(
      id: id,
      slug: slug,
      workflowId: workflowId,
      name: I18nText(translations: {'en': nameEn, 'fi': 'Johdon yhteenveto'}),
      description: const I18nText(translations: {'en': 'Test description'}),
      customPreface: const I18nText(translations: {'en': 'Test preface'}),
      displayScale: displayScale,
      strictnessLevel: strictnessLevel,
      scoringStrategy: scoringStrategy,
      visibleMetadata: visibleMetadata,
      maxExtensionItems: maxExtensionItems,
      visibleBlockExtensions: visibleBlockExtensions,
      visibleWorkflowExtensions: visibleWorkflowExtensions,
      layouts: layouts,
      targetBlockOrder: targetBlockOrder,
    );
  }

  Widget createWidgetUnderTest({
    required String profileId,
    required dynamic overrides,
    Size viewportSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      overrides: overrides,
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
        home: MediaQuery(
          data: MediaQueryData(size: viewportSize),
          child: OutputProfileCrudView(id: profileId),
        ),
      ),
    );
  }

  group('Golden Master: OutputProfileCrudView Characterization Tests', () {
    testWidgets('test_crud_view_renders_loading_state', (
      WidgetTester tester,
    ) async {
      // Input: outputProfileFormProvider overridden with AsyncLoading
      final overrides = [
        outputProfileFormProvider(
          'prf_loading',
        ).overrideWith(() => TestOutputProfileForm(const AsyncLoading())),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider('').overrideWith((ref) async => []),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_loading', overrides: overrides),
      );

      // Expected: finds CircularProgressIndicator widget in AppBar body
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('test_crud_view_renders_error_state', (
      WidgetTester tester,
    ) async {
      // Input: outputProfileFormProvider overridden with AsyncError
      final testError = AppException.validation('Failed to load profile');
      final overrides = [
        outputProfileFormProvider('prf_error').overrideWith(
          () =>
              TestOutputProfileForm(AsyncError(testError, StackTrace.current)),
        ),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider('').overrideWith((ref) async => []),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_error', overrides: overrides),
      );
      await tester.pumpAndSettle();

      // Expected: finds ErrorView widget displaying the error message
      expect(find.byType(ErrorView), findsOneWidget);
    });

    testWidgets('test_crud_view_renders_data_state_wide_screen', (
      WidgetTester tester,
    ) async {
      // Input: Valid OutputProfile with 1920x1080 viewport
      final profile = createValidProfile();
      final overrides = [
        outputProfileFormProvider(
          'prf_test',
        ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => ['citation']),
      ];

      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        createWidgetUnderTest(
          profileId: 'prf_test',
          overrides: overrides,
          viewportSize: const Size(1920, 1080),
        ),
      );
      await tester.pumpAndSettle();

      // Expected: renders 3-tab layout without assertion or overflow errors
      expect(find.byType(TabBar), findsOneWidget);
      expect(find.byType(TabBarView), findsOneWidget);
      expect(find.text('prf_test'), findsOneWidget);
      expect(find.byIcon(Icons.save), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('test_crud_view_renders_data_state_narrow_screen', (
      WidgetTester tester,
    ) async {
      // Input: Valid OutputProfile with 800x600 viewport
      final profile = createValidProfile();
      final overrides = [
        outputProfileFormProvider(
          'prf_test',
        ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => ['citation']),
      ];

      tester.view.physicalSize = const Size(800, 600);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        createWidgetUnderTest(
          profileId: 'prf_test',
          overrides: overrides,
          viewportSize: const Size(800, 600),
        ),
      );
      await tester.pumpAndSettle();

      // Expected: renders TabBar layout without assertion or overflow errors
      expect(find.byType(TabBar), findsOneWidget);
      expect(find.text('prf_test'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('test_crud_view_displays_identity_and_scoring_fields', (
      WidgetTester tester,
    ) async {
      // Input: OutputProfile with name "Executive Summary Profile", slug "exec-summary", strictness balanced
      final profile = createValidProfile(
        nameEn: 'Executive Summary Profile',
        slug: 'exec-summary',
        strictnessLevel: 50,
        scoringStrategy: ScoringStrategy.waterfall,
      );
      final overrides = [
        outputProfileFormProvider(
          'prf_test',
        ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => []),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
      );
      await tester.pumpAndSettle();

      // Expected on Tab 1: finds TextFormField containing ID and slug, finds display name
      expect(find.text('prf_test'), findsOneWidget);
      expect(find.text('exec-summary'), findsOneWidget);
      expect(find.text('Executive Summary Profile'), findsOneWidget);

      // Switch to Tab 2 (Scoring)
      await tester.tap(find.text('Scoring'));
      await tester.pumpAndSettle();

      // Expected on Tab 2: finds strictness and scoring strategy dropdowns
      expect(find.text('Balanced (50 - Default)'), findsOneWidget);
    });

    testWidgets('test_crud_view_displays_workflow_selector_and_extensions', (
      WidgetTester tester,
    ) async {
      // Input: Valid OutputProfile with workflowId "wf_test" and available extensions ["citation", "justification"]
      final testWorkflow = Workflow(
        id: 'wf_test',
        slug: 'wf-test',
        name: const I18nText(translations: {'en': 'Test Flow'}),
        description: const I18nText(
          translations: {'en': 'Test Flow Description'},
        ),
        steps: [],
      );
      final profile = createValidProfile(
        workflowId: 'wf_test',
        targetBlockOrder: [TargetBlockType.groupedExtensionsBlock],
      );
      final overrides = [
        outputProfileFormProvider(
          'prf_test',
        ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController([testWorkflow]),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => ['citation', 'justification']),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
      );
      await tester.pumpAndSettle();

      // Expected on Tab 1: finds DropdownButtonFormField with "Test Flow (wf_test)"
      expect(find.text('Test Flow (wf_test)'), findsOneWidget);

      // Switch to Tab 3 (Report Structure)
      await tester.tap(find.text('Report Structure'));
      await tester.pumpAndSettle();

      // Expected on Tab 3: finds FilterChip for citation and justification in XaiExtensionsBlockCard
      expect(
        find.widgetWithText(FilterChip, 'Source Citation'),
        findsOneWidget,
      );
      expect(find.widgetWithText(FilterChip, 'Justification'), findsOneWidget);
    });

    testWidgets('test_crud_view_displays_workflow_warning_when_unselected', (
      WidgetTester tester,
    ) async {
      // Input: OutputProfile with empty workflowId ""
      final profile = createValidProfile(workflowId: '');
      final overrides = [
        outputProfileFormProvider(
          'prf_test',
        ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider('').overrideWith((ref) async => []),
      ];

      tester.view.physicalSize = const Size(1920, 1080);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        createWidgetUnderTest(
          profileId: 'prf_test',
          overrides: overrides,
          viewportSize: const Size(1920, 1080),
        ),
      );
      await tester.pumpAndSettle();

      // Switch to Tab 3 (Report Structure)
      await tester.tap(find.text('Report Structure'));
      await tester.pumpAndSettle();

      // Expected: finds workflowSelectWarning text inside Layout pane
      expect(
        find.textContaining('Please select a Workflow ID Binding above'),
        findsOneWidget,
      );
    });

    testWidgets('test_crud_view_validates_max_extension_items', (
      WidgetTester tester,
    ) async {
      // Input: OutputProfile with maxExtensionItems modified to invalid string "-5" in XaiExtensionsBlockCard
      final profile = createValidProfile(
        maxExtensionItems: 3,
        targetBlockOrder: [TargetBlockType.groupedExtensionsBlock],
      );
      final overrides = [
        outputProfileFormProvider(
          'prf_test',
        ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => []),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
      );
      await tester.pumpAndSettle();

      // Switch to Tab 3 (Report Structure)
      await tester.tap(find.text('Report Structure'));
      await tester.pumpAndSettle();

      // Find TextFormField with initial value '3' in XaiExtensionsBlockCard
      final textFormFieldFinder = find.byWidgetPredicate(
        (widget) => widget is TextFormField && widget.initialValue == '3',
      );
      expect(textFormFieldFinder, findsOneWidget);
      await tester.ensureVisible(textFormFieldFinder);
      await tester.enterText(textFormFieldFinder, '-5');
      await tester.pumpAndSettle();

      // Tap save button
      final saveBtn = find.widgetWithText(TextButton, 'Save');
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Expected: Form validation fails and displays extensionItemsMustBeIntError
      expect(find.text('Given value must be an integer >= 1'), findsOneWidget);
    });

    testWidgets(
      'test_crud_view_navigates_to_layout_tab_and_displays_metadata_card',
      (WidgetTester tester) async {
        final testWorkflow = Workflow(
          id: 'wf_test',
          slug: 'wf-test',
          name: const I18nText(translations: {'en': 'Test Flow'}),
          description: const I18nText(
            translations: {'en': 'Test Flow Description'},
          ),
          steps: [],
        );
        final profile = createValidProfile(
          workflowId: 'wf_test',
          targetBlockOrder: [TargetBlockType.metadataBlock],
          visibleMetadata: ['date', 'organization'],
        );
        final overrides = [
          outputProfileFormProvider(
            'prf_test',
          ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
          promptBlocksControllerProvider.overrideWith(
            () => MockPromptBlocksController(),
          ),
          workflowsControllerProvider.overrideWith(
            () => MockWorkflowsController([testWorkflow]),
          ),
          stepsControllerProvider.overrideWith(() => MockStepsController()),
          workflowAvailableExtensionsProvider(
            'wf_test',
          ).overrideWith((ref) async => []),
        ];

        await tester.pumpWidget(
          createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
        );
        await tester.pumpAndSettle();

        // Switch to Tab 3 (Report Structure)
        await tester.tap(find.text('Report Structure'));
        await tester.pumpAndSettle();

        // Expected: MetadataBlockCard is rendered and displays metadata FilterChips
        expect(find.byType(MetadataBlockCard), findsOneWidget);
        expect(find.widgetWithText(FilterChip, 'date'), findsOneWidget);
        expect(find.widgetWithText(FilterChip, 'organization'), findsOneWidget);
      },
    );

    testWidgets(
      'test_crud_view_navigates_to_layout_tab_and_displays_xai_card',
      (WidgetTester tester) async {
        final testWorkflow = Workflow(
          id: 'wf_test',
          slug: 'wf-test',
          name: const I18nText(translations: {'en': 'Test Flow'}),
          description: const I18nText(
            translations: {'en': 'Test Flow Description'},
          ),
          steps: [],
        );
        final profile = createValidProfile(
          workflowId: 'wf_test',
          targetBlockOrder: [TargetBlockType.groupedExtensionsBlock],
          visibleBlockExtensions: [XaiExtensionType.citation],
        );
        final overrides = [
          outputProfileFormProvider(
            'prf_test',
          ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
          promptBlocksControllerProvider.overrideWith(
            () => MockPromptBlocksController(),
          ),
          workflowsControllerProvider.overrideWith(
            () => MockWorkflowsController([testWorkflow]),
          ),
          stepsControllerProvider.overrideWith(() => MockStepsController()),
          workflowAvailableExtensionsProvider(
            'wf_test',
          ).overrideWith((ref) async => ['citation']),
        ];

        await tester.pumpWidget(
          createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
        );
        await tester.pumpAndSettle();

        // Switch to Tab 3 (Report Structure)
        await tester.tap(find.text('Report Structure'));
        await tester.pumpAndSettle();

        // Expected: XaiExtensionsBlockCard is rendered with filter chips
        expect(find.byType(XaiExtensionsBlockCard), findsOneWidget);
        expect(
          find.widgetWithText(FilterChip, 'Source Citation'),
          findsOneWidget,
        );
      },
    );

    testWidgets('test_crud_view_triggers_save_action', (
      WidgetTester tester,
    ) async {
      // Input: Valid OutputProfile, tap save button
      final profile = createValidProfile();
      OutputProfile? submittedProfile;
      final mockLogger = MockLoggerService();

      final overrides = [
        loggerServiceProvider.overrideWithValue(mockLogger),
        outputProfileFormProvider('prf_test').overrideWith(
          () => TestOutputProfileForm(
            AsyncData(profile),
            onSubmit: (updated) async {
              submittedProfile = updated;
            },
          ),
        ),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => []),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
      );
      await tester.pumpAndSettle();

      // Tap save button
      final saveBtn = find.widgetWithText(TextButton, 'Save');
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Expected: Form submits updated payload to OutputProfileForm notifier
      expect(submittedProfile, isNotNull);
      expect(submittedProfile!.id, 'prf_test');
    });

    testWidgets('test_crud_view_handles_save_failure_gracefully', (
      WidgetTester tester,
    ) async {
      // Input: OutputProfileForm submit throws AppException
      final profile = createValidProfile();
      final mockLogger = MockLoggerService();

      final overrides = [
        loggerServiceProvider.overrideWithValue(mockLogger),
        outputProfileFormProvider('prf_test').overrideWith(
          () => TestOutputProfileForm(
            AsyncData(profile),
            onSubmit: (updated) async {
              throw AppException.validation('Simulated save failure');
            },
          ),
        ),
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(),
        ),
        workflowsControllerProvider.overrideWith(
          () => MockWorkflowsController(),
        ),
        stepsControllerProvider.overrideWith(() => MockStepsController()),
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => []),
      ];

      await tester.pumpWidget(
        createWidgetUnderTest(profileId: 'prf_test', overrides: overrides),
      );
      await tester.pumpAndSettle();

      // Tap save button
      final saveBtn = find.widgetWithText(TextButton, 'Save');
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Expected: ScaffoldMessenger displays error SnackBar, widget tree does not crash
      expect(find.byType(SnackBar), findsOneWidget);
      expect(find.textContaining('Simulated save failure'), findsOneWidget);
    });
  });
}
