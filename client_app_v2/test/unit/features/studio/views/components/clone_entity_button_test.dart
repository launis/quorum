import 'dart:async';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/features/studio/views/components/clone_entity_button.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
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
    required Future<Object?> Function() onClone,
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [loggerServiceProvider.overrideWithValue(mockLogger)],
      child: MaterialApp(
        theme: AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: Center(child: CloneEntityButton(onClone: onClone)),
        ),
      ),
    );
  }

  group('CloneEntityButton Widget & Hardening Tests', () {
    testWidgets(
      'Positive: renders localized duplicate tooltip, transitions through loading spinner, and displays floating success SnackBar on completion',
      (WidgetTester tester) async {
        final completer = Completer<Object?>();

        await tester.pumpWidget(createSubject(onClone: () => completer.future));
        await tester.pumpAndSettle();

        final BuildContext context = tester.element(
          find.byType(CloneEntityButton),
        );
        final l10n = AppLocalizations.of(context)!;

        final iconButton = tester.widget<IconButton>(find.byType(IconButton));
        expect(iconButton.tooltip, equals(l10n.tooltipDuplicate));
        expect(find.byIcon(Icons.copy), findsOneWidget);

        // Trigger clone mutation
        await tester.tap(find.byType(IconButton));
        await tester.pump();

        // Verify loading indicator is shown while future is pending
        expect(find.byType(CircularProgressIndicator), findsOneWidget);
        expect(find.byType(IconButton), findsNothing);

        // Complete clone operation
        completer.complete('wf_cloned');
        await tester.pumpAndSettle();

        // Verify button returns to idle state and floating SnackBar is displayed
        expect(find.byType(CircularProgressIndicator), findsNothing);
        expect(find.byType(IconButton), findsOneWidget);
        expect(find.text(l10n.msgEntityClonedSuccess), findsOneWidget);

        final snackBar = tester.widget<SnackBar>(find.byType(SnackBar));
        expect(snackBar.behavior, equals(SnackBarBehavior.floating));
        verifyNever(() => mockLogger.error(any(), any(), any(), any()));
      },
    );

    testWidgets(
      'Positive (Dual-Axis Localization): renders Finnish (fi) tooltip and success message accurately',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          createSubject(
            locale: const Locale('fi'),
            onClone: () async => 'blk_cloned',
          ),
        );
        await tester.pumpAndSettle();

        final BuildContext context = tester.element(
          find.byType(CloneEntityButton),
        );
        final l10n = AppLocalizations.of(context)!;

        final iconButton = tester.widget<IconButton>(find.byType(IconButton));
        expect(iconButton.tooltip, equals(l10n.tooltipDuplicate));

        await tester.tap(find.byType(IconButton));
        await tester.pumpAndSettle();

        expect(find.text(l10n.msgEntityClonedSuccess), findsOneWidget);
      },
    );

    testWidgets(
      'Negative (AppException Dual-Reporting): logs failure via LoggerService and renders localized error SnackBar with theme error color',
      (WidgetTester tester) async {
        const exception = AppException(
          detail: 'Missing prompt block dependency',
          status: 422,
          extensions: <String, Object?>{'error_code': 'WORKFLOW_CLONE_FAILED'},
        );

        await tester.pumpWidget(
          createSubject(
            onClone: () async {
              throw exception;
            },
          ),
        );
        await tester.pumpAndSettle();

        final BuildContext context = tester.element(
          find.byType(CloneEntityButton),
        );
        final l10n = AppLocalizations.of(context)!;
        final expectedErrorColor = Theme.of(context).colorScheme.error;

        await tester.tap(find.byType(IconButton));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'CloneEntityButton',
            'Clone operation failed',
            exception,
          ),
        ).called(1);

        final expectedMessage = l10n.msgEntityCloneFailed(
          l10n.workflowCloneErrorMissingDep,
        );
        expect(find.text(expectedMessage), findsOneWidget);

        final snackBar = tester.widget<SnackBar>(find.byType(SnackBar));
        expect(snackBar.backgroundColor, equals(expectedErrorColor));
        expect(snackBar.behavior, equals(SnackBarBehavior.floating));
      },
    );

    testWidgets(
      'Negative (DioException Network Failure): logs error via LoggerService and displays localized network failure hint',
      (WidgetTester tester) async {
        final dioError = DioException(
          requestOptions: RequestOptions(path: '/api/v2/workflows/clone'),
          type: DioExceptionType.connectionTimeout,
        );

        await tester.pumpWidget(
          createSubject(
            onClone: () async {
              throw dioError;
            },
          ),
        );
        await tester.pumpAndSettle();

        final BuildContext context = tester.element(
          find.byType(CloneEntityButton),
        );
        final l10n = AppLocalizations.of(context)!;

        await tester.tap(find.byType(IconButton));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'CloneEntityButton',
            'Clone operation failed',
            dioError,
          ),
        ).called(1);

        final expectedMessage = l10n.msgEntityCloneFailed(l10n.errorNetwork);
        expect(find.text(expectedMessage), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary (Unknown Exception & Retry Recovery): maps generic Exception to errorUnknown and recovers cleanly on subsequent retry tap',
      (WidgetTester tester) async {
        var attempts = 0;

        await tester.pumpWidget(
          createSubject(
            onClone: () async {
              attempts += 1;
              if (attempts == 1) {
                throw Exception('Unexpected runtime failure');
              }
              return 'wf_recovered';
            },
          ),
        );
        await tester.pumpAndSettle();

        final BuildContext context = tester.element(
          find.byType(CloneEntityButton),
        );
        final l10n = AppLocalizations.of(context)!;

        // First tap fails with generic Exception
        await tester.tap(find.byType(IconButton));
        await tester.pumpAndSettle();

        verify(
          () => mockLogger.error(
            'CloneEntityButton',
            'Clone operation failed',
            any(),
          ),
        ).called(1);

        expect(
          find.text(l10n.msgEntityCloneFailed(l10n.errorUnknown)),
          findsOneWidget,
        );
        expect(find.byType(IconButton), findsOneWidget);

        // Dismiss active SnackBar and retry
        ScaffoldMessenger.of(context).clearSnackBars();
        await tester.pumpAndSettle();

        await tester.tap(find.byType(IconButton));
        await tester.pumpAndSettle();

        expect(attempts, equals(2));
        expect(find.text(l10n.msgEntityClonedSuccess), findsOneWidget);
      },
    );
  });
}
