import 'package:flex_color_scheme/flex_color_scheme.dart';
import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get light {
    return FlexThemeData.light(
      colors: const FlexSchemeColor(
        primary: Colors.deepPurple,
        primaryContainer: Color(0xFFD0BCFF),
        secondary: Colors.deepPurpleAccent,
        secondaryContainer: Color(0xFFE8DEF8),
      ),

      visualDensity: FlexColorScheme.comfortablePlatformDensity,
    );
  }

  static ThemeData get dark {
    return FlexThemeData.dark(
      colors: const FlexSchemeColor(
        primary: Colors.deepPurple,
        primaryContainer: Color(0xFF381E72),
        secondary: Colors.deepPurpleAccent,
        secondaryContainer: Color(0xFF1D192B),
      ),

      visualDensity: FlexColorScheme.comfortablePlatformDensity,
    );
  }
}
