import 'package:client_app/features/dashboard/presentation/widgets/execution_grid_item.dart';
import 'package:client_app/features/orchestration/domain/models/execution.dart';
import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

// Mocks
class MockExecutionController extends Mock implements ExecutionController {}

void main() {
  late MockExecutionController mockController;

  setUp(() {
    mockController = MockExecutionController();
    // Stub Riverpod internals if accessed (though usually overrideWith bypasses some)
    when(() => mockController.build()).thenAnswer((_) => null);
    // when(() => mockController.state).thenReturn(const AsyncData(null)); // Notifier state is protected/internal usually? 
    // Actually, we can't easily mock 'state' property of a Notifier as it's not virtual? 
    // But Mocktail mocks class members. Notifier.state is a getter/setter.
    // If we cannot mock it easily, we rely on overrideWith return value.
    
    // Default stub for cancelExecution
    when(() => mockController.cancelExecution(any())).thenAnswer((_) async {});
  });

  Widget createWidgetUnderTest(Execution execution) {
    return ProviderScope(
      overrides: [
        executionControllerProvider.overrideWith(() => mockController),
      ],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en')],
        home: Scaffold(
          body: ExecutionGridItem(execution: execution),
        ),
      ),
    );
  }

  testWidgets('Cancel button is visible when status is running', (tester) async {
    final execution = Execution.running(
      id: 'exec-1',
      createdAt: DateTime.now(),
      status: ExecutionStatus.running,
      inputs: {},
    );

    await tester.pumpWidget(createWidgetUnderTest(execution));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.cancel), findsOneWidget);
  });

  testWidgets('Cancel button is visible when status is pending', (tester) async {
    final execution = Execution.pending(
      id: 'exec-2',
      createdAt: DateTime.now(),
      status: ExecutionStatus.pending,
      inputs: {},
    );

    await tester.pumpWidget(createWidgetUnderTest(execution));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.cancel), findsOneWidget);
  });

  testWidgets('Cancel button is NOT visible when status is completed', (tester) async {
    final execution = Execution.completed(
      id: 'exec-3',
      createdAt: DateTime.now(),
      status: ExecutionStatus.completed,
      inputs: {},
    );

    await tester.pumpWidget(createWidgetUnderTest(execution));
    await tester.pumpAndSettle();

    expect(find.byIcon(Icons.cancel), findsNothing);
  });

  testWidgets('Tapping Cancel button calls controller.cancelExecution', (tester) async {
    final execution = Execution.running(
      id: 'exec-cancel',
      createdAt: DateTime.now(),
      status: ExecutionStatus.running,
      inputs: {},
    );

    await tester.pumpWidget(createWidgetUnderTest(execution));
    await tester.pumpAndSettle();

    final cancelButton = find.byIcon(Icons.cancel);
    await tester.tap(cancelButton);
    await tester.pump(); // Handle tap

    verify(() => mockController.cancelExecution('exec-cancel')).called(1);
  });
}
