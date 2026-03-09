/// **SafeCast Utility**
///
/// Defensive parsing utility ensuring the Flutter frontend does not crash
/// when encountering unexpected types from dynamic JSON or LLM outputs.
///
/// This is a strict requirement for the V2 Zero-Codegen SDUI architecture,
/// acting as the safety net for un-typed `Map<String, dynamic>` structures.
class SafeCast {
  /// Safely extracts a double from any dynamic value.
  /// Handles int gracefully, tries to parse Strings.
  static double safeDouble(dynamic value, [double defaultValue = 0.0]) {
    if (value == null) return defaultValue;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  /// Safely extracts an int from any dynamic value.
  /// Parses Strings, truncates doubles to int.
  static int safeInt(dynamic value, [int defaultValue = 0]) {
    if (value == null) return defaultValue;
    if (value is int) return value;
    if (value is double) return value.toInt();
    if (value is String) {
      final parsedDouble = double.tryParse(value);
      if (parsedDouble != null) return parsedDouble.toInt();
    }
    return defaultValue;
  }

  /// Safely extracts a String from any dynamic value.
  static String safeString(dynamic value, [String defaultValue = '']) {
    if (value == null) return defaultValue;
    if (value is String) return value;
    return value.toString();
  }

  /// Safely extracts a boolean from any dynamic value.
  /// Handles "true", "1", 1, true.
  static bool safeBool(dynamic value, [bool defaultValue = false]) {
    if (value == null) return defaultValue;
    if (value is bool) return value;
    if (value is int) return value > 0;
    if (value is String) {
      final str = value.trim().toLowerCase();
      if (str == 'true' || str == '1') return true;
      if (str == 'false' || str == '0') return false;
    }
    return defaultValue;
  }

  /// Safely extracts a Map from any dynamic value.
  static Map<String, dynamic> safeMap(
    dynamic value, [
    Map<String, dynamic>? defaultValue,
  ]) {
    final fallback = defaultValue ?? <String, dynamic>{};
    if (value == null) return fallback;
    if (value is Map<String, dynamic>) return value;
    if (value is Map) {
      try {
        return Map<String, dynamic>.from(value);
      } catch (_) {
        return fallback;
      }
    }
    return fallback;
  }

  /// Safely extracts a List from any dynamic value.
  static List<T> safeList<T>(dynamic value, [List<T>? defaultValue]) {
    final fallback = defaultValue ?? <T>[];
    if (value == null) return fallback;
    if (value is List<T>) return value;
    if (value is List) {
      try {
        return List<T>.from(value);
      } catch (_) {
        return fallback;
      }
    }
    return fallback;
  }
}
