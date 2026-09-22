import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/profile_editor_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';

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
    outputProfiles: {
      'profile_main': const OutputProfile(
        id: 'profile_main',
        workflowId: testWfId,
        name: I18nText(
          translations: {
            'en': 'Main Profile',
            'fi': 'Pääprofiili',
          },
        ),
        visibleBlockExtensions: [],
        visibleWorkflowExtensions: [],
        matrixSynthesisGroups: [],
      ),
    },
  );

  setUp(() {
    mockClient = MockStudioClient();
    mockLogger = MockLoggerService();

    when(() => mockLogger.error(any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any())).thenReturn(null);
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
    when(() => mockLogger.info(any(), any())).thenReturn(null);

    when(() => mockClient.getSteps()).thenAnswer((_) async => []);
    when(() => mockClient.getPromptBlocks()).thenAnswer((_) async => []);
    when(() => mockClient.getSystemConfigs()).thenAnswer((_) async => []);
  });

  Widget createTestWidget({String workflowId = testWfId}) {
    return ProviderScope(
      overrides: [
        studioClientProvider.overrideWithValue(mockClient),
        loggerServiceProvider.overrideWithValue(mockLogger),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: const Locale('en'),
        home: ProfileEditorView(workflowId: workflowId),
      ),
    );
  }

  group('ProfileEditorView Desktop Tests', () {
    testWidgets(
      'renders ErrorView when studio client fails to load workflow (Negative Partition 1)',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        when(
          () => mockClient.getWorkflow(testWfId),
        ).thenThrow(Exception('Backend network failure'));

        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
      },
    );

    testWidgets(
      'renders ProfileEditorView with centered 1200px max width and profile card (Positive Partition)',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        when(
          () => mockClient.getWorkflow(testWfId),
        ).thenAnswer((_) async => testWorkflow);

        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // ConstrainedBox with maxWidth 1200 must exist
        final constrainedBoxes = tester.widgetList<ConstrainedBox>(
          find.byType(ConstrainedBox),
        );
        final has1200Box = constrainedBoxes.any(
          (box) => box.constraints.maxWidth == 1200,
        );
        expect(has1200Box, isTrue);

        // Header and Add Variant button must be present
        expect(find.text('Output Profiles Dictionary'), findsOneWidget);
        expect(find.text('Add Variant'), findsOneWidget);

        // Profile card with tabs exists
        expect(find.text('Variant ID: profile_main'), findsOneWidget);
        expect(find.text('General'), findsOneWidget);
        expect(find.text('Extensions (XAI)'), findsOneWidget);
        expect(find.text('Layouts'), findsOneWidget);
      },
    );

    testWidgets(
      'tapping Add Variant opens dialog to create a new profile (Positive Action)',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        when(
          () => mockClient.getWorkflow(testWfId),
        ).thenAnswer((_) async => testWorkflow);

        await tester.pumpWidget(createTestWidget());
        await tester.pumpAndSettle();

        // Tap Add Variant button
        final addBtn = find.widgetWithText(FilledButton, 'Add Variant');
        await tester.tap(addBtn);
        await tester.pumpAndSettle();

        expect(find.byType(AlertDialog), findsOneWidget);
        expect(find.text('New Profile ID'), findsOneWidget);

        // Tap Cancel closes dialog
        await tester.tap(find.text('Cancel'));
        await tester.pumpAndSettle();

        expect(find.byType(AlertDialog), findsNothing);
      },
    );

    testWidgets(
      'shows validation snackbar when workflow ID is empty during save (Negative Partition 2)',
      (tester) async {
        tester.view.physicalSize = const Size(1920, 1080);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final emptyIdWorkflow = testWorkflow.copyWith(id: '');

        when(
          () => mockClient.getWorkflow('new'),
        ).thenAnswer((_) async => emptyIdWorkflow);

        await tester.pumpWidget(createTestWidget(workflowId: 'new'));
        await tester.pumpAndSettle();

        // Tap Save button using Icon finder
        final saveBtn = find.byIcon(Icons.save);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        // SnackBar error appears
        expect(find.byType(SnackBar), findsOneWidget);
        expect(find.textContaining('Workflow ID is missing'), findsOneWidget);
      },
    );
  });
}
