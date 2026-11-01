import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/views/widgets/prompt_preview_dialog.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/l10n/gen/app_localizations_en.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  final l10n = AppLocalizationsEn();
  final List<MethodCall> clipboardCalls = <MethodCall>[];

  setUp(() {
    clipboardCalls.clear();
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(SystemChannels.platform, (
          MethodCall methodCall,
        ) async {
          if (methodCall.method == 'Clipboard.setData') {
            clipboardCalls.add(methodCall);
          }
          return null;
        });
  });

  tearDown(() {
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
        .setMockMethodCallHandler(SystemChannels.platform, null);
  });

  Widget buildTestApp(Widget child) {
    return MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('fi')],
      home: Scaffold(body: child),
    );
  }

  group('PromptPreviewFormatter', () {
    test('formatMessages formats strongly-typed LlmMessageDto list', () {
      const messages = [
        LlmMessageDto(role: 'system', content: 'System rule 1'),
        LlmMessageDto(role: 'user', content: 'User input 2'),
      ];

      final formatted = PromptPreviewFormatter.formatMessages(messages);

      expect(
        formatted,
        '--- Role: system ---\nSystem rule 1\n\n--- Role: user ---\nUser input 2',
      );
    });

    test('formatMessages boundary: returns empty string for empty list', () {
      expect(PromptPreviewFormatter.formatMessages(const []), isEmpty);
    });

    test('formatSchema encodes Map and List structures with indentation', () {
      final mapSchema = <String, Object?>{
        'type': 'object',
        'required': ['score'],
      };
      final formattedMap = PromptPreviewFormatter.formatSchema(
        mapSchema,
        'fallback_ignored',
      );
      expect(formattedMap, contains('"type": "object"'));
      expect(formattedMap, contains('  "required": [\n    "score"\n  ]'));

      final listSchema = <Object?>[
        <String, Object?>{'name': 'tool_a'},
      ];
      final formattedList = PromptPreviewFormatter.formatSchema(
        listSchema,
        null,
      );
      expect(formattedList, contains('"name": "tool_a"'));
    });

    test(
      'formatSchema negative & boundary: falls back when tools is null or whitespace and returns empty when both missing',
      () {
        expect(
          PromptPreviewFormatter.formatSchema(null, 'rendered_fallback'),
          'rendered_fallback',
        );
        expect(
          PromptPreviewFormatter.formatSchema('   ', 'rendered_fallback'),
          'rendered_fallback',
        );
        expect(PromptPreviewFormatter.formatSchema(null, null), isEmpty);
        expect(PromptPreviewFormatter.formatSchema(null, ''), isEmpty);
      },
    );
  });

  group('PromptPreviewDialog', () {
    testWidgets(
      'renders 3 tabs, switches tab content, copies active tab to clipboard, and resets state after timer',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1400, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);

        await tester.pumpWidget(
          buildTestApp(
            const PromptPreviewDialog(
              staticContent: 'STATIC_SYSTEM_PROMPT',
              dynamicContent: 'DYNAMIC_USER_CONTEXT',
              schemaContent: '{"type": "object"}',
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text(l10n.previewPromptTitle), findsOneWidget);
        expect(find.text(l10n.previewPromptStaticTab), findsOneWidget);
        expect(find.text(l10n.previewPromptDynamicTab), findsOneWidget);
        expect(find.text(l10n.previewPromptSchemaTab), findsOneWidget);

        // Static tab is initially active
        expect(find.text('STATIC_SYSTEM_PROMPT'), findsOneWidget);

        // Copy static content
        await tester.tap(find.text(l10n.copyToClipboardBtn));
        await tester.pump();

        expect(clipboardCalls, hasLength(1));
        expect(clipboardCalls.single.arguments, <String, Object?>{
          'text': 'STATIC_SYSTEM_PROMPT',
        });
        expect(find.text(l10n.copiedToClipboard), findsOneWidget);

        // Advance timer past 2 seconds to verify reset
        await tester.pump(const Duration(seconds: 2));
        expect(find.text(l10n.copyToClipboardBtn), findsOneWidget);

        // Switch to Dynamic tab
        await tester.tap(find.text(l10n.previewPromptDynamicTab));
        await tester.pumpAndSettle();
        expect(find.text('DYNAMIC_USER_CONTEXT'), findsOneWidget);

        // Switch to Schema tab
        await tester.tap(find.text(l10n.previewPromptSchemaTab));
        await tester.pumpAndSettle();
        expect(find.text('{"type": "object"}'), findsOneWidget);
      },
    );

    testWidgets(
      'negative & boundary: renders placeholder when all panes are empty and suppresses clipboard write',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestApp(
            const PromptPreviewDialog(
              staticContent: '',
              dynamicContent: '',
              schemaContent: '',
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Empty active pane shows "---" placeholder
        expect(find.text('---'), findsOneWidget);

        // Clicking copy when all 3 tabs are empty does not invoke Clipboard.setData
        await tester.tap(find.text(l10n.copyToClipboardBtn));
        await tester.pump();

        expect(clipboardCalls, isEmpty);
        expect(find.text(l10n.copiedToClipboard), findsNothing);
      },
    );

    testWidgets(
      'boundary: copies fallback schemaContent when active static tab is empty, and closes dialog via close button',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          buildTestApp(
            Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showDialog<void>(
                    context: context,
                    builder: (_) => const PromptPreviewDialog(
                      staticContent: '',
                      dynamicContent: '',
                      schemaContent: 'SCHEMA_FALLBACK_PAYLOAD',
                    ),
                  );
                },
                child: const Text('Open'),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open'));
        await tester.pumpAndSettle();

        expect(find.byType(PromptPreviewDialog), findsOneWidget);

        // Active tab 0 (staticContent) is empty, so copy falls back to schemaContent
        await tester.tap(find.text(l10n.copyToClipboardBtn));
        await tester.pump();

        expect(clipboardCalls, hasLength(1));
        expect(clipboardCalls.single.arguments, <String, Object?>{
          'text': 'SCHEMA_FALLBACK_PAYLOAD',
        });

        // Close dialog before 2-second timer completes to verify safe timer cancellation on dispose
        await tester.tap(find.byIcon(Icons.close));
        await tester.pumpAndSettle();
        await tester.pump(const Duration(seconds: 2));

        expect(find.byType(PromptPreviewDialog), findsNothing);
      },
    );
  });
}
