import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/models/generic_status_response_dto.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/human_override_dialog.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockExecutionClient extends Mock implements ExecutionClient {}

class FakeHumanOverrideRequestDto extends Fake
    implements HumanOverrideRequestDto {}

void main() {
  setUpAll(() {
    registerFallbackValue(FakeHumanOverrideRequestDto());
  });

  Widget createTestWidget({
    required Widget child,
    List overrides = const [],
  }) {
    return ProviderScope(
      overrides: overrides.cast(),
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en')],
        home: Scaffold(body: child),
      ),
    );
  }

  ScorecardAtomDto createSampleAtom({
    String? reason,
    ExecutionStatus status = ExecutionStatus.passed,
    List<QuoteEvidenceDto> quotes = const [
      QuoteEvidenceDto(
        quote: 'Existing evidence quote',
        verifiedSourceIds: ['src_1'],
        isVerified: true,
      ),
    ],
  }) {
    return ScorecardAtomDto(
      atomId: 'atm_test_001',
      level: 1,
      levelName: 'Level 1',
      claimLabel: 'Sample Claim Label',
      extractedFacts: const {'fact': 'val'},
      exactQuotes: quotes,
      internalLogicEn: const ReasoningStepDto(
        step1IdentifyPremise: 'p1',
        step2ScanSource: 's1',
        step3EvaluateAntiPatterns: 'a1',
        step4FinalConclusion: 'c1',
      ),
      status: status,
      semanticReasoning: 'Initial automated reasoning',
      contextualOverride: false,
      chartDisplayLabel: 'Test Atom',
      visualIntent: VisualIntent.neutral,
      humanOverride: reason != null
          ? HumanOverrideDto(
              reason: reason,
              newStatus: status,
              overriddenAt: DateTime.parse('2026-09-22T00:00:00Z'),
              overriddenBy: 'reviewer@quorum.ai',
              evidenceQuotes: quotes,
            )
          : null,
    );
  }

  group('HumanOverrideDialog Tests', () {
    testWidgets(
      'test_human_override_dialog_dirty_state_shows_discard_prompt',
      (tester) async {
        final atom = createSampleAtom();
        final mockClient = MockExecutionClient();

        await tester.pumpWidget(
          createTestWidget(
            overrides: [executionClientProvider.overrideWithValue(mockClient)],
            child: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => HumanOverrideDialog(
                      atom: atom,
                      executionId: 'exec_test_001',
                    ),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();

        // 1. Modify reason text field
        final reasonField = find.widgetWithText(
          TextFormField,
          'Reason for override',
        );
        expect(reasonField, findsOneWidget);
        await tester.enterText(reasonField, 'A completely new modified reason');
        await tester.pumpAndSettle();

        // 2. Click Cancel button to trigger dismissal
        final cancelBtn = find.widgetWithText(TextButton, 'Cancel');
        await tester.tap(cancelBtn);
        await tester.pumpAndSettle();

        // 3. Verify discard confirmation dialog appears
        expect(find.text('Discard changes?'), findsOneWidget);
        expect(
          find.text('There are unsaved changes. Do you want to discard them?'),
          findsOneWidget,
        );

        // 4. Select "Continue Editing" -> confirmation pops, dialog stays open
        final continueBtn = find.widgetWithText(TextButton, 'Continue Editing');
        await tester.tap(continueBtn);
        await tester.pumpAndSettle();

        expect(find.text('Discard changes?'), findsNothing);
        expect(find.text('Override Decision (EU AI Act)'), findsOneWidget);

        // 5. Tap Cancel again, then select "Discard Changes" -> dialog closes completely
        await tester.tap(cancelBtn);
        await tester.pumpAndSettle();

        expect(find.text('Discard changes?'), findsOneWidget);
        final discardBtn = find.widgetWithText(FilledButton, 'Discard Changes');
        await tester.tap(discardBtn);
        await tester.pumpAndSettle();

        expect(find.text('Override Decision (EU AI Act)'), findsNothing);
      },
    );

    testWidgets(
      'test_human_override_dialog_pristine_state_pops_immediately',
      (tester) async {
        final atom = createSampleAtom();
        final mockClient = MockExecutionClient();

        await tester.pumpWidget(
          createTestWidget(
            overrides: [executionClientProvider.overrideWithValue(mockClient)],
            child: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => HumanOverrideDialog(
                      atom: atom,
                      executionId: 'exec_test_001',
                    ),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();

        expect(find.text('Override Decision (EU AI Act)'), findsOneWidget);

        // Tap cancel in pristine state
        final cancelBtn = find.widgetWithText(TextButton, 'Cancel');
        await tester.tap(cancelBtn);
        await tester.pumpAndSettle();

        // Must pop immediately without discard prompt
        expect(find.text('Discard changes?'), findsNothing);
        expect(find.text('Override Decision (EU AI Act)'), findsNothing);
      },
    );

    testWidgets(
      'test_human_override_dialog_empty_reason_shows_inline_error',
      (tester) async {
        final atom = createSampleAtom();
        final mockClient = MockExecutionClient();

        await tester.pumpWidget(
          createTestWidget(
            overrides: [executionClientProvider.overrideWithValue(mockClient)],
            child: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => HumanOverrideDialog(
                      atom: atom,
                      executionId: 'exec_test_001',
                    ),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();

        // Save with empty reason
        final saveBtn = find.widgetWithText(ElevatedButton, 'Save Override');
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        // Verify inline validation error and zero SnackBars
        expect(find.text('Reason is required.'), findsOneWidget);
        expect(find.byType(SnackBar), findsNothing);

        // Verify overrideAtom was never called
        verifyNever(
          () => mockClient.overrideAtom(
            executionId: any(named: 'executionId'),
            atomId: any(named: 'atomId'),
            payload: any(named: 'payload'),
          ),
        );
      },
    );

    testWidgets(
      'test_human_override_dialog_rating_change_marks_dirty',
      (tester) async {
        final atom = createSampleAtom();
        final mockClient = MockExecutionClient();

        await tester.pumpWidget(
          createTestWidget(
            overrides: [executionClientProvider.overrideWithValue(mockClient)],
            child: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => HumanOverrideDialog(
                      atom: atom,
                      executionId: 'exec_test_001',
                    ),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();

        // Change rating dropdown from PASSED to FAILED
        final dropdown = find.byType(DropdownButtonFormField<ExecutionStatus>);
        expect(dropdown, findsOneWidget);
        await tester.tap(dropdown);
        await tester.pumpAndSettle();

        final failedItem = find.text('FAILED').last;
        await tester.tap(failedItem);
        await tester.pumpAndSettle();

        // Tap cancel
        final cancelBtn = find.widgetWithText(TextButton, 'Cancel');
        await tester.tap(cancelBtn);
        await tester.pumpAndSettle();

        // Verify discard dialog triggered
        expect(find.text('Discard changes?'), findsOneWidget);
      },
    );

    testWidgets(
      'test_human_override_dialog_quotes_mutation_marks_dirty',
      (tester) async {
        final atom = createSampleAtom();
        final mockClient = MockExecutionClient();

        await tester.pumpWidget(
          createTestWidget(
            overrides: [executionClientProvider.overrideWithValue(mockClient)],
            child: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => HumanOverrideDialog(
                      atom: atom,
                      executionId: 'exec_test_001',
                    ),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();

        // Delete the existing quote
        final deleteQuoteBtn = find.byIcon(Icons.delete);
        expect(deleteQuoteBtn, findsOneWidget);
        await tester.tap(deleteQuoteBtn);
        await tester.pumpAndSettle();

        // Tap cancel
        final cancelBtn = find.widgetWithText(TextButton, 'Cancel');
        await tester.tap(cancelBtn);
        await tester.pumpAndSettle();

        // Verify discard dialog triggered
        expect(find.text('Discard changes?'), findsOneWidget);
      },
    );

    testWidgets(
      'test_human_override_dialog_in_flight_lock',
      (tester) async {
        final atom = createSampleAtom();
        final mockClient = MockExecutionClient();
        final completer = Completer<GenericStatusResponseDto>();

        when(
          () => mockClient.overrideAtom(
            executionId: any(named: 'executionId'),
            atomId: any(named: 'atomId'),
            payload: any(named: 'payload'),
          ),
        ).thenAnswer((_) => completer.future);

        bool? dialogResult;

        await tester.pumpWidget(
          createTestWidget(
            overrides: [executionClientProvider.overrideWithValue(mockClient)],
            child: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () async {
                  dialogResult = await showDialog<bool>(
                    context: context,
                    builder: (_) => HumanOverrideDialog(
                      atom: atom,
                      executionId: 'exec_test_001',
                    ),
                  );
                },
                child: const Text('Open Dialog'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Dialog'));
        await tester.pumpAndSettle();

        // Enter valid justification
        final reasonField = find.widgetWithText(
          TextFormField,
          'Reason for override',
        );
        await tester.enterText(
          reasonField,
          'Valid expert rationale for manual override.',
        );
        await tester.pumpAndSettle();

        // Tap Save
        final saveBtn = find.widgetWithText(ElevatedButton, 'Save Override');
        await tester.tap(saveBtn);
        await tester.pump(); // Start in-flight request

        // Verify progress indicator is rendered and cancel button is disabled
        expect(find.byType(CircularProgressIndicator), findsOneWidget);
        final inFlightCancelBtn = tester.widget<TextButton>(
          find.widgetWithText(TextButton, 'Cancel'),
        );
        expect(inFlightCancelBtn.onPressed, isNull);

        // Complete the network call
        completer.complete(
          const GenericStatusResponseDto(
            status: 'ok',
            message: 'Override applied',
          ),
        );
        await tester.pumpAndSettle();

        // Verify client was called with correct typed payload
        verify(
          () => mockClient.overrideAtom(
            executionId: 'exec_test_001',
            atomId: 'atm_test_001',
            payload: any(
              named: 'payload',
              that: isA<HumanOverrideRequestDto>().having(
                (p) => p.reason,
                'reason',
                'Valid expert rationale for manual override.',
              ),
            ),
          ),
        ).called(1);

        // Verify dialog popped with true
        expect(find.text('Override Decision (EU AI Act)'), findsNothing);
        expect(dialogResult, isTrue);
      },
    );
  });
}
