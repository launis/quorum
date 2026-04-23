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
    print(logLine.trim());
    if (error != null) {
      logFile.writeAsStringSync('ERROR: $error\n', mode: FileMode.append);
      print('ERROR DETAILS: $error');
    }
  }

  logInfo('SYSTEM', 'E2E Simulation Started');

  // 2. Setup Dio
  final dio = Dio(
    BaseOptions(
      baseUrl: 'http://127.0.0.1:8000/api/v2',
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-token:usr_a3fd6b3d77c748f4',
      },
    ),
  );

  // 3. Execution Data (Fetch dynamically)
  String workflowId = '';
  String profileId = '';

  final wRes = await dio.get('/studio/workflows/');
  if (wRes.data is List && wRes.data.isNotEmpty) {
    workflowId = wRes.data[0]['id'];
    profileId = wRes.data[0]['default_profile_id'];
  } else {
    print('Failed to fetch workflow dynamically. Response data: ${wRes.data}');
    throw Exception(
      'Failed to fetch workflow dynamically: data is empty or not a list.',
    );
  }

  final rawInputs = {
    "product_text": "Sample product text for E2E",
    "chat_log": "Sample chat log data",
    "reflection_text": "Sample reflection",
  };

  logInfo('EXECUTION', 'Triggering execution for workflow: $workflowId');

  try {
    // 4. API Call
    final response = await dio.post(
      '/execution/executions/',
      data: {
        'workflow_id': workflowId,
        'profile_id': profileId,
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
      'DioException during execution: ${e.message}',
      e.response?.data,
    );
    exit(1);
  } catch (e) {
    logError('SYSTEM', 'Unknown error during execution', e);
    exit(1);
  }
}
