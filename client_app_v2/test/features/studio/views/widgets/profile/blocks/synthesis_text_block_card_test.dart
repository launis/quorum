import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/synthesis_text_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets('SynthesisTextBlockCard renders fields and updates payload', (
    WidgetTester tester,
  ) async {
    OutputProfile payload = const OutputProfile(
      id: 'profile_1',
      workflowId: 'wf_1',
      name: I18nText(
        defaultLocale: 'en',
        translations: {'en': 'Default Profile'},
      ),
      targetBlockOrder: [TargetBlockType.synthesisTextBlock],
      synthesis: SynthesisConfigDTO(synthesisBlockId: 'block_1'),
    );

    final mockPromptBlock = const PromptBlock.systemRule(
      id: 'block_1',
      slug: 'exec_summary',
      label: I18nText(
        defaultLocale: 'en',
        translations: {'en': 'Executive Summary'},
      ),
      description: I18nText(
        defaultLocale: 'en',
        translations: {'en': 'Exec summary block'},
      ),
    );

    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: SynthesisTextBlockCard(
              payload: payload,
              updatePayload: (newPayload) {
                payload = newPayload;
              },
              promptBlocksState: AsyncValue.data([mockPromptBlock]),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Synthesis & Narrative Text'), findsOneWidget);
    expect(find.byType(DropdownButtonFormField<String?>), findsOneWidget);
  });
}
