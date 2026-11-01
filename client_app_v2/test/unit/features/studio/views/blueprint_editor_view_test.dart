import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/views/blueprint_editor_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockLoggerService extends Mock implements LoggerService {}

void main() {
  late MockLoggerService mockLogger;

  setUp(() {
    mockLogger = MockLoggerService();
    when(() => mockLogger.error(any(), any(), any(), any())).thenReturn(null);
  });

  Widget createSubject({
    required Map<String, Object?> initialBlueprint,
    required ValueChanged<Map<String, Object?>> onSave,
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [loggerServiceProvider.overrideWithValue(mockLogger)],
      child: MaterialApp(
        theme: AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Builder(
          builder: (context) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute<void>(
                      builder: (_) => BlueprintEditorView(
                        initialBlueprint: initialBlueprint,
                        onSave: onSave,
                      ),
                    ),
                  );
                },
                child: const Text('Open Editor'),
              ),
            ),
          ),
        ),
      ),
    );
  }

  group('BlueprintEditorView Widget & Hardening Tests', () {
    testWidgets(
      'Positive: hydrates initialBlueprint, renders localized PresetView options, mutates state on dropdown selection, and invokes onSave with serialized JSON on save',
      (WidgetTester tester) async {
        Map<String, Object?>? savedPayload;

        await tester.pumpWidget(
          createSubject(
            initialBlueprint: const <String, Object?>{
              'preset_view': '2d_compare',
            },
            onSave: (payload) => savedPayload = payload,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Open Editor'));
        await tester.pumpAndSettle();

        expect(find.byType(BlueprintEditorView), findsOneWidget);
        expect(find.byType(AppErrorBoundary), findsOneWidget);

        final BuildContext viewContext = tester.element(
          find.byType(BlueprintEditorView),
        );
        final l10n = AppLocalizations.of(viewContext)!;

        final dropdown = tester.widget<DropdownButtonFormField<PresetView>>(
          find.byType(DropdownButtonFormField<PresetView>),
        );
        expect(dropdown.initialValue, equals(PresetView.compare2d));

        // Open dropdown and select 3D Matrix option
        await tester.tap(find.byType(DropdownButtonFormField<PresetView>));
        await tester.pumpAndSettle();

        await tester.tap(find.text(l10n.studioViewsMatrix3d).last);
        await tester.pumpAndSettle();

        // Tap Save button
        await tester.tap(find.byIcon(Icons.check));
        await tester.pumpAndSettle();

        expect(
          savedPayload,
          equals(<String, Object?>{'preset_view': '3d_matrix'}),
        );
        expect(find.byType(BlueprintEditorView), findsNothing);
      },
    );

    testWidgets(
      'Negative 1 (ISTQB BVA / Unrecognized Schema Key): unrecognized key in initialBlueprint triggers Fail-Fast logging, renders ErrorView diagnostic node, and hides Save action',
      (WidgetTester tester) async {
        Map<String, Object?>? savedPayload;

        await tester.pumpWidget(
          createSubject(
            initialBlueprint: const <String, Object?>{
              'preset_view': '1d_metrics',
              'illegal_extra_field': 'forbidden',
            },
            onSave: (payload) => savedPayload = payload,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Open Editor'));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'BlueprintEditorController',
            any(that: contains('BLUEPRINT_INIT_FAILED')),
            any(),
            any(),
          ),
        ).called(1);

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byIcon(Icons.check), findsNothing);
        expect(savedPayload, isNull);
      },
    );

    testWidgets(
      'Negative 2 (ISTQB BVA / Invalid Enum Value & Narrow Viewport Boundary): invalid preset_view value renders ErrorView in Finnish locale and narrow viewport (320px) renders without overflow',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(320, 600);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          createSubject(
            initialBlueprint: const <String, Object?>{
              'preset_view': 'invalid_unknown_preset',
            },
            onSave: (_) {},
            locale: const Locale('fi'),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.text('Open Editor'));
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        verify(
          () => mockLogger.error(
            'BlueprintEditorController',
            any(that: contains('BLUEPRINT_INIT_FAILED')),
            any(),
            any(),
          ),
        ).called(1);

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(DropdownButtonFormField<PresetView>), findsNothing);
      },
    );
  });
}
