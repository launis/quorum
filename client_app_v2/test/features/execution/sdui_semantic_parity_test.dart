import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/features/execution/views/widgets/report_renderer_v2_widget.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

// Phase 2: Granular Typographical Token Extractor for SDUI Semantic Parity
void main() {
  testWidgets('SDUI Semantic Parity Extractor', (WidgetTester tester) async {
    const goldenPath = String.fromEnvironment('GOLDEN_PATH');
    const dumpPath = String.fromEnvironment('DUMP_PATH');

    if (goldenPath.isEmpty || dumpPath.isEmpty) {
      return;
    }

    final goldenFile = File(goldenPath);
    if (!goldenFile.existsSync()) {
      throw StateError('Golden file not found at $goldenPath');
    }

    final jsonStr = goldenFile.readAsStringSync();
    final jsonMap = jsonDecode(jsonStr) as Map<String, dynamic>;
    final payload = ReportDataDto.fromJson(jsonMap);

    // CRITICAL: Call tester.ensureSemantics() before rendering
    final semanticsHandle = tester.ensureSemantics();

    tester.view.physicalSize = const Size(2400, 10000);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() => tester.view.resetPhysicalSize());
    addTearDown(() => tester.view.resetDevicePixelRatio());

    try {
      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: AppLocalizations.localizationsDelegates,
          supportedLocales: AppLocalizations.supportedLocales,
          locale: const Locale('en'), // We enforce English for the parity test
          home: Scaffold(
            body: ReportRendererV2Widget(
              payload: payload,
              executionId: 'parity_test_exec',
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      final extractedTokens = <Map<String, dynamic>>[];

      // 1. RichText widgets
      final richTextWidgets = tester.widgetList<RichText>(
        find.descendant(
          of: find.byType(ReportRendererV2Widget, skipOffstage: false),
          matching: find.byType(RichText, skipOffstage: false),
          skipOffstage: false,
        ),
      );
      for (final richText in richTextWidgets) {
        _extractSpans(richText.text, null, extractedTokens);
      }

      // 2. Plain Text widgets
      final textWidgets = tester.widgetList<Text>(
        find.descendant(
          of: find.byType(ReportRendererV2Widget, skipOffstage: false),
          matching: find.byType(Text, skipOffstage: false),
          skipOffstage: false,
        ),
      );
      for (final textWidget in textWidgets) {
        final str = textWidget.data;
        if (str != null && str.trim().isNotEmpty) {
          final style = textWidget.style;
          final isBold =
              style?.fontWeight == FontWeight.bold ||
              style?.fontWeight == FontWeight.w700 ||
              style?.fontWeight == FontWeight.w800 ||
              style?.fontWeight == FontWeight.w900;
          final isItalic = style?.fontStyle == FontStyle.italic;
          final isHeader = style?.fontSize != null && style!.fontSize! >= 20.0;
          _addToken(extractedTokens, str, isBold, isItalic, isHeader);
        }
      }

      // 3. SelectableText widgets (rendered by MarkdownBody with selectable: true)
      final selectableTextWidgets = tester.widgetList<SelectableText>(
        find.descendant(
          of: find.byType(ReportRendererV2Widget, skipOffstage: false),
          matching: find.byType(SelectableText, skipOffstage: false),
          skipOffstage: false,
        ),
      );
      for (final selectable in selectableTextWidgets) {
        if (selectable.textSpan != null) {
          _extractSpans(
            selectable.textSpan!,
            selectable.style,
            extractedTokens,
          );
        } else if (selectable.data != null &&
            selectable.data!.trim().isNotEmpty) {
          final style = selectable.style;
          final isBold =
              style?.fontWeight == FontWeight.bold ||
              style?.fontWeight == FontWeight.w700 ||
              style?.fontWeight == FontWeight.w800 ||
              style?.fontWeight == FontWeight.w900;
          final isItalic = style?.fontStyle == FontStyle.italic;
          final isHeader = style?.fontSize != null && style!.fontSize! >= 20.0;
          _addToken(
            extractedTokens,
            selectable.data!,
            isBold,
            isItalic,
            isHeader,
          );
        }
      }

      final dumpFile = File(dumpPath);
      dumpFile.writeAsStringSync(jsonEncode(extractedTokens));
    } finally {
      semanticsHandle.dispose();
    }
  });
}

void _addToken(
  List<Map<String, dynamic>> tokens,
  String text,
  bool isBold,
  bool isItalic,
  bool isHeader,
) {
  final clean = text.trim();
  if (clean.length < 2) return;
  const accessibilityStates = {
    'Expanded',
    'Collapsed',
    'Double tap to activate',
    'Double tap to expand',
  };
  if (accessibilityStates.contains(clean)) return;

  for (final line in clean.split('\n')) {
    final cleanLine = line.trim();
    if (cleanLine.length < 2) continue;
    if (accessibilityStates.contains(cleanLine)) continue;
    final exists = tokens.any(
      (t) =>
          t['text'] == cleanLine &&
          t['is_bold'] == isBold &&
          t['is_italic'] == isItalic &&
          t['is_header'] == isHeader,
    );
    if (!exists) {
      tokens.add({
        'text': cleanLine,
        'is_bold': isBold,
        'is_italic': isItalic,
        'is_header': isHeader,
      });
    }
  }
}

void _extractSpans(
  InlineSpan span,
  TextStyle? parentStyle,
  List<Map<String, dynamic>> extractedTokens,
) {
  final effectiveStyle = parentStyle != null && span.style != null
      ? parentStyle.merge(span.style)
      : (span.style ?? parentStyle);

  if (span is TextSpan) {
    final text = span.text;
    if (text != null && text.trim().isNotEmpty) {
      final isBold =
          effectiveStyle?.fontWeight == FontWeight.bold ||
          effectiveStyle?.fontWeight == FontWeight.w700 ||
          effectiveStyle?.fontWeight == FontWeight.w800 ||
          effectiveStyle?.fontWeight == FontWeight.w900;
      final isItalic = effectiveStyle?.fontStyle == FontStyle.italic;
      final isHeader =
          effectiveStyle?.fontSize != null && effectiveStyle!.fontSize! >= 20.0;
      _addToken(extractedTokens, text, isBold, isItalic, isHeader);
    }
    final children = span.children;
    if (children != null) {
      for (final child in children) {
        _extractSpans(child, effectiveStyle, extractedTokens);
      }
    }
  }
}
