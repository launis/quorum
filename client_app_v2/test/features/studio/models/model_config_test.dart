import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/features/studio/models/model_config.dart';

void main() {
  group('Bug Hunt: ModelConfig slug parsing', () {
    test(
      'Fails correctly when slug is null (matching backend SystemConfigModelRegistry)',
      () {
        final payload = {
          'id': 'sys_1234567890abcdef',
          'type': 'model_registry',
          'slug': null,
          'models': <String, dynamic>{},
        };

        // This will throw CheckedFromJsonException because slug is null
        final config = ModelConfig.fromJson(payload);

        expect(config.id, 'sys_1234567890abcdef');
      },
    );
  });
}
