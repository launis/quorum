import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for AuditApi
void main() {
  final instance = BackendApi().getAuditApi();

  group(AuditApi, () {
    // Get Audit Logs
    //
    // Retrieve audit logs.  Role Rules: - ROOT: Can see logs for ANY organization or system-wide (if org_id is None). - ADMIN: Can ONLY see logs for THEIR OWN organization. - MEMBER: Cannot see audit logs (403).
    //
    //Future<List<AuditEvent>> getAuditLogsAuditLogsGet({ String organizationId, String actorId, String action, int limit, String authorization }) async
    test('test getAuditLogsAuditLogsGet', () async {
      // TODO
    });
  });
}
