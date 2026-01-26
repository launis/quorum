import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/file_upload_field.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// Mock Mocktail class
class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  const channel = MethodChannel('miguelruivo.flutter.plugins.filepicker');

  setUpAll(() {
    registerFallbackValue(FormData.fromMap({}));
    registerFallbackValue(Options());
  });

  setUp(() {
    mockDio = MockDio();
    
    // Mock FilePicker channel
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(
      channel,
      (MethodCall methodCall) async {
        if (methodCall.method == 'pickFiles') {
          return {
             'count': 1,
             'files': [
               {
                 'name': 'test_file.txt',
                 'path': '/tmp/test_file.txt',
                 'bytes': [0, 1, 2, 3], 
                 'size': 4,
               }
             ]
          };
        }
        return null;
      },
    );
  });

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(channel, null);
  });

  testWidgets('renders correctly and shows upload button', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(mockDio),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: FileUploadField(
              label: 'Upload',
              onChanged: (_) {},
            ),
          ),
        ),
      ),
    );

    expect(find.text('Upload'), findsOneWidget);
    expect(find.text('Select file...'), findsOneWidget); // FileUploader default
  });

  // NOTE: Testing full interaction requires dealing with the async gap of FilePicker and Dio.
  // We verified logic manually. This test ensures basic rendering works. If we want to test upload:
  
  testWidgets('uploads file and returns ID', (tester) async {
    // Setup Mock Response
    when(() => mockDio.post(any(), data: any(named: 'data'))).thenAnswer(
      (_) async => Response(
        requestOptions: RequestOptions(path: '/v1/config/knowledge/upload'),
        data: {'id': '12345', 'url': 'http://foo.bar'},
        statusCode: 200,
      ),
    );

    String? uploadedId;

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(mockDio),
        ],
        child: MaterialApp(
          home: Scaffold(
            body: FileUploadField(
              label: 'Upload',
              onChanged: (val) => uploadedId = val,
            ),
          ),
        ),
      ),
    );

    // Tap select (wraps InkWell)
    await tester.tap(find.text('Select file...'));
    await tester.pump(); // Start picker
    
    // Wait for async operations (Picker -> Upload)
    await tester.pump(const Duration(milliseconds: 100)); // Picking
    await tester.pump(const Duration(milliseconds: 100)); // Uploading start

    // Should show loading?
    // expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle(); // Finish upload

    // ID should be set
    expect(uploadedId, '12345');
    // UI should show ID or filename
    expect(find.text('test_file.txt'), findsOneWidget);
  });
}
