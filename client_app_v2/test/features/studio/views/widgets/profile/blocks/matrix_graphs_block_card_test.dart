import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/matrix_graphs_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets('MatrixGraphsBlockCard renders graph collection and handles add button', (
    WidgetTester tester,
  ) async {
    OutputProfile payload = const OutputProfile(
      id: 'profile_1',
      workflowId: 'wf_1',
      name: I18nText(defaultLocale: 'en', translations: {'en': 'Test Profile'}),
      targetBlockOrder: [TargetBlockType.matrixGraphsBlock],
      layouts: [],
    );

    final mockPromptBlock = PromptBlock(
      id: 'block_1',
      slug: 'matrix_block_1',
      label: const I18nText(defaultLocale: 'en', translations: {'en': 'Matrix Block 1'}),
      description: const I18nText(defaultLocale: 'en', translations: {'en': 'Matrix block description'}),
      categoryId: 'matrix',
    );

    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: MatrixGraphsBlockCard(
              payload: payload,
              updatePayload: (newPayload) {
                payload = newPayload;
              },
              allowedBlockIds: {'block_1'},
              promptBlocksState: AsyncValue.data([mockPromptBlock]),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(MatrixGraphsBlockCard), findsOneWidget);
    expect(find.byType(FilledButton), findsOneWidget);

    await tester.tap(find.byType(FilledButton));
    await tester.pumpAndSettle();

    expect(payload.layouts.length, equals(1));
    expect(payload.layouts.first.presetView, equals(PresetView.metrics1d));
  });
}
