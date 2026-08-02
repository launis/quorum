import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_v2_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

// Phase 2: Flutter Semantic Extractor
void main() {
  testWidgets('SDUI Semantic Parity Extractor', (WidgetTester tester) async {
    const goldenPath = String.fromEnvironment('GOLDEN_PATH');
    const dumpPath = String.fromEnvironment('DUMP_PATH');

    if (goldenPath.isEmpty || dumpPath.isEmpty) {
      print('Skipping SDUI parity test: GOLDEN_PATH or DUMP_PATH missing.');
      return;
    }

    final goldenFile = File(goldenPath);
    if (!goldenFile.existsSync()) {
      throw Exception('Golden file not found at $goldenPath');
    }

    final jsonStr = goldenFile.readAsStringSync();
    final jsonMap = jsonDecode(jsonStr) as Map<String, dynamic>;
    final payload = ReportDataDto.fromJson(jsonMap);

    // CRITICAL: Call tester.ensureSemantics() before rendering
    final semanticsHandle = tester.ensureSemantics();

    tester.view.physicalSize = const Size(2400, 10000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() => tester.view.resetPhysicalSize());
    addTearDown(() => tester.view.resetDevicePixelRatio());

    await tester.pumpWidget(
      MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'), // We enforce English for the parity test
        home: Scaffold(
          body: ReportRendererV2Widget(
            payload: payload,
            executionId: 'parity_test_exec',
          ),
        ),
      ),
    );

    await tester.pumpAndSettle();

    final semanticNode = tester.getSemantics(
      find.byType(ReportRendererV2Widget),
    );

    final textSequence = <String>[];
    _extractSemantics(semanticNode, textSequence);

    final dumpFile = File(dumpPath);
    dumpFile.writeAsStringSync(jsonEncode(textSequence));
    print(
      'Successfully extracted ${textSequence.length} semantic tokens to $dumpPath',
    );
    semanticsHandle.dispose();
  });
}

void _extractSemantics(SemanticsNode node, List<String> textSequence) {
  final data = node.getSemanticsData();

  if (data.label.trim().isNotEmpty) {
    textSequence.add(data.label.trim());
  } else if (data.value.trim().isNotEmpty) {
    textSequence.add(data.value.trim());
  }

  node.visitChildren((SemanticsNode child) {
    _extractSemantics(child, textSequence);
    return true; // continue visiting
  });
}
