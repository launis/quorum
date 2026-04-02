// E2E Client Simulation Test
// Matches Epic 16.5 real-world usage architecture.
import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:logger/logger.dart' hide FileOutput;

// Import LoggerService to populate client_debug.log natively.
import 'package:client_app/core/logging/logger_service.dart';

void main() {
  test('E2E Real LLM Simulation runs ExecutionClient and logs activity', () async {
    // 1. Initialize custom Logger directly bound to client_debug.log
    // We bypass the global LoggerService init to force the path safely in the test env.

    // 1.1 Read environment paths usually available in Python orchestrator
    final workspaceRoot = File('../client_debug.log').existsSync()
        ? '..'
        : '../..'; // Fallback depending on where flutter test runs from

    final logFile = File('$workspaceRoot/client_debug.log');
    final outTraceFile = File(
      '$workspaceRoot/backend_v2/tests/test_data/e2e_new_trace.json',
    );
    final inTraceFile = File(
      '$workspaceRoot/backend_v2/tests/test_data/exe_c0bc_inputs.json',
    );

    // Overriding Logger Output for the test to ensure it hits the mandated log file
    final logger = Logger(
      filter: ProductionFilter(),
      printer: CustomPrinter(),
      output: FileOutput(logFile),
    );

    logger.i('[E2E_CLIENT] | client | Starting E2E Client Simulation Test.');

    try {
      if (!inTraceFile.existsSync()) {
        logger.w('[E2E_CLIENT] | client | Inputs file not found. Skipping.');
        return;
      }

      final rawInputsStr = await inTraceFile.readAsString();
      final rawInputs = jsonDecode(rawInputsStr) as Map<String, dynamic>;

      // 2. Setup Dio pointing to local Python backend
      final dio = Dio(
        BaseOptions(
          baseUrl: 'http://127.0.0.1:8000/api/v2',
          connectTimeout: const Duration(seconds: 5),
          sendTimeout: const Duration(minutes: 5),
          receiveTimeout: const Duration(minutes: 5),
          headers: {
            'Authorization':
                'Bearer mock-token:usr_18a0d5f6151349a5',
          },
        ),
      );

      logger.i(
        '[E2E_CLIENT] | client | Sending execution request to backend...',
      );

      // 3. Trigger execution using the exact same structure as ExecutionClient
      final String workflowId =
          Platform.environment['TEST_WORKFLOW_ID'] ??
          'wf_d653170e174847559e08af42b938d826';
      final response = await dio.post(
        '/execution/executions/',
        data: {
          'workflow_id': workflowId,
          'raw_inputs': rawInputs,
          'target_locale': 'fi',
        },
      );

      logger.i(
        '[E2E_CLIENT] | client | Received response from backend: ${response.statusCode}',
      );

      // 4. Save trace for Python deep_logic_compare
      final responseData = response.data;
      if (responseData is Map<String, dynamic> &&
          responseData.containsKey('execution_trace')) {
        await outTraceFile.writeAsString(
          jsonEncode(responseData['execution_trace']),
        );
        logger.i(
          '[E2E_CLIENT] | client | Trace written successfully to test_data.',
        );
      } else {
        logger.e('[E2E_CLIENT] | client | Invalid response structure.');
        fail('Response did not contain execution_trace');
      }
    } catch (e, stack) {
      logger.e(
        '[E2E_CLIENT] | client | E2E Test execution failed',
        error: e,
        stackTrace: stack,
      );
      rethrow;
    }
  });
}
