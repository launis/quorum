import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/features/studio/views/matrices_master_view.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockPromptBlocksController extends PromptBlocksController {
  final List<PromptBlock> blocks;
  MockPromptBlocksController([this.blocks = const []]);

  @override
  FutureOr<List<PromptBlock>> build() async {
    return blocks;
  }
}

void main() {
  Widget createTestWidget(
    List<PromptBlock> blocks, {
    Size screenSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      overrides: [
        promptBlocksControllerProvider.overrideWith(
          () => MockPromptBlocksController(blocks),
        ),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        home: MediaQuery(
          data: MediaQueryData(size: screenSize),
          child: const Scaffold(body: MatricesMasterView()),
        ),
      ),
    );
  }

  PromptBlock createMatrixBlock(String id, String name, String slug) {
    return PromptBlock.matrix(
      id: id,
      slug: slug,
      label: I18nText(translations: {'en': name, 'fi': name}),
      description: const I18nText(translations: {'en': 'Desc'}),
      scales: const [],
    );
  }

  group('MatricesMasterView Widget Tests', () {
    testWidgets(
      'test_matrices_master_view_instant_search_filtering',
      (tester) async {
        final mockBlocks = [
          createMatrixBlock('blk_empathy', 'Empathy Matrix', 'empathy-matrix'),
          createMatrixBlock('blk_clarity', 'Clarity Matrix', 'clarity-matrix'),
        ];

        await tester.pumpWidget(createTestWidget(mockBlocks));
        await tester.pumpAndSettle();

        expect(find.text('Empathy Matrix'), findsOneWidget);
        expect(find.text('Clarity Matrix'), findsOneWidget);
        expect(find.text('Showing 2 of 2 items'), findsOneWidget);

        // Search for 'clarity'
        await tester.enterText(find.byType(TextField), 'clarity');
        await tester.pumpAndSettle();

        expect(find.text('Empathy Matrix'), findsNothing);
        expect(find.text('Clarity Matrix'), findsOneWidget);
        expect(find.text('Showing 1 of 2 items'), findsOneWidget);

        // Clear search
        await tester.tap(find.byIcon(Icons.clear));
        await tester.pumpAndSettle();

        expect(find.text('Empathy Matrix'), findsOneWidget);
        expect(find.text('Clarity Matrix'), findsOneWidget);
        expect(find.text('Showing 2 of 2 items'), findsOneWidget);
      },
    );

    testWidgets(
      'test_master_views_4k_display_containment',
      (tester) async {
        tester.view.physicalSize = const Size(3840, 2160);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        final mockBlocks = [
          createMatrixBlock('blk_1', 'Matrix 1', 'matrix-1'),
        ];

        await tester.pumpWidget(
          createTestWidget(
            mockBlocks,
            screenSize: const Size(3840, 2160),
          ),
        );
        await tester.pumpAndSettle();

        final constrainedBoxFinder = find.byWidgetPredicate(
          (widget) =>
              widget is ConstrainedBox &&
              widget.constraints.maxWidth == 1200.0,
        );
        expect(constrainedBoxFinder, findsOneWidget);

        final box = tester.renderObject(constrainedBoxFinder) as RenderBox;
        expect(box.size.width, lessThanOrEqualTo(1200.0));
      },
    );

    testWidgets(
      'test_matrices_master_view_virtualized_rendering',
      (tester) async {
        final mockBlocks = List.generate(
          40,
          (i) => createMatrixBlock('blk_$i', 'Matrix $i', 'matrix-slug-$i'),
        );

        await tester.pumpWidget(createTestWidget(mockBlocks));
        await tester.pumpAndSettle();

        final listViewFinder = find.byType(ListView);
        expect(listViewFinder, findsOneWidget);

        final listView = tester.widget<ListView>(listViewFinder);
        expect(listView.prototypeItem, isNotNull);

        final visibleTiles = find.byType(ListTile);
        expect(visibleTiles.evaluate().length, lessThan(40));
        expect(visibleTiles.evaluate().length, greaterThan(0));

        expect(find.text('Showing 40 of 40 items'), findsOneWidget);
      },
    );

    testWidgets('excludes non-matrix category blocks', (tester) async {
      final mockBlocks = [
        createMatrixBlock('blk_matrix', 'Active Matrix', 'matrix-slug'),
        const PromptBlock.executionPersona(
          id: 'blk_persona',
          slug: 'persona-slug',
          label: I18nText(translations: {'en': 'Executive Coach Persona'}),
          description: I18nText(translations: {'en': 'Persona Desc'}),
        ),
      ];

      await tester.pumpWidget(createTestWidget(mockBlocks));
      await tester.pumpAndSettle();

      expect(find.text('Active Matrix'), findsOneWidget);
      expect(find.text('Executive Coach Persona'), findsNothing);
      expect(find.text('Showing 1 of 1 items'), findsOneWidget);
    });

    testWidgets('renders zero-state when no matrices available', (
      tester,
    ) async {
      await tester.pumpWidget(createTestWidget([]));
      await tester.pumpAndSettle();

      expect(find.text('No Matrices Available.'), findsOneWidget);
      expect(find.text('Showing 0 of 0 items'), findsOneWidget);
    });

    testWidgets('renders search miss when query yields 0 results', (
      tester,
    ) async {
      final mockBlocks = [
        createMatrixBlock('blk_1', 'Cognitive Bias', 'cognitive-bias'),
      ];

      await tester.pumpWidget(createTestWidget(mockBlocks));
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextField), 'UnknownQuery');
      await tester.pumpAndSettle();

      expect(find.text('No matching items found.'), findsOneWidget);
      expect(find.text('Showing 0 of 1 items'), findsOneWidget);
    });
  });
}
