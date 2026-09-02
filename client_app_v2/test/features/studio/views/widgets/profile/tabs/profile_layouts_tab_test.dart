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
  group('ProfileStructureTab Tests', () {
    testWidgets('test_structure_tab_throws_state_error_when_payload_is_null', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'test_id',
            ).overrideWith(() => MockNullOutputProfileForm()),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileStructureTab(id: 'test_id')),
          ),
        ),
      );

      expect(tester.takeException(), isA<StateError>());
    });

    testWidgets(
      'test_add_inactive_variance_block_adds_to_both_order_and_extensions',
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

        final initialProfile = OutputProfile(
          id: 'prf_test',
          workflowId: 'wf_test',
          name: const I18nText(translations: {'en': 'Test Profile'}),
          targetBlockOrder: [TargetBlockType.metadataBlock],
          visibleWorkflowExtensions: [],
        );

        final formNotifier = TestOutputProfileForm(initialProfile);

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              outputProfileFormProvider(
                'prf_test',
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
              home: Scaffold(body: ProfileStructureTab(id: 'prf_test')),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Find the ActionChip for Variance Validation in the available blocks tray
        final varianceChipFinder = find.widgetWithText(
          ActionChip,
          'Variance Validation',
        );
        expect(varianceChipFinder, findsOneWidget);

        await tester.tap(varianceChipFinder);
        await tester.pumpAndSettle();

        expect(
          formNotifier.currentProfile.targetBlockOrder,
          contains(TargetBlockType.varianceValidationBlock),
        );
        expect(
          formNotifier.currentProfile.visibleWorkflowExtensions,
          contains(XaiExtensionType.varianceValidation),
        );
      },
    );
  });
}
