import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_widget.dart';

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
        synthesis: 'Good',
      );

      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: ReportRendererWidget(payload: dto))),
      );

      expect(find.text('Mock Axis'), findsOneWidget);
      expect(find.text('Perfect'), findsOneWidget);
      expect(find.text('100.0'), findsOneWidget); // Raw score value
    },
  );
}
