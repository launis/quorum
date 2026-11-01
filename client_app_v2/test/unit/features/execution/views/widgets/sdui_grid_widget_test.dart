import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/features/execution/views/widgets/sdui_grid_widget.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  Widget buildTestApp(SduiGridBlock block, {ThemeData? theme}) {
    return MaterialApp(
      theme:
          theme ??
          ThemeData.light().copyWith(
            extensions: const <ThemeExtension<dynamic>>[
              AppSemanticColors.light,
            ],
          ),
      home: Scaffold(body: SduiGridWidget(block: block)),
    );
  }

  group('SduiGridWidget — Positive Rendering & Theme Sovereignty', () {
    testWidgets(
      'renders even number of grid items in two-column Expanded Row layout with theme tokens',
      (tester) async {
        const block = SduiGridBlock(
          id: 'blk_01965b30000070008000000000000010',
          items: <SduiBlockDTO>[
            SduiParagraphBlock(text: 'First grid cell narrative'),
            SduiAlertBoxBlock(
              text: 'Second grid cell alert',
              severity: AlertSeverity.success,
            ),
            SduiMarkdownBlock(text: 'Third grid cell markdown'),
            SduiParagraphBlock(text: 'Fourth grid cell narrative'),
          ],
        );

        final customTheme = ThemeData.light().copyWith(
          extensions: const <ThemeExtension<dynamic>>[AppSemanticColors.light],
        );

        await tester.pumpWidget(buildTestApp(block, theme: customTheme));

        expect(find.byType(Card), findsNWidgets(4));
        expect(find.byType(SduiBlocksRenderer), findsNWidgets(4));
        expect(find.byType(OutputRenderer), findsNWidgets(4));
        expect(find.text('First grid cell narrative'), findsOneWidget);
        expect(find.text('Second grid cell alert'), findsOneWidget);
        expect(find.text('Third grid cell markdown'), findsOneWidget);
        expect(find.text('Fourth grid cell narrative'), findsOneWidget);

        final card = tester.widget<Card>(find.byType(Card).first);
        expect(card.elevation, 0);
        expect(card.margin, EdgeInsets.zero);
        expect(
          card.color,
          customTheme.colorScheme.surfaceContainerHighest.withValues(
            alpha: 0.5,
          ),
        );
        final shape = card.shape as RoundedRectangleBorder;
        expect(shape.borderRadius, BorderRadius.circular(AppSpacing.s8));
      },
    );

    testWidgets(
      'renders odd number of grid items with trailing Expanded placeholder cleanly',
      (tester) async {
        const block = SduiGridBlock(
          id: 'blk_01965b30000070008000000000000011',
          items: <SduiBlockDTO>[
            SduiParagraphBlock(text: 'Cell 1'),
            SduiParagraphBlock(text: 'Cell 2'),
            SduiParagraphBlock(text: 'Cell 3 Odd Trailing'),
          ],
        );

        await tester.pumpWidget(buildTestApp(block));

        expect(find.byType(Card), findsNWidgets(3));
        expect(find.text('Cell 1'), findsOneWidget);
        expect(find.text('Cell 2'), findsOneWidget);
        expect(find.text('Cell 3 Odd Trailing'), findsOneWidget);
      },
    );
  });

  group('SduiGridWidget — Negative & Boundary Value Analysis', () {
    testWidgets(
      'Boundary: empty items list returns empty SizedBox without rendering Cards',
      (tester) async {
        const emptyBlock = SduiGridBlock(items: <SduiBlockDTO>[]);

        await tester.pumpWidget(buildTestApp(emptyBlock));

        expect(tester.takeException(), isNull);
        expect(find.byType(Card), findsNothing);
        expect(find.byType(SduiBlocksRenderer), findsNothing);
      },
    );

    testWidgets(
      'Boundary: narrow width constraint contains long multi-word grid items via Expanded without RenderFlex overflow',
      (tester) async {
        final longTextA = List.filled(18, 'AlphaGridMetricToken').join(' ');
        final longTextB = List.filled(18, 'BetaGridMetricToken').join(' ');
        final block = SduiGridBlock(
          items: <SduiBlockDTO>[
            SduiParagraphBlock(text: longTextA),
            SduiParagraphBlock(text: longTextB),
          ],
        );

        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.light().copyWith(
              extensions: const <ThemeExtension<dynamic>>[
                AppSemanticColors.light,
              ],
            ),
            home: Scaffold(
              body: SingleChildScrollView(
                child: SizedBox(
                  width: 180,
                  child: SduiGridWidget(block: block),
                ),
              ),
            ),
          ),
        );

        expect(tester.takeException(), isNull);
        expect(find.byType(Card), findsNWidgets(2));
        expect(find.byType(Expanded), findsNWidgets(2));
      },
    );

    test(
      'Negative: SduiBlockDTO.fromJson rejects missing items, non-list items, and unrecognized keys on grid block (Fail-Fast)',
      () {
        expect(
          () => SduiBlockDTO.fromJson(const <String, Object?>{
            'block_type': 'grid',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => SduiBlockDTO.fromJson(const <String, Object?>{
            'block_type': 'grid',
            'items': 'invalid_non_list_payload',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => SduiBlockDTO.fromJson(const <String, Object?>{
            'block_type': 'grid',
            'items': <Object?>[],
            'rogue_unrecognized_field': true,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
