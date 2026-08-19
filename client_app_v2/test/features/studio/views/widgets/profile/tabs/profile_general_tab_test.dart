import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_general_tab.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockNullOutputProfileForm extends OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String id) {
    throw StateError('Profile payload must not be null when rendering ProfileGeneralTab');
  }
}

class MockWorkflowsController extends WorkflowsController {
  @override
  FutureOr<List<Workflow>> build() async {
    return [];
  }
}

void main() {
  testWidgets('ProfileGeneralTab throws StateError when payload is missing (Fail-Fast)', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          outputProfileFormProvider('test_id').overrideWith(
            () => MockNullOutputProfileForm(),
          ),
          workflowsControllerProvider.overrideWith(
            () => MockWorkflowsController(),
          ),
        ],
        child: const MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(
            body: ProfileGeneralTab(id: 'test_id'),
          ),
        ),
      ),
    );

    expect(tester.takeException(), isA<StateError>());
  });
}
