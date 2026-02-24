import 'dart:io';
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/knowledge_base/controller/ingestion_controller.dart';
import 'package:client_app/features/knowledge_base/view/ingestion_view.dart';
import 'package:client_app/models/knowledge_base.dart';

// Mocks and fakes

void main() {
  Widget createWidgetUnderTest(AsyncValue<IngestionStatus?> state) {
    return ProviderScope(
      overrides: [
        ingestionControllerProvider.overrideWith(() => MockIngestionController(state)),
      ],
      child: MaterialApp(
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: const IngestionView(),
      ),
    );
  }

  group('IngestionView Tests', () {
    testWidgets('Renders initial state correctly', (tester) async {
      await tester.pumpWidget(createWidgetUnderTest(const AsyncValue.data(null)));
      await tester.pumpAndSettle();

      expect(find.text('Knowledge Base Ingestion'), findsOneWidget);
      expect(find.text('Upload DOCX / MD'), findsOneWidget);
      // "Select File" text depends on L10n, assuming English for test context or checking key presence
      // Since we use real L10n delegates, we expect English default
      expect(find.byType(ElevatedButton), findsOneWidget);
    });

    testWidgets('Renders progress state correctly', (tester) async {
      final status = IngestionStatus(
        jobId: '123',
        status: 'processing',
        progress: 50,
        stage: 'Parsing',
      );
      
      await tester.pumpWidget(createWidgetUnderTest(AsyncValue.data(status)));
      await tester.pumpAndSettle();

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
      expect(find.text('Parsing (50%)'), findsOneWidget);
    });

    testWidgets('Renders completed state correctly', (tester) async {
      final summary = IngestionSummary(
        conceptsCount: 10,
        referencesCount: 5,
        claimsCount: 2,
        filename: 'test.docx',
      );
      
      final status = IngestionStatus(
        jobId: '123',
        status: 'completed',
        progress: 100,
        stage: 'Finished',
        result: summary,
      );

      await tester.pumpWidget(createWidgetUnderTest(AsyncValue.data(status)));
      await tester.pumpAndSettle();

      expect(find.text('Ingestion Complete!'), findsOneWidget);
      expect(find.text('References: 5'), findsOneWidget);
      expect(find.text('Claims: 2'), findsOneWidget);
    });
  });
}

class MockIngestionController extends IngestionController {
  final AsyncValue<IngestionStatus?> _initialState;

  MockIngestionController(this._initialState);

  @override
  AsyncValue<IngestionStatus?> build() {
    return _initialState;
  }
}
