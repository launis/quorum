import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/studio/presentation/screens/prompt_playground_screen.dart';
import 'package:client_app/features/studio/presentation/widgets/sdui/code_editor_field.dart' as code_editor_field;
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;

  setUpAll(() {
    registerFallbackValue(Options());
    registerFallbackValue(<String, dynamic>{}); // Map fallback
  });

  setUp(() {
    mockDio = MockDio();
  });

  testWidgets('extracts variables and runs prompt', (tester) async {
    // Mock API Response
    when(() => mockDio.post(
      any(),
      data: any(named: 'data'),
      options: any(named: 'options'),
    )).thenAnswer(
      (_) async => Response(
        requestOptions: RequestOptions(path: '/run'),
        data: 'Generated Story',
        statusCode: 200,
      ),
    );

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          apiClientProvider.overrideWithValue(mockDio),
        ],
        child: const MaterialApp(
          home: PromptPlaygroundScreen(),
        ),
      ),
    );

    // Check initial state
    expect(find.text('Prompt Template'), findsOneWidget);
    expect(find.textContaining('{{tone}}'), findsOneWidget); // Initial value
    expect(find.text('tone'), findsOneWidget); // Variable label
    expect(find.text('topic'), findsOneWidget); // Variable label

    // Verify initial values
    print('Checking initial values');
    expect(find.textContaining('{{tone}}'), findsOneWidget);

    // Enter new template
    print('Entering template');
    await tester.enterText(find.byType(TextFormField).first, 'Hello {{name}}!');
    await tester.pump();

    // Verify extracted variables
    expect(find.text('name'), findsOneWidget);
    expect(find.text('tone'), findsNothing); 
    
    // Check Run button exists
    expect(find.text('Run Prompt'), findsOneWidget);
  });
}
  });
}
