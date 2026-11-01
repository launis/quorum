import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/schema_mapper.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  Widget buildTestHarness({
    required String key,
    required Map<String, Object?> schema,
    Object? value,
    ValueChanged<Object?>? onChanged,
    bool isRequired = false,
    GlobalKey<FormState>? formKey,
    ThemeData? theme,
    Locale locale = const Locale('en'),
    double? width,
  }) {
    return MaterialApp(
      theme: theme ?? AppTheme.light,
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: Scaffold(
        body: SingleChildScrollView(
          child: Builder(
            builder: (context) {
              final widget = SchemaMapper.mapFieldToWidget(
                context: context,
                key: key,
                schema: schema,
                value: value,
                onChanged: onChanged ?? (_) {},
                isRequired: isRequired,
              );
              final content = formKey != null
                  ? Form(key: formKey, child: widget)
                  : widget;
              return width != null
                  ? SizedBox(width: width, child: content)
                  : content;
            },
          ),
        ),
      ),
    );
  }

  group('SchemaMapper Dumb Painter & Fail-Fast Boundary Tests', () {
    testWidgets(
      'Positive: maps string, integer, number, boolean, and enum definitions to form widgets and emits typed values on change',
      (WidgetTester tester) async {
        Object? latestEmitted;

        // 1. String field
        await tester.pumpWidget(
          buildTestHarness(
            key: 'agent_role',
            schema: const <String, Object?>{
              'type': 'string',
              'title': 'Agent Role',
              'description': 'Primary persona identifier',
            },
            value: 'Falsifier',
            isRequired: true,
            onChanged: (val) => latestEmitted = val,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.text('Agent Role *'), findsOneWidget);
        expect(find.text('Primary persona identifier'), findsOneWidget);
        await tester.enterText(find.byType(TextFormField), 'Synthesizer');
        await tester.pumpAndSettle();
        expect(latestEmitted, equals('Synthesizer'));

        // 2. Integer & Number fields
        await tester.pumpWidget(
          buildTestHarness(
            key: 'max_tokens',
            schema: const <String, Object?>{
              'type': 'integer',
              'title': 'Max Tokens',
            },
            value: 1024,
            onChanged: (val) => latestEmitted = val,
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(find.byType(TextFormField), '2048');
        await tester.pumpAndSettle();
        expect(latestEmitted, equals(2048));

        await tester.enterText(find.byType(TextFormField), '');
        await tester.pumpAndSettle();
        expect(latestEmitted, isNull);

        await tester.pumpWidget(
          buildTestHarness(
            key: 'temperature',
            schema: const <String, Object?>{
              'type': 'number',
              'title': 'Temperature',
            },
            value: 0.2,
            onChanged: (val) => latestEmitted = val,
          ),
        );
        await tester.pumpAndSettle();

        await tester.enterText(find.byType(TextFormField), '0.75');
        await tester.pumpAndSettle();
        expect(latestEmitted, equals(0.75));

        // 3. Boolean field
        await tester.pumpWidget(
          buildTestHarness(
            key: 'strict_validation',
            schema: const <String, Object?>{
              'type': 'boolean',
              'title': 'Strict Validation',
              'description': 'Enforce zero-fallback parsing',
            },
            value: false,
            onChanged: (val) => latestEmitted = val,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(SwitchListTile));
        await tester.pumpAndSettle();
        expect(latestEmitted, isTrue);

        // 4. Enum dropdown field
        await tester.pumpWidget(
          buildTestHarness(
            key: 'cognitive_tier',
            schema: const <String, Object?>{
              'type': 'string',
              'title': 'Cognitive Tier',
              'enum': <Object?>['FAST', 'BALANCED', 'DEEP'],
            },
            value: 'FAST',
            onChanged: (val) => latestEmitted = val,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byType(DropdownButtonFormField<String>));
        await tester.pumpAndSettle();
        await tester.tap(find.text('DEEP').last);
        await tester.pumpAndSettle();
        expect(latestEmitted, equals('DEEP'));
      },
    );

    testWidgets(
      'Boundary 1: required field validator enforces localized AppLocalizations.fieldRequired message in Finnish and narrow 240px dark viewport renders without overflow',
      (WidgetTester tester) async {
        final formKey = GlobalKey<FormState>();
        final l10nFi = await AppLocalizations.delegate.load(const Locale('fi'));

        await tester.pumpWidget(
          buildTestHarness(
            key: 'required_enum_field',
            schema: const <String, Object?>{
              'type': 'string',
              'title':
                  'ExtraordinarilyLongEnterpriseConfigurationParameterTitleWithoutSpaces',
              'enum': <Object?>[
                'ExtraordinarilyLongEnumOptionIdentifierValueOne_2026_Final',
                'OptionTwo',
              ],
            },
            value: null,
            isRequired: true,
            formKey: formKey,
            theme: AppTheme.dark,
            locale: const Locale('fi'),
            width: 240,
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(formKey.currentState!.validate(), isFalse);
        await tester.pumpAndSettle();

        expect(find.text(l10nFi.fieldRequired), findsOneWidget);
      },
    );

    testWidgets(
      'Negative 1: empty key or unsupported/missing schema type and enum throws AppException.validation (Fail-Fast)',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Builder(
              builder: (context) {
                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: '   ',
                    schema: const <String, Object?>{'type': 'string'},
                    value: null,
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: 'untyped_field',
                    schema: const <String, Object?>{'title': 'No Type Or Enum'},
                    value: null,
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: 'invalid_type_field',
                    schema: const <String, Object?>{'type': 'unsupported_blob'},
                    value: null,
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                return const SizedBox();
              },
            ),
          ),
        );
      },
    );

    testWidgets(
      'Negative 2: malformed enum list, out-of-bounds enum value, or mismatched runtime value type throws AppException.validation without silent fallback',
      (WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            localizationsDelegates: AppLocalizations.localizationsDelegates,
            supportedLocales: AppLocalizations.supportedLocales,
            home: Builder(
              builder: (context) {
                // Empty enum list
                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: 'mode',
                    schema: const <String, Object?>{
                      'type': 'string',
                      'enum': <Object?>[],
                    },
                    value: null,
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                // Initial value not in enum options
                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: 'mode',
                    schema: const <String, Object?>{
                      'type': 'string',
                      'enum': <Object?>['A', 'B'],
                    },
                    value: 'INVALID_OPTION',
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                // Non-bool value for boolean field
                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: 'flag',
                    schema: const <String, Object?>{'type': 'boolean'},
                    value: 'not_a_boolean',
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                // Non-string value for string field
                expect(
                  () => SchemaMapper.mapFieldToWidget(
                    context: context,
                    key: 'label',
                    schema: const <String, Object?>{'type': 'string'},
                    value: 99999,
                    onChanged: (_) {},
                    isRequired: false,
                  ),
                  throwsA(isA<AppException>()),
                );

                return const SizedBox();
              },
            ),
          ),
        );
      },
    );
  });
}
