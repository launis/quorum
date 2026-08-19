import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/base_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/block_card_registry.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_summary_table_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/metadata_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/simple_toggle_block_card.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

void main() {
  OutputProfile createTestProfile({
    List<TargetBlockType>? targetBlockOrder,
    int maxExtensionItems = 3,
    List<OutputLayoutBlock> layouts = const [],
    List<String> visibleMetadata = const ['date', 'organization'],
  }) {
    return OutputProfile(
      id: 'prf_test',
      workflowId: 'wf_test',
      name: const I18nText(
        defaultLocale: 'en',
        translations: {'en': 'Test Profile'},
      ),
      maxExtensionItems: maxExtensionItems,
      layouts: layouts,
      visibleMetadata: visibleMetadata,
      targetBlockOrder: targetBlockOrder ?? TargetBlockType.values,
    );
  }

  Widget createTestWidget({
    required Widget child,
    List<dynamic> overrides = const [],
  }) {
    return ProviderScope(
      overrides: [
        workflowAvailableExtensionsProvider(
          'wf_test',
        ).overrideWith((ref) async => ['citation', 'justification']),
        ...overrides,
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
        home: Scaffold(body: SingleChildScrollView(child: child)),
      ),
    );
  }

  group('BlockCardRegistry Parity Tests', () {
    test('asserts all TargetBlockType members are mapped in the registry', () {
      expect(
        BlockCardRegistry.registeredTypes,
        containsAll(TargetBlockType.values),
      );
      expect(
        BlockCardRegistry.registeredTypes.length,
        equals(TargetBlockType.values.length),
      );
    });

    for (final type in TargetBlockType.values) {
      testWidgets('renders card for TargetBlockType.${type.name} cleanly', (
        tester,
      ) async {
        final profile = createTestProfile();

        await tester.pumpWidget(
          createTestWidget(
            child: Builder(
              builder: (context) {
                return BlockCardRegistry.getBlockCard(
                  type: type,
                  context: context,
                  profileId: 'prf_test',
                  payload: profile,
                  updatePayload: (_) {},
                  allowedBlockIds: {},
                  promptBlocksState: const AsyncData([]),
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(BaseBlockCard), findsOneWidget);
      });
    }
  });

  group('Universal Baseline Toggle Tests', () {
    testWidgets('toggling switch off removes block from targetBlockOrder', (
      tester,
    ) async {
      final profile = createTestProfile(
        targetBlockOrder: [TargetBlockType.metadataBlock],
      );
      OutputProfile? updatedProfile;

      await tester.pumpWidget(
        createTestWidget(
          child: Builder(
            builder: (context) {
              return MetadataBlockCard(
                payload: profile,
                updatePayload: (p) => updatedProfile = p,
              );
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      final switchFinder = find.byType(Switch);
      expect(switchFinder, findsOneWidget);

      await tester.tap(switchFinder);
      await tester.pumpAndSettle();

      expect(updatedProfile, isNotNull);
      expect(
        updatedProfile!.targetBlockOrder,
        isNot(contains(TargetBlockType.metadataBlock)),
      );
    });

    testWidgets('toggling switch on adds block to targetBlockOrder', (
      tester,
    ) async {
      final profile = createTestProfile(targetBlockOrder: []);
      OutputProfile? updatedProfile;

      await tester.pumpWidget(
        createTestWidget(
          child: Builder(
            builder: (context) {
              return SimpleToggleBlockCard(
                blockType: TargetBlockType.penaltiesBlock,
                title: 'Penalties',
                subtitle: 'Penalties deduction',
                icon: Icons.gavel,
                payload: profile,
                updatePayload: (p) => updatedProfile = p,
              );
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      final switchFinder = find.byType(Switch);
      expect(switchFinder, findsOneWidget);

      await tester.tap(switchFinder);
      await tester.pumpAndSettle();

      expect(updatedProfile, isNotNull);
      expect(
        updatedProfile!.targetBlockOrder,
        contains(TargetBlockType.penaltiesBlock),
      );
    });
  });

  group('XaiExtensionsBlockCard Clamping & Validation', () {
    testWidgets(
      'clamps slider to 20 without assertion error when maxExtensionItems is 50',
      (tester) async {
        final profile = createTestProfile(
          maxExtensionItems: 50,
          targetBlockOrder: [TargetBlockType.groupedExtensionsBlock],
        );

        await tester.pumpWidget(
          createTestWidget(
            child: Builder(
              builder: (context) {
                return XaiExtensionsBlockCard(
                  payload: profile,
                  updatePayload: (_) {},
                );
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        final sliderFinder = find.byType(Slider);
        expect(sliderFinder, findsOneWidget);
        final Slider slider = tester.widget(sliderFinder);
        expect(slider.value, equals(20.0));
      },
    );
  });

  group('MatrixGraphsBlockCard Collection Builder', () {
    testWidgets('adds new graph layout to payload.layouts on button tap', (
      tester,
    ) async {
      final profile = createTestProfile(
        targetBlockOrder: [TargetBlockType.matrixGraphsBlock],
        layouts: [],
      );
      OutputProfile? updatedProfile;

      await tester.pumpWidget(
        createTestWidget(
          child: Builder(
            builder: (context) {
              return MatrixGraphsBlockCard(
                payload: profile,
                updatePayload: (p) => updatedProfile = p,
                allowedBlockIds: {},
                promptBlocksState: const AsyncData([]),
              );
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      final addBtnFinder = find.text('Add Graph');
      expect(addBtnFinder, findsOneWidget);

      await tester.tap(addBtnFinder);
      await tester.pumpAndSettle();

      expect(updatedProfile, isNotNull);
      expect(updatedProfile!.layouts.length, equals(1));
      expect(
        updatedProfile!.layouts.first.presetView,
        equals(PresetView.metrics1d),
      );
    });
  });

  group('MatrixSummaryTableCard Configuration', () {
    testWidgets('toggles column visibility chip', (tester) async {
      final profile = createTestProfile(
        targetBlockOrder: [TargetBlockType.matrixSummaryTableBlock],
        layouts: [
          const OutputLayoutBlock(
            presetView: PresetView.matrixSummary,
            matrixVisibleColumns: ['label'],
          ),
        ],
      );
      OutputProfile? updatedProfile;

      await tester.pumpWidget(
        createTestWidget(
          child: Builder(
            builder: (context) {
              return MatrixSummaryTableCard(
                payload: profile,
                updatePayload: (p) => updatedProfile = p,
              );
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      final scoreChipFinder = find.widgetWithText(FilterChip, 'score');
      expect(scoreChipFinder, findsOneWidget);

      await tester.tap(scoreChipFinder);
      await tester.pumpAndSettle();

      expect(updatedProfile, isNotNull);
      final summaryLayout = updatedProfile!.layouts.firstWhere(
        (l) => l.presetView == PresetView.matrixSummary,
      );
      expect(summaryLayout.matrixVisibleColumns, contains('score'));
    });
  });
}
