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
  OutputProfile createTestProfile({int strictnessLevel = 50}) {
    return OutputProfile(
      id: 'prf_test',
      workflowId: 'wf_test',
      name: const I18nText(translations: {'en': 'Test Profile'}),
      displayScale: DisplayScale.original,
      strictnessLevel: strictnessLevel,
      visibleMetadata: const ['date', 'organization'],
      visibleBlockExtensions: const [XaiExtensionType.citation],
    );
  }

  Widget buildTestApp(OutputProfile profile) {
    return ProviderScope(
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
    );
  }

  group('ProfileScoringTab Tests', () {
    testWidgets(
      'test_scoring_tab_renders_display_scale_and_strictness_slider',
      (WidgetTester tester) async {
        final profile = createTestProfile(strictnessLevel: 50);

        await tester.pumpWidget(buildTestApp(profile));
        await tester.pumpAndSettle();

        expect(find.byType(DropdownButton<DisplayScale>), findsOneWidget);
        expect(find.byType(DropdownButton<int>), findsNothing);
        expect(find.byType(Slider), findsOneWidget);
        expect(find.byType(ChoiceChip), findsNWidgets(4));
        expect(find.text('50%'), findsOneWidget); // Pill badge
      },
    );

    testWidgets(
      'test_scoring_tab_tapping_preset_chips_updates_strictness',
      (WidgetTester tester) async {
        final profile = createTestProfile(strictnessLevel: 50);

        await tester.pumpWidget(buildTestApp(profile));
        await tester.pumpAndSettle();

        // Tap the 0% (Free) preset chip
        final freeChip = find.widgetWithText(ChoiceChip, '0% Free');
        expect(freeChip, findsOneWidget);
        await tester.tap(freeChip);
        await tester.pumpAndSettle();

        expect(find.text('0%'), findsWidgets);

        // Tap the 100% (Absolute) preset chip
        final absoluteChip = find.widgetWithText(ChoiceChip, '100% Absolute');
        expect(absoluteChip, findsOneWidget);
        await tester.tap(absoluteChip);
        await tester.pumpAndSettle();

        expect(find.text('100%'), findsWidgets);
      },
    );

    testWidgets(
      'test_scoring_tab_displays_absolute_consequence_at_100',
      (WidgetTester tester) async {
        final profile = createTestProfile(strictnessLevel: 100);
        await tester.pumpWidget(buildTestApp(profile));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      },
    );

    testWidgets(
      'test_scoring_tab_displays_free_consequence_at_0',
      (WidgetTester tester) async {
        final profile = createTestProfile(strictnessLevel: 0);
        await tester.pumpWidget(buildTestApp(profile));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.info_outline), findsOneWidget);
      },
    );

    testWidgets(
      'test_scoring_tab_fi_locale_360px_no_overflow',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(360, 800);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        final profile = createTestProfile(strictnessLevel: 85);
        await tester.pumpWidget(
          ProviderScope(
            overrides: [
              outputProfileFormProvider(
                'prf_test',
              ).overrideWith(() => MockValidOutputProfileForm(profile)),
            ],
            child: const MaterialApp(
              locale: Locale('fi'),
              localizationsDelegates: AppLocalizations.localizationsDelegates,
              supportedLocales: AppLocalizations.supportedLocales,
              home: Scaffold(body: ProfileScoringTab(id: 'prf_test')),
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(Slider), findsOneWidget);
        expect(find.text('85%'), findsOneWidget);
        expect(tester.takeException(), isNull);
      },
    );

    testWidgets('test_scoring_tab_does_not_render_metadata_or_xai_checkboxes', (
      WidgetTester tester,
    ) async {
      final profile = createTestProfile();

      await tester.pumpWidget(buildTestApp(profile));
      await tester.pumpAndSettle();

      // Negative test: verify no CheckboxListTile on ProfileScoringTab
      expect(find.byType(CheckboxListTile), findsNothing);
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

