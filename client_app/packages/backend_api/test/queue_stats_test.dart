import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

// tests for QueueStats
void main() {
  final QueueStats? instance = /* QueueStats(...) */ null;
  // TODO add properties to the entity

  group(QueueStats, () {
    // Number of jobs currently waiting in the queue.
    // int queuedJobs
    test('to test the property `queuedJobs`', () async {
      // TODO
    });

    // Number of jobs currently being processed.
    // int activeJobs
    test('to test the property `activeJobs`', () async {
      // TODO
    });

    // Number of jobs in the dead letter queue (failed).
    // int deadJobs
    test('to test the property `deadJobs`', () async {
      // TODO
    });
  });
}
