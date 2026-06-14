import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_widget.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'ReportRendererWidget renders 1D metrics statically without dynamic factory overhead',
    (WidgetTester tester) async {
      final dto = const ReportDataDTO(
        workflowId: 'wf_test',
        profileId: 'default',
        profileName: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Default Profile'},
        ),
        availableProfiles: {
          'default': I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Default Profile'},
          ),
        },
        layouts: [
          ReportLayoutDTO(
            presetView: PresetView.metrics1d,
            title: null,
            description: null,
            textDeliveryMode: 'full',
            axes: [
              MatrixScorecardRowDto(
                blockId: 'mock',
                labelI18n: const I18nText(
                  translations: {'fi': 'Mock Axis', 'en': 'Mock Axis'},
                ),
                name: 'Mock Axis',
                score: 100.0,
                rowExplanation: 'Perfect',
                scaleMin: 0.0,
                scaleMax: 6.0,
              ),
            ],
          ),
        ],
      );

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: ReportRendererWidget(
                payload: dto,
                executionId: 'test_exec_id',
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Mock Axis'), findsOneWidget);
      expect(find.text('Perfect'), findsOneWidget);
      expect(
        find.text('100.0 / 6.0'),
        findsOneWidget,
      ); // Raw score value is formatted this way
    },
  );

  testWidgets(
    'ReportRendererWidget renders text_only preset as 1D metrics without charts',
    (WidgetTester tester) async {
      final dto = const ReportDataDTO(
        workflowId: 'wf_test_2',
        profileId: 'default',
        profileName: I18nText(
          defaultLocale: 'en',
          translations: {'en': 'Default Profile'},
        ),
        availableProfiles: {
          'default': I18nText(
            defaultLocale: 'en',
            translations: {'en': 'Default Profile'},
          ),
        },
        layouts: [
          ReportLayoutDTO(
            presetView: PresetView.textOnly,
            title: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Text Layout Title'},
            ),
            description: I18nText(
              defaultLocale: 'en',
              translations: {'en': 'Text Layout Desc'},
            ),
            synthesisMd: 'Synthesis content',
            textDeliveryMode: 'full',
            axes: [
              MatrixScorecardRowDto(
                blockId: 'text_mock',
                labelI18n: const I18nText(
                  translations: {'fi': 'Text Axis', 'en': 'Text Axis'},
                ),
                name: 'Text Axis',
                score: 0.0,
                rowExplanation: 'This is a text only rowExplanation',
                scaleMin: 0.0,
                scaleMax: 6.0,
              ),
            ],
          ),
        ],
      );

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(
              body: ReportRendererWidget(
                payload: dto,
                executionId: 'test_exec_id',
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Text Layout Title'), findsOneWidget);
      expect(find.text('Text Layout Desc'), findsOneWidget);
      expect(find.textContaining('Synthesis content'), findsOneWidget);
      expect(find.text('Text Axis'), findsNothing);
      expect(find.text('This is a text only rowExplanation'), findsNothing);
    },
  );
}
