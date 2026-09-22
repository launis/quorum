import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/workflow_builder_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockStudioClient mockClient;
  late MockLoggerService mockLogger;

  const testWfId = 'wor_01b1d71000000001';

  final testWorkflow = Workflow(
    id: testWfId,
    slug: 'test-workflow-slug',
    name: const I18nText(
      translations: {'en': 'Test Workflow', 'fi': 'Testityönkulku'},
    ),
    description: const I18nText(
      translations: {'en': 'Test Desc', 'fi': 'Testikuvaus'},
    ),
    modelRegistryId: 'mr_test',
    steps: const [],
    expectedInputs: const [],
  );

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    when(() => mockLogger.info(any(), any())).thenReturn(null);

    when(() => mockClient.getSteps()).thenAnswer((_) async => []);
    when(() => mockClient.getMcpGateways()).thenAnswer((_) async => []);
    when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
    when(() => mockClient.getOutputProfiles()).thenAnswer((_) async => []);
  });

  Widget createTestWidget({String id = testWfId}) {
    return ProviderScope(
      overrides: [
        studioClientProvider.overrideWithValue(mockClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('fi'),
        home: WorkflowBuilderView(id: id),
      ),
    );
  }

  group('WorkflowBuilderView Widget Tests', () {
    testWidgets(
      'renders ErrorView when studio client fails to load workflow (Negative Partition 1)',
      (tester) async {
        when(
          () => mockClient.getWorkflow(testWfId),
        ).thenThrow(Exception('Failed to load workflow form'));

        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
      },
    );

    testWidgets(
      'renders WorkflowBuilderView with 4 tabs when loaded successfully (Positive Partition)',
      (tester) async {
        when(
          () => mockClient.getWorkflow(testWfId),
        ).thenAnswer((_) async => testWorkflow);

        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Verify TabBar with 4 tabs exists
        expect(find.byType(TabBar), findsOneWidget);
        expect(find.text('1. Yleiset & Tulosteet'), findsOneWidget);
        expect(find.text('2. Syötteet'), findsOneWidget);
        expect(find.text('3. Stepit & Riippuvuudet'), findsOneWidget);
        expect(find.text('4. Arvioinnin ankaruus'), findsOneWidget);

        // Verify title in AppBar shows localized workflow name
        expect(
          find.descendant(
            of: find.byType(AppBar),
            matching: find.text('Testityönkulku'),
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'shows validation snackbar when saving with empty ID (Negative Partition 2)',
      (tester) async {
        final emptyIdWorkflow = testWorkflow.copyWith(id: '');

        when(
          () => mockClient.getWorkflow('new'),
        ).thenAnswer((_) async => emptyIdWorkflow);

        await tester.pumpWidget(createTestWidget(id: ''));
        await tester.pumpAndSettle();

        // Tap save button
        await tester.tap(find.byIcon(Icons.save));
        await tester.pumpAndSettle();

        // Expect ID required snackbar
        expect(find.text('ID on pakollinen.'), findsOneWidget);
      },
    );
  });
}
