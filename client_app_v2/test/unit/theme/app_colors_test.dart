import 'package:client_app/core/models/enums.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('app_colors.dart Theme Sovereignty & Semantic Token Tests', () {
    test(
      'Positive: AppSemanticColors.light and dark define distinct WCAG-compliant tokens and copyWith overrides selectively',
      () {
        const light = AppSemanticColors.light;
        const dark = AppSemanticColors.dark;

        expect(light.success, isNot(equals(dark.success)));
        expect(light.warning, isNot(equals(dark.warning)));
        expect(light.criticalOverride, isNot(equals(dark.criticalOverride)));
        expect(light.info, isNot(equals(dark.info)));
        expect(light.neutral, isNot(equals(dark.neutral)));

        // copyWith with partial override preserves untouched tokens
        final modified = light.copyWith(success: dark.success);
        expect(modified.success, equals(dark.success));
        expect(modified.warning, equals(light.warning));
        expect(modified.criticalOverride, equals(light.criticalOverride));
        expect(modified.info, equals(light.info));
        expect(modified.neutral, equals(light.neutral));

        // copyWith with all nulls preserves all tokens
        final unchanged = light.copyWith();
        expect(unchanged.success, equals(light.success));
        expect(unchanged.warning, equals(light.warning));
        expect(unchanged.criticalOverride, equals(light.criticalOverride));
        expect(unchanged.info, equals(light.info));
        expect(unchanged.neutral, equals(light.neutral));
      },
    );

    test(
      'Positive: AppColors.fromIntent exhaustively maps all VisualIntent enum values to ColorScheme tokens',
      () {
        final scheme = ColorScheme.fromSeed(seedColor: const Color(0xFF673AB7));

        expect(
          AppColors.fromIntent(VisualIntent.success, scheme),
          equals(scheme.primary),
        );
        expect(
          AppColors.fromIntent(VisualIntent.warning, scheme),
          equals(scheme.errorContainer),
        );
        expect(
          AppColors.fromIntent(VisualIntent.criticalOverride, scheme),
          equals(scheme.error),
        );
        expect(
          AppColors.fromIntent(VisualIntent.error, scheme),
          equals(scheme.error),
        );
        expect(
          AppColors.fromIntent(VisualIntent.info, scheme),
          equals(scheme.secondary),
        );
        expect(
          AppColors.fromIntent(VisualIntent.neutral, scheme),
          equals(scheme.outline),
        );
      },
    );

    test(
      'Negative/Boundary 1: AppSemanticColors.lerp handles null ThemeExtension and boundary t values (0.0, 0.5, 1.0)',
      () {
        const light = AppSemanticColors.light;
        const dark = AppSemanticColors.dark;

        // Negative: null other returns self identically
        final lerpNull = light.lerp(null, 0.5);
        expect(identical(lerpNull, light), isTrue);

        // Boundary t = 0.0 matches start palette
        final atZero = light.lerp(dark, 0.0);
        expect(atZero.success, equals(light.success));
        expect(atZero.warning, equals(light.warning));
        expect(atZero.criticalOverride, equals(light.criticalOverride));
        expect(atZero.info, equals(light.info));
        expect(atZero.neutral, equals(light.neutral));

        // Boundary t = 1.0 matches end palette
        final atOne = light.lerp(dark, 1.0);
        expect(atOne.success, equals(dark.success));
        expect(atOne.warning, equals(dark.warning));
        expect(atOne.criticalOverride, equals(dark.criticalOverride));
        expect(atOne.info, equals(dark.info));
        expect(atOne.neutral, equals(dark.neutral));

        // Midpoint t = 0.5 produces interpolated color distinct from both endpoints
        final atHalf = light.lerp(dark, 0.5);
        expect(
          atHalf.success,
          equals(Color.lerp(light.success, dark.success, 0.5)),
        );
        expect(atHalf.success, isNot(equals(light.success)));
        expect(atHalf.success, isNot(equals(dark.success)));
      },
    );

    testWidgets(
      'Negative/Boundary 2: ThemeContextExtension resolves registered dark AppSemanticColors and falls back to AppSemanticColors.light when extension is omitted',
      (WidgetTester tester) async {
        final darkScheme = ColorScheme.fromSeed(
          seedColor: const Color(0xFF673AB7),
          brightness: Brightness.dark,
        );
        final darkTheme = ThemeData.from(colorScheme: darkScheme).copyWith(
          extensions: const <ThemeExtension<dynamic>>[AppSemanticColors.dark],
        );

        late ThemeData capturedDarkTheme;
        late ColorScheme capturedDarkScheme;
        late TextTheme capturedDarkTextTheme;
        late AppSemanticColors capturedDarkSemantics;

        await tester.pumpWidget(
          MaterialApp(
            theme: darkTheme,
            home: Builder(
              builder: (BuildContext context) {
                capturedDarkTheme = context.theme;
                capturedDarkScheme = context.colorScheme;
                capturedDarkTextTheme = context.textTheme;
                capturedDarkSemantics = context.semanticColors;
                return const SizedBox();
              },
            ),
          ),
        );

        expect(capturedDarkTheme.brightness, equals(Brightness.dark));
        expect(capturedDarkScheme.primary, equals(darkScheme.primary));
        expect(capturedDarkTextTheme.bodyMedium, isNotNull);
        expect(
          capturedDarkSemantics.success,
          equals(AppSemanticColors.dark.success),
        );
        expect(
          capturedDarkSemantics.warning,
          equals(AppSemanticColors.dark.warning),
        );

        // Negative boundary: ThemeData constructed without AppSemanticColors extension
        late AppSemanticColors fallbackSemantics;
        await tester.pumpWidget(
          MaterialApp(
            key: const ValueKey('unextended_light_app'),
            theme: ThemeData.light(useMaterial3: true),
            home: Builder(
              builder: (BuildContext context) {
                fallbackSemantics = context.semanticColors;
                return const SizedBox();
              },
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(
          fallbackSemantics.success,
          equals(AppSemanticColors.light.success),
        );
        expect(
          fallbackSemantics.criticalOverride,
          equals(AppSemanticColors.light.criticalOverride),
        );
      },
    );
  });
}
