import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

// tests for UsageReport
void main() {
  final UsageReport? instance = /* UsageReport(...) */ null;
  // TODO add properties to the entity

  group(UsageReport, () {
    // Scope of the report (system, organization, user).
    // String scope
    test('to test the property `scope`', () async {
      // TODO
    });

    // String entityId
    test('to test the property `entityId`', () async {
      // TODO
    });

    // Reporting period (e.g., '2026-02', 'all-time').
    // String period
    test('to test the property `period`', () async {
      // TODO
    });

    // Aggregated token and cost statistics.
    // TokenUsage usage
    test('to test the property `usage`', () async {
      // TODO
    });

    // num quotaLimitUsd
    test('to test the property `quotaLimitUsd`', () async {
      // TODO
    });

    // num percentageUsed
    test('to test the property `percentageUsed`', () async {
      // TODO
    });

  });
}
