import 'package:client_app/features/orchestration/domain/models/execution_input.dart';
import 'package:client_app/features/orchestration/domain/models/execution_file.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ExecutionInput Model', () {
    test('should serialize correctly excluding files', () {
      final input = ExecutionInput(
        workflowId: 'wf-1',
        inputs: {'text': 'hello'},
        files: {'doc': ExecutionFile(path: '/tmp/doc.pdf', name: 'doc.pdf')},
      );

      final json = input.toJson();

      expect(json['workflow_id'], 'wf-1');
      expect(json['inputs'], {'text': 'hello'});
      // 'files' should NOT be in the JSON output per @JsonKey(includeToJson: false)
      expect(json.containsKey('files'), false);
    });
  });
}
