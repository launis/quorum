import 'dart:typed_data';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/file_input_field.dart';
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
    PlatformFile? value,
    IconData? icon,
    ValueChanged<PlatformFile>? onFileSelected,
    VoidCallback? onClear,
    String? Function(PlatformFile?)? validator,
    Future<FilePickerResult?> Function()? pickFiles,
    GlobalKey<FormState>? formKey,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
    LoggerService? logger,
  }) {
    final field = FileInputField(
      label: label,
      value: value,
      icon: icon,
      onFileSelected: onFileSelected ?? (_) {},
      onClear: onClear ?? () {},
      validator: validator,
      pickFiles: pickFiles,
    );

    final content = formKey != null ? Form(key: formKey, child: field) : field;

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
                ? SizedBox(width: width, child: content)
                : content,
          ),
        ),
      ),
    );
  }

  group('FileInputField Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: renders empty state with localized prompt, picks file, displays file info, and clears selection',
      (WidgetTester tester) async {
        PlatformFile? selectedFile;
        var cleared = false;
        final pickedFile = PlatformFile(
          name: 'coaching_transcript.pdf',
          size: 4096,
          bytes: Uint8List.fromList([1, 2, 3, 4]),
        );

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Upload Transcript',
            icon: Icons.upload_file,
            onFileSelected: (file) => selectedFile = file,
            onClear: () => cleared = true,
            pickFiles: () async => FilePickerResult([pickedFile]),
          ),
        );
        await tester.pumpAndSettle();

        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        expect(find.text('Upload Transcript'), findsOneWidget);
        expect(find.text(l10n.selectFile), findsOneWidget);
        expect(find.byIcon(Icons.attach_file), findsOneWidget);
        expect(find.byIcon(Icons.upload_file), findsOneWidget);

        await tester.tap(find.byType(InkWell));
        await tester.pumpAndSettle();

        expect(selectedFile, equals(pickedFile));

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Upload Transcript',
            value: pickedFile,
            onClear: () => cleared = true,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('coaching_transcript.pdf'), findsOneWidget);
        expect(
          find.text(l10n.fileInputLabel('coaching_transcript.pdf', 4096)),
          findsOneWidget,
        );
        expect(find.byIcon(Icons.clear), findsOneWidget);

        await tester.tap(find.byIcon(Icons.clear));
        await tester.pumpAndSettle();

        expect(cleared, isTrue);
      },
    );

    testWidgets(
      'Boundary 1: 0-byte file and extreme long filename in narrow 240px dark mode viewport render with ellipsis without overflow',
      (WidgetTester tester) async {
        final boundaryFile = PlatformFile(
          name:
              'ExtraordinarilyLongEnterpriseExecutiveCoachingTranscriptDocumentFileNameWithoutSpaces_v2026_Final.pdf',
          size: 0,
          bytes: Uint8List(0),
        );

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Document Source',
            value: boundaryFile,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));
        expect(
          find.text(l10nFi.fileInputLabel(boundaryFile.name, 0)),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Boundary 2: form validation triggers error text when required file is missing',
      (WidgetTester tester) async {
        final formKey = GlobalKey<FormState>();
        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Required File',
            formKey: formKey,
            validator: (value) => value == null ? l10n.fileRequired : null,
          ),
        );
        await tester.pumpAndSettle();

        expect(formKey.currentState!.validate(), isFalse);
        await tester.pumpAndSettle();

        expect(find.text(l10n.fileRequired), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty label logs error via LoggerService and renders compact ErrorView (Fail-Fast UI Boundary)',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(buildTestHarness(label: '   ', logger: logger));
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(find.byType(InputDecorator), findsNothing);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render FileInputField',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: malformed PlatformFile (empty name or negative size) and picker exception log via LoggerService',
      (WidgetTester tester) async {
        final logger = _RecordingLoggerService();
        final invalidFile = PlatformFile(name: '  ', size: 100);

        await tester.pumpWidget(
          buildTestHarness(
            label: 'Valid Label',
            value: invalidFile,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render FileInputField',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            label: 'Valid Label',
            logger: logger,
            pickFiles: () async => throw Exception('Disk read failure'),
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(InkWell));
        await tester.pumpAndSettle();

        expect(
          logger.loggedErrors.any(
            (msg) =>
                msg.contains('[FileInputField] File Error:') &&
                msg.contains('Disk read failure'),
          ),
          isTrue,
        );
        expect(find.byType(SnackBar), findsOneWidget);
      },
    );
  });
}
