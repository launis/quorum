import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for UsageApi
void main() {
  final instance = BackendApi().getUsageApi();

  group(UsageApi, () {
    // Get Organization Usage
    //
    // Get usage statistics for a specific organization.
    //
    //Future<UsageReport> getOrganizationUsageV1UsageOrganizationOrgIdGet(String orgId, { String since, String authorization }) async
    test('test getOrganizationUsageV1UsageOrganizationOrgIdGet', () async {
      // TODO
    });

    // Get System Usage
    //
    // Get system-wide usage statistics (Root only).
    //
    //Future<UsageReport> getSystemUsageV1UsageSystemGet({ String since, String authorization }) async
    test('test getSystemUsageV1UsageSystemGet', () async {
      // TODO
    });

    // Get User Usage
    //
    // Get usage statistics for a specific user.
    //
    //Future<UsageReport> getUserUsageV1UsageUserUserIdGet(String userId, { String since, String authorization }) async
    test('test getUserUsageV1UsageUserUserIdGet', () async {
      // TODO
    });

  });
}
