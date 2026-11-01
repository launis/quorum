import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_v2_widget.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/theme/app_theme.dart';

void main() {
  const validExecutionId = 'exec_01960000000070008000000000000001';
  const validWorkflowId = 'wf_01960000000070008000000000000001';
  const validProfileId = 'prf_01960000000070008000000000000001';

  Widget buildTestHarness(
    ReportDataDto payload, {
    String executionId = validExecutionId,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
  }) {
    final child = ReportRendererV2Widget(
      payload: payload,
      executionId: executionId,
    );
    return MaterialApp(
      theme: theme ?? AppTheme.light,
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: width != null ? SizedBox(width: width, child: child) : child,
        ),
      ),
    );
  }

  group('ReportRendererV2Widget Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders inner SDUI blocks inside AppErrorBoundary and SduiBlocksRenderer without diagnostic error container',
      (WidgetTester tester) async {
        const payload = ReportDataDto(
          executionId: validExecutionId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          innerSduiBlocks: [
            SduiBlockDTO.heroInsight(
              text: 'Strategic synthesis verified across all dimensions.',
            ),
            SduiBlockDTO.scoreCard(globalScore: 91.25),
          ],
        );

        await tester.pumpWidget(buildTestHarness(payload));
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.byType(AppErrorBoundary), findsOneWidget);
        expect(find.byType(SduiBlocksRenderer), findsOneWidget);
        expect(
          find.text('Strategic synthesis verified across all dimensions.'),
          findsOneWidget,
        );
        expect(find.text('91.25/100'), findsOneWidget);
        expect(find.text(l10n.sharedNoReportData), findsNothing);
        expect(find.text(l10n.reportEmptyProfile), findsNothing);
      },
    );

    testWidgets(
      'Negative/Boundary 1: empty innerSduiBlocks renders localized errorContainer diagnostic card in dark mode without overflow on narrow 120px width',
      (WidgetTester tester) async {
        const emptyPayload = ReportDataDto(
          executionId: validExecutionId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          innerSduiBlocks: [],
        );

        await tester.pumpWidget(
          buildTestHarness(
            emptyPayload,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 120,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);

        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(find.text(l10nFi.sharedNoReportData), findsOneWidget);
        expect(find.text(l10nFi.reportEmptyProfile), findsOneWidget);
        expect(find.byIcon(Icons.error_outline), findsOneWidget);
        expect(find.byType(SduiBlocksRenderer), findsNothing);

        final icon = tester.widget<Icon>(find.byIcon(Icons.error_outline));
        expect(icon.color, equals(AppTheme.dark.colorScheme.onErrorContainer));

        final container = tester.widget<Container>(
          find.ancestor(
            of: find.byIcon(Icons.error_outline),
            matching: find.byType(Container),
          ),
        );
        final decoration = container.decoration as BoxDecoration;
        expect(
          decoration.color,
          equals(AppTheme.dark.colorScheme.errorContainer),
        );
        final border = decoration.border as Border;
        expect(border.left.color, equals(AppTheme.dark.colorScheme.error));
        expect(border.left.width, equals(AppSpacing.s4));
      },
    );

    testWidgets(
      'Negative/Boundary 2: malformed SDUI block with empty I18nText translations triggers Fail-Fast AppException caught by AppErrorBoundary',
      (WidgetTester tester) async {
        const invalidPayload = ReportDataDto(
          executionId: validExecutionId,
          workflowId: validWorkflowId,
          profileId: validProfileId,
          innerSduiBlocks: [
            SduiBlockDTO.metrics1d(
              title: I18nText(translations: {}),
              axes: [],
            ),
          ],
        );

        await tester.pumpWidget(buildTestHarness(invalidPayload));

        final exception = tester.takeException();
        expect(exception, isA<AppException>());

        await tester.pump();
        expect(find.byIcon(Icons.report_problem), findsOneWidget);
      },
    );
  });
}
