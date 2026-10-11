import 'package:client_app/core/models/enums.dart';
import 'package:flutter/material.dart';

/// Semantic intent color tokens adhering to Material 3 and Theme Sovereignty.
@immutable
class AppSemanticColors extends ThemeExtension<AppSemanticColors> {
  const AppSemanticColors({
    required this.success,
    required this.warning,
    required this.criticalOverride,
    required this.info,
    required this.neutral,
  });

  final Color success;
  final Color warning;
  final Color criticalOverride;
  final Color info;
  final Color neutral;

  /// Semantic palette tuned for Light surfaces (WCAG AA >= 4.5:1).
  static const light = AppSemanticColors(
    success: Color(0xFF2E7D32),
    warning: Color(0xFFEF6C00),
    criticalOverride: Color(0xFFC62828),
    info: Color(0xFF1565C0),
    neutral: Color(0xFF616161),
  );

  /// Semantic palette tuned for Dark surface containers (WCAG AA >= 4.5:1).
  static const dark = AppSemanticColors(
    success: Color(0xFF81C784),
    warning: Color(0xFFFFB74D),
    criticalOverride: Color(0xFFE57373),
    info: Color(0xFF64B5F6),
    neutral: Color(0xFFBDBDBD),
  );

  @override
  AppSemanticColors copyWith({
    Color? success,
    Color? warning,
    Color? criticalOverride,
    Color? info,
    Color? neutral,
  }) {
    return AppSemanticColors(
      success: success ?? this.success,
      warning: warning ?? this.warning,
      criticalOverride: criticalOverride ?? this.criticalOverride,
      info: info ?? this.info,
      neutral: neutral ?? this.neutral,
    );
  }

  @override
  AppSemanticColors lerp(ThemeExtension<AppSemanticColors>? other, double t) {
    if (other is! AppSemanticColors) {
      return this;
    }
    return AppSemanticColors(
      success: Color.lerp(success, other.success, t) ?? success,
      warning: Color.lerp(warning, other.warning, t) ?? warning,
      criticalOverride:
          Color.lerp(criticalOverride, other.criticalOverride, t) ??
          criticalOverride,
      info: Color.lerp(info, other.info, t) ?? info,
      neutral: Color.lerp(neutral, other.neutral, t) ?? neutral,
    );
  }
}

/// Static mapper resolving semantic VisualIntent via the active ColorScheme.
class AppColors {
  const AppColors._();

  static Color fromIntent(VisualIntent intent, ColorScheme colorScheme) {
    switch (intent) {
      case VisualIntent.success:
        return colorScheme.primary;
      case VisualIntent.warning:
        return colorScheme.errorContainer;
      case VisualIntent.criticalOverride:
      case VisualIntent.error:
        return colorScheme.error;
      case VisualIntent.info:
        return colorScheme.secondary;
      case VisualIntent.neutral:
        return colorScheme.outline;
    }
  }
}

/// Extension on BuildContext providing direct ergonomic access to theme tokens.
extension ThemeContextExtension on BuildContext {
  ThemeData get theme => Theme.of(this);
  ColorScheme get colorScheme => Theme.of(this).colorScheme;
  TextTheme get textTheme => Theme.of(this).textTheme;
  AppSemanticColors get semanticColors =>
      Theme.of(this).extension<AppSemanticColors>() ?? AppSemanticColors.light;
}
