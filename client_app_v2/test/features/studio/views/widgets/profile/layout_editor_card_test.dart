import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/layout_editor_card.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'LayoutEditorCard should not crash when rendering matrixSummary PresetView',
    (WidgetTester tester) async {
      // Arrange
      final layout = OutputLayoutBlock(
        presetView: PresetView.matrixSummary,
        title: I18nText(defaultLocale: 'en'),
        textDeliveryMode: TextDeliveryMode.full,
        targetBlocks: [],
      );

      // Act & Assert
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: LayoutEditorCard(
                layouts: [layout],
                onChanged: (_) {},
                allowedBlockIds: {},
                promptBlocksState: const AsyncValue.data([]),
              ),
            ),
          ),
        ),
      );

      // If we reach here without crashing, the test passes.
      expect(find.byType(LayoutEditorCard), findsOneWidget);
    },
  );
}
