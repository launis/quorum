import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/controllers/prompt_blocks_controller.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/views/matrix_editor_view.dart';
import 'package:client_app/features/studio/views/prompt_block_builder_view.dart';
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
    String? id,
    required Future<PromptBlock> Function(String id) onFetchBlock,
    Locale locale = const Locale('en'),
  }) {
    return ProviderScope(
      overrides: [
        loggerServiceProvider.overrideWithValue(mockLogger),
        promptBlockByIdProvider.overrideWith(
          (ref, requestedId) => onFetchBlock(requestedId),
        ),
      ],
      child: MaterialApp(
        theme: AppTheme.light,
        locale: locale,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        home: MatrixEditorView(id: id),
      ),
    );
  }

  group('MatrixEditorView Widget & Hardening Tests', () {
    testWidgets(
      'Positive (Create Matrix Routing): routes null, empty, whitespace, or "new" id to PromptBlockBuilderView with id="new" and slug="create-matrix"',
      (WidgetTester tester) async {
        final requestedIds = <String>[];

        for (final candidateId in <String?>[null, '', '   ', 'new']) {
          await tester.pumpWidget(
            createSubject(
              id: candidateId,
              onFetchBlock: (requestedId) async {
                requestedIds.add(requestedId);
                throw const AppException(
                  detail: 'Simulated test boundary halt',
                  status: 404,
                );
              },
            ),
          );
          await tester.pumpAndSettle();

          final builderView = tester.widget<PromptBlockBuilderView>(
            find.byType(PromptBlockBuilderView),
          );
          expect(builderView.id, equals('new'));
          expect(builderView.slug, equals('create-matrix'));
        }

        expect(requestedIds, everyElement(equals('new')));
      },
    );

    testWidgets(
      'Positive (Edit Matrix Routing): routes existing matrix ID to PromptBlockBuilderView with trimmed id and slug="edit-matrix"',
      (WidgetTester tester) async {
        const targetId = 'blk_0195f000000070008000000000000001';
        String? capturedProviderId;

        await tester.pumpWidget(
          createSubject(
            id: '  $targetId  ',
            onFetchBlock: (requestedId) async {
              capturedProviderId = requestedId;
              throw const AppException(
                detail: 'Simulated test boundary halt',
                status: 404,
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        final builderView = tester.widget<PromptBlockBuilderView>(
          find.byType(PromptBlockBuilderView),
        );
        expect(builderView.id, equals(targetId));
        expect(builderView.slug, equals('edit-matrix'));
        expect(capturedProviderId, equals(targetId));
      },
    );

    testWidgets(
      'Negative 1 (ISTQB BVA / Missing Entity 404 Fail-Fast): propagates backend AppException into ErrorView diagnostic state',
      (WidgetTester tester) async {
        const missingId = 'blk_0195f000000070008000000000000404';
        String? requestedEntityId;

        await tester.pumpWidget(
          createSubject(
            id: missingId,
            onFetchBlock: (requestedId) async {
              requestedEntityId = requestedId;
              throw const AppException(
                detail: 'Matrix block not found',
                status: 404,
                extensions: <String, Object?>{'error_code': 'ENTITY_NOT_FOUND'},
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(requestedEntityId, equals(missingId));
        expect(find.byType(ErrorView), findsOneWidget);

        final errorView = tester.widget<ErrorView>(find.byType(ErrorView));
        expect(errorView.error, isA<AppException>());
        expect((errorView.error as AppException).status, equals(404));
        expect(errorView.onRetry, isNotNull);
      },
    );

    testWidgets(
      'Negative 2 (ISTQB BVA / Narrow Viewport & Finnish Localization Boundary): renders ErrorView in Finnish locale without horizontal overflow at 320px width',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(320, 600);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(() {
          tester.view.resetPhysicalSize();
          tester.view.resetDevicePixelRatio();
        });

        await tester.pumpWidget(
          createSubject(
            id: 'new',
            locale: const Locale('fi'),
            onFetchBlock: (_) async {
              throw AppException.validation(
                'Fail-Fast: Matrix configuration schema error',
              );
            },
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        final BuildContext context = tester.element(
          find.byType(PromptBlockBuilderView),
        );
        final l10n = AppLocalizations.of(context)!;

        expect(find.text(l10n.promptBlockEditTitle), findsOneWidget);
        expect(find.byType(ErrorView), findsOneWidget);
      },
    );
  });
}
