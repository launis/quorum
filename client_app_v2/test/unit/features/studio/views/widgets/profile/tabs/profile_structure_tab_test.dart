import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_structure_tab.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

class _FakeOutputProfileForm extends OutputProfileForm {
  final OutputProfile? initialPayload;
  final Object? initialError;
  final bool stayLoading;

  _FakeOutputProfileForm({
    this.initialPayload,
    this.initialError,
    this.stayLoading = false,
  });

  @override
  FutureOr<OutputProfile> build(String configId) {
    if (stayLoading) {
      return Completer<OutputProfile>().future;
    }
    if (initialError != null) {
      throw initialError!;
    }
    return initialPayload!;
  }
}

void main() {
  const testProfileId = 'op_0195f3a0000070008000000000000300';
  const testWorkflowId = 'wf_0195f3a0000070008000000000000001';

  OutputProfile buildProfile({
    required List<TargetBlockType> targetBlockOrder,
    List<XaiExtensionType> visibleWorkflowExtensions = const [],
  }) {
    return OutputProfile(
      id: testProfileId,
      slug: 'test_profile',
      workflowId: testWorkflowId,
      name: const I18nText(
        translations: {'en': 'Test Profile', 'fi': 'Testiprofiili'},
      ),
      targetBlockOrder: targetBlockOrder,
      visibleWorkflowExtensions: visibleWorkflowExtensions,
    );
  }

  Widget createTestWidget({
    required _FakeOutputProfileForm Function() formNotifierBuilder,
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [
        outputProfileFormProvider(
          testProfileId,
        ).overrideWith(formNotifierBuilder),
      ],
      child: MaterialApp(
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: const Scaffold(body: ProfileStructureTab(id: testProfileId)),
      ),
    );
  }

  group('ProfileStructureTab Widget & ISTQB Boundary Tests', () {
    testWidgets(
      'Positive: renders active blocks (filtering out synthesisTextBlock), renders inactive block tray, and synchronizes workflow extensions when adding varianceValidationBlock',
      (WidgetTester tester) async {
        final initialProfile = buildProfile(
          targetBlockOrder: const [
            TargetBlockType.metadataBlock,
            TargetBlockType.executiveSummaryBlock,
            TargetBlockType.synthesisTextBlock,
          ],
          visibleWorkflowExtensions: const [],
        );

        await tester.pumpWidget(
          createTestWidget(
            formNotifierBuilder: () =>
                _FakeOutputProfileForm(initialPayload: initialProfile),
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        // Synthesis text block is filtered out, leaving 2 active blocks
        expect(find.text(l10n.reportVisualBlocksHeader), findsOneWidget);
        expect(find.text(l10n.activeBlocksCount(2)), findsOneWidget);
        expect(find.byType(SimpleToggleBlockCard), findsNWidgets(2));
        expect(find.text(l10n.blockMetadataTitle), findsOneWidget);
        expect(find.text(l10n.blockExecutiveSummaryTitle), findsOneWidget);
        expect(find.text(l10n.blockSynthesisTextTitle), findsNothing);

        // Inactive tray is visible with remaining 8 blocks
        expect(find.text(l10n.availableBlocksHeader), findsOneWidget);
        expect(find.byType(ActionChip), findsNWidgets(8));

        // Tap varianceValidationBlock ActionChip to activate it and synchronize XaiExtensionType.varianceValidation
        final varianceChip = find.widgetWithText(
          ActionChip,
          l10n.blockVarianceTitle,
        );
        expect(varianceChip, findsOneWidget);
        tester.widget<ActionChip>(varianceChip).onPressed!();
        await tester.pumpAndSettle();

        expect(find.text(l10n.activeBlocksCount(3)), findsOneWidget);
        expect(find.byType(SimpleToggleBlockCard), findsNWidgets(3));
        expect(find.byType(ActionChip), findsNWidgets(7));

        final container = ProviderScope.containerOf(
          tester.element(find.byType(ProfileStructureTab)),
        );
        final updatedState = container.read(
          outputProfileFormProvider(testProfileId),
        );
        final updatedProfile = updatedState.value!;
        expect(
          updatedProfile.targetBlockOrder,
          contains(TargetBlockType.varianceValidationBlock),
        );
        expect(
          updatedProfile.visibleWorkflowExtensions,
          contains(XaiExtensionType.varianceValidation),
        );

        // Reorder active blocks via ReorderableListView callback
        final reorderable = tester.widget<ReorderableListView>(
          find.byType(ReorderableListView),
        );
        reorderable.onReorder(0, 2);
        await tester.pumpAndSettle();

        final reorderedProfile = container
            .read(outputProfileFormProvider(testProfileId))
            .value!;
        expect(
          reorderedProfile.targetBlockOrder.first,
          equals(TargetBlockType.executiveSummaryBlock),
        );
        expect(
          reorderedProfile.targetBlockOrder[1],
          equals(TargetBlockType.metadataBlock),
        );
      },
    );

    testWidgets(
      'Negative Partition 1: throws StateError Fail-Fast when outputProfileFormProvider is in AsyncLoading or AsyncError state',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          createTestWidget(
            formNotifierBuilder: () =>
                _FakeOutputProfileForm(stayLoading: true),
          ),
        );

        final loadingException = tester.takeException();
        expect(loadingException, isA<StateError>());

        await tester.pumpWidget(const SizedBox());
        await tester.pumpWidget(
          createTestWidget(
            formNotifierBuilder: () => _FakeOutputProfileForm(
              initialError: StateError('Backend load failure'),
            ),
          ),
        );

        final errorException = tester.takeException();
        expect(errorException, isA<StateError>());
      },
    );

    testWidgets(
      'Negative Partition 2 (BVA): handles boundary targetBlockOrder sizes (0 active blocks vs all 10 non-synthesis blocks active hiding inactive tray)',
      (WidgetTester tester) async {
        final emptyProfile = buildProfile(
          targetBlockOrder: const [TargetBlockType.synthesisTextBlock],
        );

        await tester.pumpWidget(
          createTestWidget(
            formNotifierBuilder: () =>
                _FakeOutputProfileForm(initialPayload: emptyProfile),
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        // Boundary min (0 active non-synthesis blocks): all 10 available in tray
        expect(find.text(l10n.activeBlocksCount(0)), findsOneWidget);
        expect(find.byType(SimpleToggleBlockCard), findsNothing);
        expect(find.text(l10n.availableBlocksHeader), findsOneWidget);
        expect(find.byType(ActionChip), findsNWidgets(10));

        // Transition to boundary max (all non-synthesis blocks active): inactive tray is hidden
        final container = ProviderScope.containerOf(
          tester.element(find.byType(ProfileStructureTab)),
        );
        container
            .read(outputProfileFormProvider(testProfileId).notifier)
            .updatePayload(
              buildProfile(targetBlockOrder: TargetBlockType.values),
            );
        await tester.pumpAndSettle();

        expect(find.text(l10n.activeBlocksCount(10)), findsOneWidget);
        expect(find.byType(SimpleToggleBlockCard), findsNWidgets(10));
        expect(find.text(l10n.availableBlocksHeader), findsNothing);
        expect(find.byType(ActionChip), findsNothing);
      },
    );
  });
}
