import 'package:flex_color_scheme/flex_color_scheme.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// **Application Theme Configuration**
///
/// Defines the visual identity of the application.
///
/// **Strategy**:
/// - **Base**: Material 3.
/// - **Colors**: [FlexColorScheme] with `deepPurple` (Brand DNA).
/// - **Typography**: [GoogleFonts.inter] for clean, data-dense readability.
/// - **Sub-themes**: Standardized input decorators and component styles.
class AppTheme {
  const AppTheme._();

  /// The Primary Brand Color (Deep Purple)
  /// Seed: #673AB7 (approx)
  static const FlexScheme _scheme = FlexScheme.deepPurple;

  /// **Light Theme**
  static ThemeData get light {
    return FlexThemeData.light(
      scheme: _scheme,
      useMaterial3: true,
      textTheme: GoogleFonts.interTextTheme(),
      // Add any specific sub-theme overrides here if needed
      subThemesData: const FlexSubThemesData(
        inputDecoratorBorderType: FlexInputBorderType.outline,
        inputDecoratorRadius: 8.0,
      ),
    );
  }

  /// **Dark Theme**
  static ThemeData get dark {
    return FlexThemeData.dark(
      scheme: _scheme,
      useMaterial3: true,
      textTheme: GoogleFonts.interTextTheme(),
      // Add any specific sub-theme overrides here if needed
      subThemesData: const FlexSubThemesData(
        inputDecoratorBorderType: FlexInputBorderType.outline,
        inputDecoratorRadius: 8.0,
      ),
    );
  }
}
