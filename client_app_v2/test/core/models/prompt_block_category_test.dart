import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/prompt_block_category.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

void main() {
  group('PromptBlockCategory', () {
    test(
      'roundtrips all canonical backend PromptBlockCategory IDs deterministically',
      () {
        const expectedIds = <PromptBlockCategory, String>{
          PromptBlockCategory.matrix: 'matrix',
          PromptBlockCategory.agentRole: 'agent_role',
          PromptBlockCategory.systemRule: 'system_rule',
          PromptBlockCategory.protocol: 'protocol',
          PromptBlockCategory.runtimeVariables: 'runtime_variables',
          PromptBlockCategory.executionPersona: 'execution_persona',
        };

        expect(PromptBlockCategory.values.length, expectedIds.length);
        for (final entry in expectedIds.entries) {
          expect(entry.key.id, entry.value);
          expect(PromptBlockCategory.fromId(entry.value), entry.key);
        }
      },
    );

    test(
      'throws AppException validation error when category ID is empty or unknown',
      () {
        expect(
          () => PromptBlockCategory.fromId(''),
          throwsA(
            isA<AppException>()
                .having((e) => e.status, 'status', 400)
                .having((e) => e.errorCode, 'errorCode', 'VALIDATION_FAILED'),
          ),
        );

        expect(
          () => PromptBlockCategory.fromId('unknown_category'),
          throwsA(
            isA<AppException>()
                .having((e) => e.status, 'status', 400)
                .having(
                  (e) => e.detail,
                  'detail',
                  contains('Unknown PromptBlockCategory: unknown_category'),
                ),
          ),
        );
      },
    );

    test(
      'throws AppException validation error on case-mismatched or whitespace boundary IDs',
      () {
        expect(
          () => PromptBlockCategory.fromId('MATRIX'),
          throwsA(isA<AppException>()),
        );
        expect(
          () => PromptBlockCategory.fromId(' matrix '),
          throwsA(isA<AppException>()),
        );
      },
    );

    testWidgets(
      'resolves localized displayName for all categories when AppLocalizations is present',
      (tester) async {
        late BuildContext capturedContext;
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            locale: const Locale('en'),
            home: Builder(
              builder: (context) {
                capturedContext = context;
                return const SizedBox();
              },
            ),
          ),
        );

        for (final category in PromptBlockCategory.values) {
          final label = category.displayName(capturedContext);
          expect(label.trim(), isNotEmpty);
        }
      },
    );

    testWidgets(
      'throws AppException validation error when AppLocalizations is missing from BuildContext',
      (tester) async {
        late BuildContext unlocalizedContext;
        await tester.pumpWidget(
          Directionality(
            textDirection: TextDirection.ltr,
            child: Builder(
              builder: (context) {
                unlocalizedContext = context;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(
          () => PromptBlockCategory.matrix.displayName(unlocalizedContext),
          throwsA(
            isA<AppException>()
                .having((e) => e.status, 'status', 400)
                .having((e) => e.errorCode, 'errorCode', 'VALIDATION_FAILED'),
          ),
        );
      },
    );
  });
}
