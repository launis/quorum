import 'dart:typed_data';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/omni_input_box.dart';
import 'package:client_app/shared/widgets/pdf_export_guide_dialog.dart';
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
    required String keyName,
    required String label,
    Object? currentValue,
    IconData? icon,
    int minLines = 1,
    ValueChanged<Object?>? onChanged,
    Future<FilePickerResult?> Function()? pickFiles,
    GlobalKey<FormState>? formKey,
    ThemeData? theme,
    Locale locale = const Locale('fi'),
    double? width,
    LoggerService? logger,
  }) {
    final box = OmniInputBox(
      keyName: keyName,
      label: label,
      currentValue: currentValue,
      icon: icon,
      minLines: minLines,
      onChanged: onChanged ?? (_) {},
      pickFiles: pickFiles,
    );

    final content = formKey != null ? Form(key: formKey, child: box) : box;

    return ProviderScope(
      overrides: [
        if (logger != null) loggerServiceProvider.overrideWithValue(logger),
      ],
      child: MaterialApp(
        theme: theme ?? AppTheme.light,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        locale: locale,
        home: Scaffold(
          body: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: width != null
                  ? SizedBox(width: width, child: content)
                  : content,
            ),
          ),
        ),
      ),
    );
  }

  group('OmniInputBox Dumb Painter & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive 1: renders with help button, opens PdfExportGuideDialog on tap, and emits text changes',
      (tester) async {
        Object? latestValue;
        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label: 'Keskusteluhistoria',
            icon: Icons.chat_bubble_outline,
            onChanged: (val) => latestValue = val,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Keskusteluhistoria'), findsOneWidget);
        expect(find.byIcon(Icons.help_outline), findsOneWidget);
        expect(find.byIcon(Icons.chat_bubble_outline), findsOneWidget);

        await tester.enterText(
          find.byType(TextFormField),
          'Käyttäjä: Hei valmentaja',
        );
        expect(latestValue, equals('Käyttäjä: Hei valmentaja'));

        await tester.tap(find.byIcon(Icons.help_outline));
        await tester.pumpAndSettle();

        expect(find.byType(PdfExportGuideDialog), findsOneWidget);
        expect(find.text('Keskustelun tuominen Quorumiin'), findsOneWidget);

        await tester.tap(find.text('Sulje'));
        await tester.pumpAndSettle();
        expect(find.byType(PdfExportGuideDialog), findsNothing);
      },
    );

    testWidgets(
      'Positive 2: displays truncation warning banner for chat_log in file mode, hides for non-chat keys, and picks/clears files',
      (tester) async {
        Object? latestValue = 'initial text';
        final sampleFile = PlatformFile(
          name: 'chat_export.pdf',
          size: 2048,
          bytes: Uint8List.fromList([1, 2, 3]),
        );

        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label: 'Keskusteluhistoria',
            currentValue: latestValue,
            onChanged: (val) => latestValue = val,
            pickFiles: () async => FilePickerResult([sampleFile]),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning_amber_rounded), findsNothing);
        expect(find.textContaining('leikkautuneet poikki'), findsNothing);

        await tester.tap(find.byIcon(Icons.upload_file));
        await tester.pumpAndSettle();

        expect(latestValue, isNull);
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
        expect(find.textContaining('leikkautuneet poikki'), findsOneWidget);

        await tester.tap(find.byIcon(Icons.attach_file));
        await tester.pumpAndSettle();
        expect(latestValue, equals(sampleFile));

        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'product_text',
            label: 'Lopputuote',
            onChanged: (val) => latestValue = val,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byIcon(Icons.upload_file));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.warning_amber_rounded), findsNothing);
        expect(find.textContaining('leikkautuneet poikki'), findsNothing);
      },
    );

    testWidgets(
      'Boundary 1: narrow 240px viewport in Finnish dark mode with long label and PlatformFile renders without overflow',
      (tester) async {
        final boundaryFile = PlatformFile(
          name:
              'ExtraordinarilyLongEnterpriseExecutiveCoachingTranscriptDocumentFileName_v2026.pdf',
          size: 0,
          bytes: Uint8List(0),
        );

        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label:
                'ErittäinPitkäKeskusteluhistorianOtsikkoIlmanVälilyöntejäKapeassaNäkymässä',
            currentValue: boundaryFile,
            icon: Icons.assignment_outlined,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
      },
    );

    testWidgets(
      'Boundary 2: form validation enforces required text in paste mode and required file in file mode',
      (tester) async {
        final formKey = GlobalKey<FormState>();
        final l10n = await AppLocalizations.delegate.load(const Locale('en'));

        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label: 'Conversation History',
            formKey: formKey,
            locale: const Locale('en'),
          ),
        );
        await tester.pumpAndSettle();

        expect(formKey.currentState!.validate(), isFalse);
        await tester.pumpAndSettle();
        expect(find.text(l10n.fieldRequired), findsOneWidget);

        await tester.enterText(find.byType(TextFormField), '   ');
        expect(formKey.currentState!.validate(), isFalse);

        await tester.enterText(find.byType(TextFormField), 'Valid transcript');
        expect(formKey.currentState!.validate(), isTrue);

        await tester.tap(find.byIcon(Icons.upload_file));
        await tester.pumpAndSettle();

        expect(formKey.currentState!.validate(), isFalse);
        await tester.pumpAndSettle();
        expect(find.text(l10n.fileRequired), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty label, empty keyName, or minLines < 1 logs error via LoggerService and renders compact ErrorView',
      (tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(keyName: 'chat_log', label: '   ', logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render OmniInputBox',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(keyName: '  ', label: 'Valid Label', logger: logger),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render OmniInputBox',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label: 'Valid Label',
            minLines: 0,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render OmniInputBox',
            ),
          ),
          isTrue,
        );
      },
    );

    testWidgets(
      'Negative 2: unsupported currentValue runtime type or malformed PlatformFile logs via LoggerService and renders ErrorView',
      (tester) async {
        final logger = _RecordingLoggerService();

        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label: 'Valid Label',
            currentValue: 12345,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render OmniInputBox',
            ),
          ),
          isTrue,
        );

        logger.loggedErrors.clear();
        final invalidFile = PlatformFile(name: '   ', size: 128);
        await tester.pumpWidget(
          buildTestHarness(
            keyName: 'chat_log',
            label: 'Valid Label',
            currentValue: invalidFile,
            logger: logger,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byType(ErrorView), findsOneWidget);
        expect(
          logger.loggedErrors.any(
            (msg) => msg.contains(
              'VALIDATION_FAILED: Failed to render OmniInputBox',
            ),
          ),
          isTrue,
        );
      },
    );
  });
}
