import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_general_tab.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockNullOutputProfileForm extends OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String id) {
    throw StateError(
      'Profile payload must not be null when rendering ProfileGeneralTab',
    );
  }
}

class MockWorkflowsController extends WorkflowsController {
  @override
  FutureOr<List<Workflow>> build() async {
    return [];
  }
}

class MockErrorWorkflowsController extends WorkflowsController {
  @override
  FutureOr<List<Workflow>> build() {
    throw StateError('Workflow repository unavailable');
  }
}

class TestValidOutputProfileForm extends OutputProfileForm {
  final OutputProfile _profile;
  OutputProfile? lastUpdatedPayload;
  TestValidOutputProfileForm(this._profile);

  @override
  FutureOr<OutputProfile> build(String id) => _profile;

  @override
  void updatePayload(OutputProfile updated) {
    lastUpdatedPayload = updated;
    state = AsyncData(updated);
  }
}

void main() {
  testWidgets(
    'ProfileGeneralTab throws StateError when payload is missing (Fail-Fast)',
    (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'test_id',
            ).overrideWith(() => MockNullOutputProfileForm()),
            workflowsControllerProvider.overrideWith(
              () => MockWorkflowsController(),
            ),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileGeneralTab(id: 'test_id')),
          ),
        ),
      );

      expect(tester.takeException(), isA<StateError>());
    },
  );

  testWidgets(
    'ProfileGeneralTab renders tone instruction and 4 matrix view type directives, and prunes 1:1 section directives',
    (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1920, 3000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final profile = OutputProfile(
        id: 'prf_test',
        workflowId: 'wf_test',
        slug: 'prf-test',
        name: const I18nText(translations: {'en': 'Test Profile'}),
        toneInstruction: 'Direct, candid, executive coaching tone',
        matrix1dSynthesisDirective: '1D metric directive',
        matrix2dSynthesisDirective: '2D comparison directive',
        matrix3dSynthesisDirective: '3D radar directive',
        matrixTextSynthesisDirective: 'Text narrative directive',
      );

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'prf_test',
            ).overrideWith(() => TestValidOutputProfileForm(profile)),
            workflowsControllerProvider.overrideWith(
              () => MockWorkflowsController(),
            ),
          ],
          child: const MaterialApp(
            locale: Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileGeneralTab(id: 'prf_test')),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Card 2: Tone instruction TextFormField
      expect(
        find.byKey(const Key('profile_tone_instruction_field')),
        findsOneWidget,
      );

      await tester.drag(find.byType(ListView), const Offset(0, -600));
      await tester.pumpAndSettle();

      // Card 3: Matrix View Directives title
      expect(
        find.text('Matrix View Type Synthesis Directives'),
        findsOneWidget,
      );

      // Card 3: 4 Reusable View Type TextFormFields
      expect(
        find.byKey(const Key('profile_matrix_1d_directive_field')),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('profile_matrix_2d_directive_field')),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('profile_matrix_3d_directive_field')),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('profile_matrix_text_directive_field')),
        findsOneWidget,
      );

      // Invariant: Pruned 1:1 Section Directives must NOT exist on Tab 1
      expect(find.text('Executive summary synthesis directive'), findsNothing);
      expect(find.text('Row explanation synthesis directive'), findsNothing);
      expect(find.text('XAI highlights synthesis directive'), findsNothing);
      expect(
        find.text('Variance validation synthesis directive'),
        findsNothing,
      );
    },
  );

  testWidgets(
    'ProfileGeneralTab renders localized workflow error state and normalizes whitespace-only directives to null',
    (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1920, 3000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      final profile = OutputProfile(
        id: 'prf_boundary',
        workflowId: 'wf_dangling',
        slug: 'prf-boundary',
        name: const I18nText(translations: {'en': 'Boundary Profile'}),
        toneInstruction: 'Initial tone',
        matrix1dSynthesisDirective: 'Initial 1D',
      );
      final formNotifier = TestValidOutputProfileForm(profile);

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'prf_boundary',
            ).overrideWith(() => formNotifier),
            workflowsControllerProvider.overrideWith(
              () => MockErrorWorkflowsController(),
            ),
          ],
          child: const MaterialApp(
            locale: Locale('en'),
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileGeneralTab(id: 'prf_boundary')),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Negative check: Workflows AsyncError displays localized error text
      expect(
        find.textContaining('Workflow repository unavailable'),
        findsOneWidget,
      );

      // Boundary check: Whitespace-only input in toneInstruction and 1D directive normalizes to null
      await tester.enterText(
        find.byKey(const Key('profile_tone_instruction_field')),
        '   ',
      );
      await tester.pump();
      expect(formNotifier.lastUpdatedPayload?.toneInstruction, isNull);

      await tester.enterText(
        find.byKey(const Key('profile_matrix_1d_directive_field')),
        '   ',
      );
      await tester.pump();
      expect(
        formNotifier.lastUpdatedPayload?.matrix1dSynthesisDirective,
        isNull,
      );
    },
  );
}
