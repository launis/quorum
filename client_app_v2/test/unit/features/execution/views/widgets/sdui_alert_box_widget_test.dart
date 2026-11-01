import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/views/widgets/sdui_alert_box_widget.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  Widget buildTestApp(SduiAlertBoxBlock block, {ThemeData? theme}) {
    return MaterialApp(
      theme:
          theme ??
          ThemeData.light().copyWith(
            extensions: const <ThemeExtension<dynamic>>[
              AppSemanticColors.light,
            ],
          ),
      home: Scaffold(body: SduiAlertBoxWidget(block: block)),
    );
  }

  group('SduiAlertBoxWidget — Positive Rendering & Theme Sovereignty', () {
    testWidgets(
      'renders success severity with check_circle_outline and semantic success color',
      (tester) async {
        const block = SduiAlertBoxBlock(
          id: 'blk_01965b30000070008000000000000001',
          text: 'All assertions verified.',
          severity: AlertSeverity.success,
        );

        await tester.pumpWidget(buildTestApp(block));

        final iconFinder = find.byIcon(Icons.check_circle_outline);
        expect(iconFinder, findsOneWidget);
        final icon = tester.widget<Icon>(iconFinder);
        expect(icon.color, AppSemanticColors.light.success);
        expect(icon.size, AppSpacing.s24);
        expect(find.byType(OutputRenderer), findsOneWidget);
        expect(find.text('All assertions verified.'), findsOneWidget);
      },
    );

    testWidgets(
      'renders warning, info, error, and criticalOverride severities',
      (tester) async {
        final cases = <(AlertSeverity, IconData)>[
          (AlertSeverity.warning, Icons.warning_amber_rounded),
          (AlertSeverity.info, Icons.info_outline),
          (AlertSeverity.error, Icons.error_outline),
          (AlertSeverity.criticalOverride, Icons.error_outline),
        ];

        for (final (severity, expectedIcon) in cases) {
          final block = SduiAlertBoxBlock(
            text: 'Severity check: ${severity.name}',
            severity: severity,
          );
          await tester.pumpWidget(buildTestApp(block));
          expect(find.byIcon(expectedIcon), findsOneWidget);
          expect(find.text('Severity check: ${severity.name}'), findsOneWidget);
        }
      },
    );
  });

  group('SduiAlertBoxWidget — Negative & Boundary Value Analysis', () {
    testWidgets(
      'Boundary: empty string and HTML <br> tags render cleanly without overflow',
      (tester) async {
        const emptyBlock = SduiAlertBoxBlock(
          text: '',
          severity: AlertSeverity.info,
        );
        await tester.pumpWidget(buildTestApp(emptyBlock));
        expect(tester.takeException(), isNull);
        expect(find.byType(OutputRenderer), findsOneWidget);

        const brBlock = SduiAlertBoxBlock(
          text: 'First line<br/>Second line<BR>Third line',
          severity: AlertSeverity.warning,
        );
        await tester.pumpWidget(buildTestApp(brBlock));
        expect(tester.takeException(), isNull);
        expect(find.text('First line Second line Third line'), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary: narrow width constraint contains long alert text via Expanded without RenderFlex overflow',
      (tester) async {
        final longText = List.filled(20, 'Verification Alert Token').join(' ');
        final block = SduiAlertBoxBlock(
          text: longText,
          severity: AlertSeverity.criticalOverride,
        );

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: SingleChildScrollView(
                child: SizedBox(
                  width: 180,
                  child: SduiAlertBoxWidget(block: block),
                ),
              ),
            ),
          ),
        );

        expect(tester.takeException(), isNull);
        expect(find.byType(Expanded), findsOneWidget);
      },
    );

    test(
      'Negative: SduiBlockDTO.fromJson rejects invalid severity and unrecognized keys (Fail-Fast)',
      () {
        expect(
          () => SduiBlockDTO.fromJson(<String, dynamic>{
            'block_type': 'alert_box',
            'text': 'Invalid severity payload',
            'severity': 'non_existent_severity',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );

        expect(
          () => SduiBlockDTO.fromJson(<String, dynamic>{
            'block_type': 'alert_box',
            'text': 'Rogue key payload',
            'severity': 'info',
            'rogue_unrecognized_field': true,
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
