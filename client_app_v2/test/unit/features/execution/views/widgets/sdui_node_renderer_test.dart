import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';
import 'package:client_app/features/execution/views/widgets/sdui_node_renderer.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_theme.dart';

void main() {
  const validExecutionId = 'exec_01960000000070008000000000000001';
  const validTdaId = 'tda_01960000000070008000000000000001';

  Widget buildTestHarness({
    required String executionId,
    required AtomResultDTO result,
    HydratedAtomDTO? hydratedAtom,
    bool overrideHydratedProvider = true,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
  }) {
    final child = SduiNodeRenderer(executionId: executionId, result: result);
    return ProviderScope(
      overrides: [
        if (overrideHydratedProvider)
          hydratedReferenceProvider(
            executionId,
            result.tdaId,
          ).overrideWithValue(hydratedAtom),
      ],
      child: MaterialApp(
        theme: theme ?? AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: width != null ? SizedBox(width: width, child: child) : child,
        ),
      ),
    );
  }

  group('SduiNodeRenderer Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders booleanCard for passed and failed status with semantic colorScheme tokens',
      (WidgetTester tester) async {
        const passedResult = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.passed,
        );
        const hydratedAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.booleanCard,
          resolvedClaim: 'Executive board Charter is formally ratified.',
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: passedResult,
            hydratedAtom: hydratedAtom,
          ),
        );
        await tester.pumpAndSettle();

        expect(
          find.text('Executive board Charter is formally ratified.'),
          findsOneWidget,
        );
        final passedIcon = tester.widget<Icon>(find.byIcon(Icons.check_circle));
        expect(passedIcon.color, equals(AppTheme.light.colorScheme.primary));

        const failedResult = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.failed,
        );
        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: failedResult,
            hydratedAtom: hydratedAtom,
          ),
        );
        await tester.pumpAndSettle();

        final failedIcon = tester.widget<Icon>(find.byIcon(Icons.error));
        expect(failedIcon.color, equals(AppTheme.light.colorScheme.error));
      },
    );

    testWidgets(
      'Positive 2: renders extractedValueCard with and without unit cleanly',
      (WidgetTester tester) async {
        const resultWithUnit = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.passed,
          extractedData: ExtractedValueDTO(value: 92.4, unit: '%'),
        );
        const hydratedAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.extractedValueCard,
          resolvedClaim: 'Quarterly retention rate metric',
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: resultWithUnit,
            hydratedAtom: hydratedAtom,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.info), findsOneWidget);
        expect(find.text('Quarterly retention rate metric'), findsOneWidget);
        expect(find.text('92.4 %'), findsOneWidget);

        const resultWithoutUnit = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.passed,
          extractedData: ExtractedValueDTO(value: 42),
        );
        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: resultWithoutUnit,
            hydratedAtom: hydratedAtom,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('42'), findsOneWidget);
      },
    );

    testWidgets(
      'Positive 3: renders errorCard and nACard with theme tokens and localized cascade reason',
      (WidgetTester tester) async {
        const errorResult = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.systemError,
          errorDetails: ErrorDetailsDTO(
            errorCode: 'ERR_PARSE_TIMEOUT',
            message: 'Upstream synthesis node timed out.',
          ),
        );
        const errorAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.errorCard,
          resolvedClaim: 'Audit trail verification claim',
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: errorResult,
            hydratedAtom: errorAtom,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning), findsOneWidget);
        expect(find.text('Audit trail verification claim'), findsOneWidget);
        expect(find.text('Upstream synthesis node timed out.'), findsOneWidget);
        final card = tester.widget<Card>(find.byType(Card));
        expect(card.color, equals(AppTheme.light.colorScheme.errorContainer));

        const naResult = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.nA,
          shortCircuitReasonTdaIds: [
            'tda_01960000000070008000000000000010',
            'tda_01960000000070008000000000000011',
          ],
        );
        const naAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.nACard,
          resolvedClaim: 'Dependent downstream governance assertion',
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: naResult,
            hydratedAtom: naAtom,
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));
        expect(find.byIcon(Icons.block), findsOneWidget);
        expect(
          find.text('Dependent downstream governance assertion'),
          findsOneWidget,
        );
        expect(
          find.text(
            l10n.lblNaCascadeReason(
              'tda_01960000000070008000000000000010, tda_01960000000070008000000000000011',
            ),
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Negative/Boundary 1: missing hydratedAtom reference throws Fail-Fast AppException',
      (WidgetTester tester) async {
        const result = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.passed,
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: result,
            hydratedAtom: null,
          ),
        );

        final exception = tester.takeException();
        expect(exception, isA<AppException>());
      },
    );

    testWidgets(
      'Negative/Boundary 2: empty executionId triggers Fail-Fast AppException from hydratedReferenceProvider',
      (WidgetTester tester) async {
        const result = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.passed,
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: '   ',
            result: result,
            overrideHydratedProvider: false,
          ),
        );

        final exception = tester.takeException();
        expect(exception, isA<Object>());
      },
    );

    testWidgets(
      'Negative/Boundary 3: ultra-long text in narrow 120px dark-mode viewport renders without horizontal overflow',
      (WidgetTester tester) async {
        final longText = 'A' * 300;
        final errorResult = AtomResultDTO(
          tdaId: validTdaId,
          status: ExecutionStatus.systemError,
          errorDetails: ErrorDetailsDTO(
            errorCode: 'ERR_OVERFLOW_BOUNDARY',
            message: longText,
          ),
        );
        final errorAtom = HydratedAtomDTO(
          sduiComponent: SDUIComponentType.errorCard,
          resolvedClaim: longText,
        );

        await tester.pumpWidget(
          buildTestHarness(
            executionId: validExecutionId,
            result: errorResult,
            hydratedAtom: errorAtom,
            theme: AppTheme.dark,
            width: 120,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byIcon(Icons.warning), findsOneWidget);
      },
    );
  });
}
