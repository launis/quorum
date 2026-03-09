import 'package:client_app/core/api/studio_client.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late StudioClient client;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    client = StudioClient(mockDio);
  });

  group('StudioClient', () {
    test('getPromptBlocks calls correct endpoint and returns data', () async {
      // Arrange
      final mockData = [
        {'id': 'pb1', 'strictness_level': 50},
      ];
      when(() => mockDio.get('studio/prompt-blocks')).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: 'studio/prompt-blocks'),
          data: mockData,
          statusCode: 200,
        ),
      );

      // Act
      final result = await client.getPromptBlocks();

      // Assert
      expect(result, equals(mockData));
      verify(() => mockDio.get('studio/prompt-blocks')).called(1);
    });

    test('savePromptBlock calls correct endpoint and returns updated data', () async {
      // Arrange
      final requestData = {'strictness_level': 100};
      final returnedData = {'id': 'pb2', 'strictness_level': 100, 'version': 2};
      
      when(() => mockDio.put('studio/prompt-blocks/pb2', data: requestData)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: 'studio/prompt-blocks/pb2'),
          data: returnedData,
          statusCode: 200,
        ),
      );

      // Act
      final result = await client.savePromptBlock('pb2', requestData);

      // Assert
      expect(result, equals(returnedData));
      verify(() => mockDio.put('studio/prompt-blocks/pb2', data: requestData)).called(1);
    });
  });
}
