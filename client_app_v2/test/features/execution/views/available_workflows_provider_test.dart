import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';

class MockStudioClient extends Mock implements StudioClient {}

void main() {
  group('availableWorkflowsProvider Contract Tests', () {
    test('test_available_workflows_provider_typed_resolution', () async {
      final mockStudioClient = MockStudioClient();
      final workflow = Workflow(
        id: 'wor_1234567812345678',
        slug: 'test_wf',
        name: const I18nText(translations: {'en': 'Test Workflow'}),
        description: const I18nText(translations: {'en': 'Desc'}),
        modelRegistryId: 'reg_default',
        outputProfiles: const {},
      );

      when(
        () => mockStudioClient.getWorkflows(),
      ).thenAnswer((_) async => [workflow]);

      final container = ProviderContainer(
        overrides: [studioClientProvider.overrideWithValue(mockStudioClient)],
      );
      addTearDown(container.dispose);

      final result = await container.read(availableWorkflowsProvider.future);

      expect(result, isA<List<Workflow>>());
      expect(result.length, 1);
      expect(result.first.id, 'wor_1234567812345678');
      expect(result.first.name.translations['en'], 'Test Workflow');
      verify(() => mockStudioClient.getWorkflows()).called(1);
    });
  });
}
