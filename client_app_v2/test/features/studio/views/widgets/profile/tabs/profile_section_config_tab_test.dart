import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/executive_summary_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class TestOutputProfileForm extends OutputProfileForm {
  final AsyncValue<OutputProfile> _initialState;
  TestOutputProfileForm(this._initialState);

  @override
  FutureOr<OutputProfile> build(String id) {
    if (_initialState.hasError) {
      throw _initialState.error!;
    }
    return _initialState.value!;
  }
}

class MockNullOutputProfileForm extends OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String id) {
    throw StateError(
      'Profile payload must not be null when rendering ProfileSectionConfigTab',
    );
  }
}

class MockPromptBlocksController extends PromptBlocksController {
  @override
  FutureOr<List<PromptBlock>> build() async => [];
}

class MockWorkflowsController extends WorkflowsController {
  final List<Workflow> _workflows;
  MockWorkflowsController([this._workflows = const []]);

  @override
  FutureOr<List<Workflow>> build() async => _workflows;
}

class MockStepsController extends StepsController {
  @override
  FutureOr<List<NodeStrategy>> build() async => [];
}

OutputProfile _createProfile({
  String workflowId = 'wf_test',
  List<TargetBlockType>? targetBlockOrder,
  int? synthesisLengthConstraint,
}) {
  return OutputProfile(
    id: 'prf_test',
    workflowId: workflowId,
    slug: 'prf-test',
    name: const I18nText(translations: {'en': 'Test Profile'}),
    targetBlockOrder:
        targetBlockOrder ??
        [
          TargetBlockType.executiveSummaryBlock,
          TargetBlockType.matrixGraphsBlock,
        ],
    synthesisLengthConstraint: synthesisLengthConstraint,
  );
}

void main() {
  group('ProfileSectionConfigTab Master-Detail Tests', () {
    testWidgets('throws StateError when payload is missing (Fail-Fast)', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'prf_test',
            ).overrideWith(() => MockNullOutputProfileForm()),
            workflowsControllerProvider.overrideWith(
              () => MockWorkflowsController(),
            ),
            promptBlocksControllerProvider.overrideWith(
              () => MockPromptBlocksController(),
            ),
            stepsControllerProvider.overrideWith(() => MockStepsController()),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileSectionConfigTab(id: 'prf_test')),
          ),
        ),
      );

      expect(tester.takeException(), isA<StateError>());
    });

    testWidgets(
      'renders Master list of active sections and navigates to Detail and back',
      (WidgetTester tester) async {
        final profile = _createProfile();
        final testWorkflow = Workflow(
          id: 'wf_test',
          slug: 'wf-test',
          name: const I18nText(translations: {'en': 'Test Flow'}),
          description: const I18nText(
            translations: {'en': 'Test Flow Description'},
          ),
          steps: [],
        );

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              outputProfileFormProvider(
                'prf_test',
              ).overrideWith(() => TestOutputProfileForm(AsyncData(profile))),
              workflowsControllerProvider.overrideWith(
                () => MockWorkflowsController([testWorkflow]),
              ),
              promptBlocksControllerProvider.overrideWith(
                () => MockPromptBlocksController(),
              ),
              stepsControllerProvider.overrideWith(() => MockStepsController()),
              workflowAvailableExtensionsProvider(
                'wf_test',
              ).overrideWith((ref) async => []),
            ],
            child: const MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(body: ProfileSectionConfigTab(id: 'prf_test')),
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Master List: Should show ListTile items for Executive Summary and Matrix Graphs
        expect(find.text('Executive Summary'), findsOneWidget);
        expect(find.text('Matrix Visualizations & Graphs'), findsOneWidget);

        // Tap Executive Summary to open Detail View
        await tester.tap(find.text('Executive Summary'));
        await tester.pumpAndSettle();

        // Detail View: Should show Back button and ExecutiveSummaryBlockCard with fields
        expect(find.text('All Sections'), findsOneWidget);
        expect(find.byType(ExecutiveSummaryBlockCard), findsOneWidget);
        expect(find.byKey(const Key('profile_executive_summary_directive_field')), findsOneWidget);
        expect(find.byType(TextFormField), findsNWidgets(2));

        // Tap Back button
        await tester.tap(find.text('All Sections'));
        await tester.pumpAndSettle();

        // Returned to Master List
        expect(find.text('Executive Summary'), findsOneWidget);
        expect(find.text('Matrix Visualizations & Graphs'), findsOneWidget);
        expect(find.byType(ExecutiveSummaryBlockCard), findsNothing);
      },
    );
  });
}
