import 'dart:typed_data';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/file_uploader.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _RecordingLoggerService extends LoggerService {
  final List<String> loggedErrors = [];

  _RecordingLoggerService()
    : super(
        telemetryDio: Dio(BaseOptions(baseUrl: 'https://test.invalid'))
          ..interceptors.add(
            InterceptorsWrapper(
              onRequest: (options, handler) => handler.resolve(
                Response(requestOptions: options, statusCode: 200),
              ),
            ),
          ),
      );

  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    loggedErrors.add('[$context] $message');
  }
}

void main() {
  Widget buildTestHarness({
    required String label,
    String? initialFileName,
    bool isLoading = false,
    String? errorText,
    ValueChanged<PlatformFile>? onFileSelected,
    VoidCallback? onClear,
    Future<FilePickerResult?> Function()? pickFiles,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final uploader = FileUploader(
      label: label,
      initialFileName: initialFileName,
      isLoading: isLoading,
      errorText: errorText,
      onFileSelected: onFileSelected,
      onClear: onClear,
      pickFiles: pickFiles,
    );

    return ProviderScope(
      overrides: [
        if (logger != null) loggerServiceProvider.overrideWithValue(logger),
      ],
      child: MaterialApp(
        theme: theme ?? AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: Scaffold(
          body: SingleChildScrollView(
            child: width != null
                ? SizedBox(width: width, child: uploader)
                : uploader,
          ),
        ),
      ),
    );
  }

  group('FileUploader Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders localized prompt, selects file via picker, displays filename, and clears selection',
      (WidgetTester tester) async {
        PlatformFile? selectedFile;
        var cleared = false;
        final pickedFile = PlatformFile(
          name: 'executive_audit_report.pdf',
          size: 2048,
          bytes: Uint8List.fromList([1, 2, 3, 4]),
        );

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Source Document',
            onFileSelected: (file) => selectedFile = file,
            onClear: () => cleared = true,
            pickFiles: () async => FilePickerResult([pickedFile]),
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.text('Source Document'), findsOneWidget);
        expect(find.text(l10n.sharedSelectFile), findsOneWidget);
        expect(find.byIcon(Icons.attach_file), findsOneWidget);

        await tester.tap(find.byType(InkWell));
        await tester.pumpAndSettle();

        expect(selectedFile, equals(pickedFile));
        expect(find.text('executive_audit_report.pdf'), findsOneWidget);
        expect(find.byIcon(Icons.close), findsOneWidget);

        await tester.tap(find.byIcon(Icons.close));
        await tester.pumpAndSettle();

        expect(cleared, isTrue);
        expect(find.text(l10n.sharedSelectFile), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 1: extreme long filename and error text in narrow 220px dark mode Finnish viewport render with ellipsis without overflow',
      (WidgetTester tester) async {
        const longFileName =
            'ExtraordinarilyLongEnterpriseExecutiveCoachingTranscriptDocumentFileNameWithoutSpaces_v2026_Final.pdf';

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Erittäin pitkä asiakirjan otsikko kapeassa näkymässä',
            initialFileName: longFileName,
            errorText:
                'Tiedoston validointi epäonnistui kokorajoituksen vuoksi kapeassa näkymässä.',
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 220,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.text(longFileName), findsOneWidget);
        expect(
          find.text(
            'Tiedoston validointi epäonnistui kokorajoituksen vuoksi kapeassa näkymässä.',
          ),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Boundary 2: isLoading state disables tap interaction, hides clear button, and displays CircularProgressIndicator with localized uploading text',
      (WidgetTester tester) async {
        var pickerInvoked = false;
        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Upload State',
            initialFileName: 'existing.pdf',
            isLoading: true,
            locale: const Locale('fi'),
            pickFiles: () async {
              pickerInvoked = true;
              return null;
            },
          ),
        );
        await tester.pump();

        expect(find.byType(CircularProgressIndicator), findsOneWidget);
        expect(find.text(l10nFi.sharedUploading), findsOneWidget);
        expect(find.byIcon(Icons.close), findsNothing);

        await tester.tap(find.byType(InkWell));
        await tester.pump();

        expect(pickerInvoked, isFalse);
      },
    );

    testWidgets(
      'Negative 1: empty label, blank initialFileName, or blank errorText logs error via LoggerService and renders compact ErrorView',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(buildTestHarness(label: '   ', logger: logger));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render FileUploader',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            label: 'Valid Label',
            initialFileName: '   ',
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render FileUploader',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            label: 'Valid Label',
            errorText: '   ',
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render FileUploader',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: picker exception or malformed PlatformFile (empty name or negative size) logs via LoggerService and shows localized SnackBar',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Valid Label',
            logger: logger,
            pickFiles: () async =>
                FilePickerResult([PlatformFile(name: '   ', size: 10)]),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(InkWell));
        await tester.pumpAndSettle();

        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains('[FileUploader] File Uploader Error:'),
          ),
          isTrue,
        );
        expect(find.byType(SnackBar), findsOneWidget);

        ScaffoldMessenger.of(
          tester.element(find.byType(FileUploader)),
        ).clearSnackBars();
        logger.loggedErrors.clear();

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Valid Label',
            logger: logger,
            pickFiles: () async => throw Exception('IO permission denied'),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(InkWell));
        await tester.pumpAndSettle();

        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('[FileUploader] File Uploader Error:') &&
                msg.contains('IO permission denied'),
          ),
          isTrue,
        );
        expect(find.byType(SnackBar), findsOneWidget);
      },
    );
  });
}
