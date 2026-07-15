import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/atom_result_dto.dart';
import 'package:client_app/features/execution/models/hydrated_atom_dto.dart';
import 'package:client_app/features/execution/views/widgets/sdui_node_renderer.dart';
import 'package:client_app/features/execution/providers/hydrated_reference_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  testWidgets('SduiNodeRenderer renders NACard correctly with grey theme and short circuit reasons', (WidgetTester tester) async {
    const executionId = 'test_execution';
    const tdaId = 'tda_123';

    // Mock AtomResultDTO
    const result = AtomResultDTO(
      tdaId: tdaId,
      status: ExecutionStatus.nA,
      shortCircuitReasonTdaIds: ['reason_1', 'reason_2'],
    );

    // Mock HydratedAtomDTO for nACard
    const hydratedAtom = HydratedAtomDTO(
      sduiComponent: SDUIComponentType.nACard,
      resolvedClaim: 'This step was skipped because of previous failures.',
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          hydratedReferenceProvider(executionId, tdaId).overrideWithValue(hydratedAtom),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'),
          home: Scaffold(
            body: SduiNodeRenderer(
              executionId: executionId,
              result: result,
            ),
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    // Verify it renders the claim in italic
    final claimFinder = find.text('This step was skipped because of previous failures.');
    expect(claimFinder, findsOneWidget);
    
    final textWidget = tester.widget<Text>(claimFinder);
    expect(textWidget.style?.fontStyle, FontStyle.italic);

    // Verify it renders the short circuit reasons text
    expect(find.text('N/A Cascade Reason: reason_1, reason_2'), findsOneWidget);

    // Verify the block icon is present
    expect(find.byIcon(Icons.block), findsOneWidget);
  });
}
