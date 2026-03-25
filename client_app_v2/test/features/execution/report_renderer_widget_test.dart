import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  testWidgets(
    'ReportRendererWidget renders 1D metrics statically without dynamic factory overhead',
    (WidgetTester tester) async {
      final dto = const ReportDataDTO(
        workflowId: 'wf_test',
        profileId: 'default',
        profileName: {'en': 'Default Profile'},
        availableProfiles: {'default': 'Default Profile'},
        layouts: [
          ReportLayoutDTO(
            presetView: '1d_metrics',
            title: {},
            description: {},
            showText: true,
            axes: [
              ReportAxisDTO(
                name: 'Mock Axis',
                score: 100.0,
                justification: 'Perfect',
                scaleMin: 0.0,
                scaleMax: 6.0,
                scaleLabels: {},
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
            home: Scaffold(body: ReportRendererWidget(payload: dto)),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('Mock Axis'), findsOneWidget);
      expect(find.text('Perfect'), findsOneWidget);
      expect(find.text('100.0 / 6.0'), findsOneWidget); // Raw score value is formatted this way
    },
  );
}
