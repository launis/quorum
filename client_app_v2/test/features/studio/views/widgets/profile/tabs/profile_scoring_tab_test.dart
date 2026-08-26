import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class MockNullOutputProfileForm extends OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String id) {
    throw StateError(
      'Profile payload must not be null when rendering ProfileScoringTab',
    );
  }
}

class MockValidOutputProfileForm extends OutputProfileForm {
  final OutputProfile profile;
  MockValidOutputProfileForm(this.profile);

  @override
  FutureOr<OutputProfile> build(String id) {
    return profile;
  }
}

void main() {
  OutputProfile createTestProfile() {
    return const OutputProfile(
      id: 'prf_test',
      workflowId: 'wf_test',
      name: I18nText(translations: {'en': 'Test Profile'}),
      displayScale: DisplayScale.original,
      strictnessLevel: 50,
      scoringStrategy: ScoringStrategy.waterfall,
      visibleMetadata: ['date', 'organization'],
      visibleBlockExtensions: [XaiExtensionType.citation],
    );
  }

  group('ProfileScoringTab Tests', () {
    testWidgets(
      'test_scoring_tab_renders_display_scale_strictness_and_strategy',
      (WidgetTester tester) async {
        final profile = createTestProfile();

        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              outputProfileFormProvider(
                'prf_test',
              ).overrideWith(() => MockValidOutputProfileForm(profile)),
            ],
            child: const MaterialApp(
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(body: ProfileScoringTab(id: 'prf_test')),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(DropdownButton<DisplayScale>), findsOneWidget);
        expect(find.byType(DropdownButton<int>), findsOneWidget);
        expect(find.byType(DropdownButton<ScoringStrategy?>), findsOneWidget);
      },
    );

    testWidgets('test_scoring_tab_does_not_render_metadata_or_xai_checkboxes', (
      WidgetTester tester,
    ) async {
      final profile = createTestProfile();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'prf_test',
            ).overrideWith(() => MockValidOutputProfileForm(profile)),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileScoringTab(id: 'prf_test')),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Negative test: verify no CheckboxListTile or TextFormField on ProfileScoringTab
      expect(find.byType(CheckboxListTile), findsNothing);
      expect(find.byType(TextFormField), findsNothing);
    });

    testWidgets('test_scoring_tab_throws_state_error_when_payload_is_null', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            outputProfileFormProvider(
              'test_id',
            ).overrideWith(() => MockNullOutputProfileForm()),
          ],
          child: const MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Scaffold(body: ProfileScoringTab(id: 'test_id')),
          ),
        ),
      );

      expect(tester.takeException(), isA<StateError>());
    });
  });
}
