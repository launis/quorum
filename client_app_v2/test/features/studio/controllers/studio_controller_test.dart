import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

void main() {
  late MockStudioClient mockClient;
  late ProviderContainer container;

  setUp(() {
    mockClient = MockStudioClient();
    container = ProviderContainer(
      overrides: [
        studioClientProvider.overrideWithValue(mockClient),
      ],
    );
  });

  tearDown(() {
    container.dispose();
  });

  group('PromptBlocksController Exception Handling', () {
    test('deletePromptBlock throws AppError if DioException contains one (RFC 7807 Fail-Fast)', () async {
      // Arrange
      const id = 'pb1';
      final appError = const AppError.api(
        errorCode: 'RESOURCE_IN_USE',
        detail: 'Cannot delete block used by a blueprint',
        status: 400,
      );

      when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);

      when(() => mockClient.deletePromptBlock(id)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/studio/prompt-blocks/$id'),
          error: appError,
        ),
      );

      final controller = container.read(promptBlocksControllerProvider.notifier);

      // Act & Assert
      expect(
        () => controller.deletePromptBlock(id),
        throwsA(
          isA<ApiAppError>()
              .having((e) => e.errorCode, 'errorCode', 'RESOURCE_IN_USE')
              .having((e) => e.status, 'status', 400),
        ),
      );
      
      // Verify client was called
      verify(() => mockClient.deletePromptBlock(id)).called(1);
    });
  });
}
