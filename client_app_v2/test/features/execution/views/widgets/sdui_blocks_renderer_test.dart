import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/core/error/app_exception.dart';

void main() {
  group('SduiBlocksRenderer tests', () {
    testWidgets('throws AppException on unsupported block type', (
      tester,
    ) async {
      final block = SduiNACardBlock(
        message: 'Test',
        shortCircuitReasonTdaIds: const [],
      );

      final widget = SduiBlocksRenderer(blocks: [block]);

      await tester.pumpWidget(MaterialApp(home: Scaffold(body: widget)));

      final exception = tester.takeException();
      expect(exception, isNotNull);
      expect(exception, isA<AppException>());
    });
  });
}
