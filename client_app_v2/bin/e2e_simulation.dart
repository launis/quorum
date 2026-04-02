import 'dart:io';
import 'package:dio/dio.dart';

/// E2E Simulation Client for Quorum V2
/// Simulates a real Flutter execution flow to populate `client_debug.log`
/// and verify the Fail-Fast architecture end-to-end.
void main(List<String> args) async {
  // 1. Initialize Logging matching LoggerService format
  final logFile = File('c:\\src\\quorum\\client_debug.log');

  void logInfo(String context, String message) {
    final time = DateTime.now().toString().substring(0, 19);
    final logLine = '$time | INFO | [$context] | client | $message\n';
    logFile.writeAsStringSync(logLine, mode: FileMode.append);
    print(logLine.trim());
  }

  void logError(String context, String message, [dynamic error]) {
    final time = DateTime.now().toString().substring(0, 19);
    final logLine = '$time | ERROR | [$context] | client | $message\n';
    logFile.writeAsStringSync(logLine, mode: FileMode.append);
    if (error != null) {
      logFile.writeAsStringSync('ERROR: $error\n', mode: FileMode.append);
    }
    print(logLine.trim());
  }

  logInfo('SYSTEM', 'E2E Simulation Started');

  // 2. Setup Dio
  final dio = Dio(
    BaseOptions(
      baseUrl: 'http://localhost:8000/api/v2',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 10),
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization':
            'Bearer mock-token:usr_18a0d5f6151349a5',
      },
    ),
  );

  // 3. Execution Data (Using the trace from Epic 16)
  final workflowId =
      'wf_d653170e174847559e08af42b938d826'; // Default Kokonaisvaltainen Auditointierates new ID usually, but we need to trigger an execution. We'll start a new one.

  final rawInputs = {
    "organization_name": "Test Org",
    "industry": "Technology",
    "target_audience": "Developers",
  };

  logInfo('EXECUTION', 'Triggering execution for workflow: \$workflowId');

  try {
    // 4. API Call
    final response = await dio.post(
      '/execution/executions/',
      data: {
        'workflow_id': workflowId,
        'raw_inputs': rawInputs,
        'target_locale': 'fi',
      },
    );

    // 5. Parse using Isolate.run() simulation (fail-fast JSON parsing)
    final responseData = response.data as Map<String, dynamic>;
    logInfo(
      'NETWORK',
      "Received successful execution response: \${responseData['execution_id']}",
    );

    // Basic Fail-Fast validation of payload structure
    if (!responseData.containsKey('status')) {
      throw Exception('Missing status in response');
    }

    logInfo('SYSTEM', 'E2E Simulation Completed Successfully');
    exit(0);
  } on DioException catch (e) {
    logError(
      'NETWORK',
      'DioException during execution: \${e.message}',
      e.response?.data,
    );
    exit(1);
  } catch (e) {
    logError('SYSTEM', 'Unknown error during execution', e);
    exit(1);
  }
}
