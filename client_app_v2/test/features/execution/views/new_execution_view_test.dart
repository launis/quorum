import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:mocktail/mocktail.dart';

class MockStudioClient extends Mock implements StudioClient {}

void main() {
  late MockStudioClient mockStudioClient;

  setUp(() {
    mockStudioClient = MockStudioClient();
  });

  Widget createTestWidget({
    required MockStudioClient studioClient,
    Size screenSize = const Size(1920, 1080),
  }) {
    return ProviderScope(
      overrides: [studioClientProvider.overrideWithValue(studioClient)],
      child: MaterialApp(
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [Locale('en'), Locale('fi')],
        home: MediaQuery(
          data: MediaQueryData(size: screenSize),
          child: const NewExecutionView(),
        ),
      ),
    );
  }

  Workflow createWorkflow({
    required String id,
    required String name,
    List<ExpectedInput> expectedInputs = const [],
  }) {
    return Workflow(
      id: id,
      slug: 'slug_$id',
      name: I18nText(translations: {'en': name, 'fi': name}),
      description: I18nText(
        translations: {'en': 'Desc $name', 'fi': 'Kuvaus $name'},
      ),
      modelRegistryId: 'reg_default',
      expectedInputs: expectedInputs,
      outputProfiles: const {},
    );
  }

  group('NewExecutionView Widget Tests', () {
    testWidgets('renders empty workflows placeholder when no workflows exist', (
      tester,
    ) async {
      when(() => mockStudioClient.getWorkflows()).thenAnswer((_) async => []);

      await tester.pumpWidget(createTestWidget(studioClient: mockStudioClient));
      await tester.pumpAndSettle();

      expect(find.text('No workflows available for your account.'), findsOneWidget);
      expect(
        find.text('Select a workflow from the list to begin.'),
        findsOneWidget,
      );
    });

    testWidgets('renders ErrorView when availableWorkflowsProvider fails', (
      tester,
    ) async {
      final testError = AppException.validation('Failed to fetch workflows');
      when(() => mockStudioClient.getWorkflows()).thenThrow(testError);

      await tester.pumpWidget(createTestWidget(studioClient: mockStudioClient));
      await tester.pumpAndSettle();

      expect(find.byType(ErrorView), findsOneWidget);
    });

    testWidgets(
      'renders workflow inputs and validates required field on submit',
      (tester) async {
        final requiredInput = ExpectedInput(
          inputKey: 'consultant_brief',
          label: const I18nText(
            translations: {
              'en': 'Consultant Brief',
              'fi': 'Valmennustiivistelmä',
            },
          ),
          description: const I18nText(
            translations: {'en': 'Detailed brief', 'fi': 'Tarkka tiivistelmä'},
          ),
          required: true,
          inputModes: const ['text'],
        );

        final wf = createWorkflow(
          id: 'wor_coaching_123',
          name: 'Executive Coaching',
          expectedInputs: [requiredInput],
        );

        when(
          () => mockStudioClient.getWorkflows(),
        ).thenAnswer((_) async => [wf]);

        await tester.pumpWidget(
          createTestWidget(studioClient: mockStudioClient),
        );
        await tester.pumpAndSettle();

        expect(find.text('Executive Coaching'), findsOneWidget);

        // Select workflow
        await tester.tap(find.text('Executive Coaching'));
        await tester.pumpAndSettle();

        expect(
          find.text('Configure Inputs for Executive Coaching'),
          findsOneWidget,
        );
        expect(find.byType(TextField), findsOneWidget);

        // Click submit without entering text -> SnackBar validation failure
        await tester.tap(find.byType(FilledButton));
        await tester.pumpAndSettle();

        expect(find.byType(SnackBar), findsOneWidget);
        expect(
          find.text('Please fill in required inputs.'),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'renders instant submit button when workflow requires zero inputs',
      (tester) async {
        final wf = createWorkflow(
          id: 'wor_zero_input',
          name: 'Automated Benchmark',
          expectedInputs: const [],
        );

        when(
          () => mockStudioClient.getWorkflows(),
        ).thenAnswer((_) async => [wf]);

        await tester.pumpWidget(
          createTestWidget(studioClient: mockStudioClient),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Automated Benchmark'));
        await tester.pumpAndSettle();

        expect(
          find.text('No inputs strictly required for \nwor_zero_input'),
          findsOneWidget,
        );
        expect(find.byType(FilledButton), findsOneWidget);
      },
    );

    testWidgets(
      'renders localized expected input label and description instead of raw slug',
      (tester) async {
        final chatInput = ExpectedInput(
          inputKey: 'chat_log',
          label: const I18nText(
            translations: {
              'en': 'Conversation History (Chat)',
              'fi': 'Keskusteluhistoria (Chat)',
            },
          ),
          description: const I18nText(
            translations: {
              'en': 'Attach complete conversation',
              'fi': 'Tuo täysi keskustelu',
            },
          ),
          required: true,
          inputModes: const ['file', 'paste'],
        );
        final productInput = ExpectedInput(
          inputKey: 'product_text',
          label: const I18nText(
            translations: {
              'en': 'Product Deliverable',
              'fi': 'Lopputuote',
            },
          ),
          description: const I18nText(
            translations: {
              'en': 'Attach resulting deliverable',
              'fi': 'Liitä syntynyt lopputuotos',
            },
          ),
          required: true,
          inputModes: const ['file', 'paste'],
        );

        final wf = createWorkflow(
          id: 'wor_ai_driver',
          name: 'AI Driving License',
          expectedInputs: [chatInput, productInput],
        );

        when(
          () => mockStudioClient.getWorkflows(),
        ).thenAnswer((_) async => [wf]);

        await tester.pumpWidget(
          createTestWidget(studioClient: mockStudioClient),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('AI Driving License'));
        await tester.pumpAndSettle();

        // Must display human-readable localized labels
        expect(find.text('Conversation History (Chat) *'), findsOneWidget);
        expect(find.text('Product Deliverable *'), findsOneWidget);
        expect(find.text('Attach complete conversation'), findsOneWidget);
        expect(find.text('Attach resulting deliverable'), findsOneWidget);

        // Must NOT display raw unlocalized slugs as field titles
        expect(find.text('Input: chat_log'), findsNothing);
        expect(find.text('Input: product_text'), findsNothing);
      },
    );
  });
}
