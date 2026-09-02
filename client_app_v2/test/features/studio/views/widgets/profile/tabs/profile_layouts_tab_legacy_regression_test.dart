import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockNullOutputProfileForm extends OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String id) {
    throw StateError(
      'Profile payload must not be null when rendering ProfileStructureTab',
    );
  }
}

class TestOutputProfileForm extends OutputProfileForm {
  OutputProfile currentProfile;
  TestOutputProfileForm(this.currentProfile);

  @override
  FutureOr<OutputProfile> build(String id) {
    return currentProfile;
  }

  @override
  void updatePayload(OutputProfile updatedData) {
    currentProfile = updatedData;
    state = AsyncData(updatedData);
  }
}

class MockPromptBlocksController extends PromptBlocksController {
  @override
  FutureOr<List<PromptBlock>> build() async => [];
}

class MockWorkflowsController extends WorkflowsController {
  final List<Workflow> workflows;
  MockWorkflowsController(this.workflows);

  @override
  FutureOr<List<Workflow>> build() async => workflows;
}

class MockStepsController extends StepsController {
  @override
  FutureOr<List<NodeStrategy>> build() async => [];
}

void main() {
  group('ProfileStructureTab Legacy SynthesisTextBlock Regression Tests', () {
    testWidgets(
      'test_structure_tab_renders_legacy_profile_with_synthesis_text_block_without_assertion_error',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final testWorkflow = Workflow(
          id: 'wf_test',
          slug: 'wf-test',
          name: const I18nText(translations: {'en': 'Test Flow'}),
          description: const I18nText(
            translations: {'en': 'Test Flow Description'},
          ),
          steps: [],
        );

        // Historical / seed database output profile containing legacy synthesisTextBlock in targetBlockOrder
        final legacyProfile = OutputProfile(
          id: 'prf_legacy',
          workflowId: 'wf_test',
          name: const I18nText(translations: {'en': 'Legacy Profile'}),
          targetBlockOrder: [
            TargetBlockType.metadataBlock,
            TargetBlockType.executiveSummaryBlock,
            TargetBlockType
                .synthesisTextBlock, // Legacy block that was demolished from UI
            TargetBlockType.matrixGraphsBlock,
            TargetBlockType.groupedExtensionsBlock,
            TargetBlockType.penaltiesBlock,
            TargetBlockType.matrixSummaryTableBlock,
            TargetBlockType.varianceValidationBlock,
            TargetBlockType.authenticityEvaluationBlock,
            TargetBlockType.printableSourcesBlock,
          ],
          visibleWorkflowExtensions: [],
        );

        final formNotifier = TestOutputProfileForm(legacyProfile);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              outputProfileFormProvider(
                'prf_legacy',
              ).overrideWith(() => formNotifier),
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
            ],
            child: const MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              locale: Locale('en'),
              home: Scaffold(body: ProfileStructureTab(id: 'prf_legacy')),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Must not throw Flutter Framework ReorderableListView assertion error
        expect(tester.takeException(), isNull);
      },
    );
  });
}
