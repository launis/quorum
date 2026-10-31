import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/theme/app_theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class _UnregisteredExtension extends ThemeExtension<_UnregisteredExtension> {
  const _UnregisteredExtension();

  @override
  _UnregisteredExtension copyWith() => const _UnregisteredExtension();

  @override
  _UnregisteredExtension lerp(
    covariant ThemeExtension<_UnregisteredExtension>? other,
    double t,
  ) => this;
}

void main() {
  group('app_theme.dart Material 3 & Theme Sovereignty Tests', () {
    testWidgets(
      'Positive: AppTheme.light and AppTheme.dark configure Material 3, brightness, and AppSemanticColors extensions',
      (WidgetTester tester) async {
        final lightTheme = AppTheme.light;
        final darkTheme = AppTheme.dark;

        expect(lightTheme.useMaterial3, isTrue);
        expect(darkTheme.useMaterial3, isTrue);

        expect(lightTheme.brightness, equals(Brightness.light));
        expect(darkTheme.brightness, equals(Brightness.dark));

        expect(lightTheme.colorScheme.brightness, equals(Brightness.light));
        expect(darkTheme.colorScheme.brightness, equals(Brightness.dark));
        expect(
          lightTheme.colorScheme.surface,
          isNot(equals(darkTheme.colorScheme.surface)),
        );

        final lightSemantics = lightTheme.extension<AppSemanticColors>();
        final darkSemantics = darkTheme.extension<AppSemanticColors>();

        expect(lightSemantics, isNotNull);
        expect(darkSemantics, isNotNull);
        expect(
          lightSemantics!.success,
          equals(AppSemanticColors.light.success),
        );
        expect(darkSemantics!.success, equals(AppSemanticColors.dark.success));
        expect(
          lightSemantics.criticalOverride,
          equals(AppSemanticColors.light.criticalOverride),
        );
        expect(
          darkSemantics.criticalOverride,
          equals(AppSemanticColors.dark.criticalOverride),
        );
      },
    );

    testWidgets(
      'Positive: AppTheme.light and AppTheme.dark enforce OutlineInputBorder InputDecorationTheme and Inter TextTheme',
      (WidgetTester tester) async {
        final lightTheme = AppTheme.light;
        final darkTheme = AppTheme.dark;

        expect(
          lightTheme.inputDecorationTheme.border,
          isA<OutlineInputBorder>(),
        );
        expect(
          darkTheme.inputDecorationTheme.border,
          isA<OutlineInputBorder>(),
        );
        expect(lightTheme.textTheme.bodyMedium, isNotNull);
        expect(darkTheme.textTheme.bodyMedium, isNotNull);
        expect(lightTheme.textTheme.bodyMedium!.fontFamily, contains('Inter'));
        expect(darkTheme.textTheme.bodyMedium!.fontFamily, contains('Inter'));
      },
    );

    testWidgets(
      'Negative/Boundary 1: Unregistered ThemeExtension lookup returns null and empty extension override strips AppSemanticColors',
      (WidgetTester tester) async {
        final lightTheme = AppTheme.light;
        final darkTheme = AppTheme.dark;

        expect(lightTheme.extension<_UnregisteredExtension>(), isNull);
        expect(darkTheme.extension<_UnregisteredExtension>(), isNull);

        final strippedTheme = lightTheme.copyWith(
          extensions: const <ThemeExtension<dynamic>>[],
        );
        expect(strippedTheme.extension<AppSemanticColors>(), isNull);
      },
    );

    testWidgets(
      'Negative/Boundary 2: MaterialApp switching between AppTheme.light and AppTheme.dark under tight 64x64 constraints renders TextField without overflow',
      (WidgetTester tester) async {
        late ThemeData activeTheme;
        late AppSemanticColors activeSemantics;

        await tester.pumpWidget(
          MaterialApp(
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.dark,
            home: Scaffold(
              body: Center(
                child: SizedBox(
                  width: 64,
                  height: 64,
                  child: Builder(
                    builder: (BuildContext context) {
                      activeTheme = Theme.of(context);
                      activeSemantics = context.semanticColors;
                      return const TextField();
                    },
                  ),
                ),
              ),
            ),
          ),
        );

        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull);
        expect(activeTheme.brightness, equals(Brightness.dark));
        expect(activeSemantics.warning, equals(AppSemanticColors.dark.warning));
      },
    );
  });
}
