import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/blocks/xai_extensions_block_card.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets('XaiExtensionsBlockCard renders slider and extension chips', (
    WidgetTester tester,
  ) async {
    OutputProfile payload = const OutputProfile(
      id: 'profile_1',
      workflowId: 'wf_1',
      name: I18nText(defaultLocale: 'en', translations: {'en': 'Test Profile'}),
      targetBlockOrder: [TargetBlockType.groupedExtensionsBlock],
      visibleBlockExtensions: [XaiExtensionType.citation],
      maxExtensionItems: 3,
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          workflowAvailableExtensionsProvider('wf_1').overrideWithValue(
            const AsyncValue.data(['citation', 'justification', 'falsification']),
          ),
        ],
        child: MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: SingleChildScrollView(
              child: XaiExtensionsBlockCard(
                payload: payload,
                updatePayload: (newPayload) {
                  payload = newPayload;
                },
              ),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(XaiExtensionsBlockCard), findsOneWidget);
    expect(find.byType(Slider), findsOneWidget);
    expect(find.byType(FilterChip), findsWidgets);
  });
}
