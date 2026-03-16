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

  /// Safely extracts a DateTime from any dynamic value.
  /// Handles valid ISO 8601 strings and milliseconds since epoch.
  static DateTime? safeDateTime(dynamic value) {
    if (value == null) return null;
    if (value is DateTime) return value;
    if (value is String) {
      return DateTime.tryParse(value);
    }
    if (value is int) {
      // Assuming it could be milliseconds since epoch from JSON
      try {
        return DateTime.fromMillisecondsSinceEpoch(value);
      } catch (_) {
        return null;
      }
    }
    return null;
  }

  /// Safely converts a String value to an Enum.
  /// Returns the provided default value if parsing fails or value is missing.
  static T safeEnum<T extends Enum>(
    dynamic value,
    Iterable<T> values,
    T defaultValue,
  ) {
    if (value == null) return defaultValue;
    if (value is T) return value;
    final strValue = value.toString().toLowerCase();

    try {
      return values.firstWhere(
        (e) => e.name.toLowerCase() == strValue,
        orElse: () => defaultValue,
      );
    } catch (_) {
      return defaultValue;
    }
  }

  /// Recursively deep copies a Map<String, dynamic>.
  /// Essential for Riverpod state immutability when dealing with dynamic SDUI forms,
  /// preventing unintended mutations of cached states via nested map references.
  static Map<String, dynamic> safeDeepCopyMap(Map<String, dynamic>? source) {
    if (source == null) return <String, dynamic>{};

    final copy = <String, dynamic>{};
    for (final entry in source.entries) {
      if (entry.value is Map<String, dynamic>) {
        copy[entry.key] = safeDeepCopyMap(entry.value as Map<String, dynamic>);
      } else if (entry.value is Map) {
        // Handle untyped maps safely
        try {
          copy[entry.key] = safeDeepCopyMap(
            Map<String, dynamic>.from(entry.value as Map),
          );
        } catch (_) {
          copy[entry.key] = entry.value;
        }
      } else if (entry.value is List) {
        // Deep copy lists to prevent nested reference mutations inside lists
        copy[entry.key] = List.from(entry.value as List);
      } else {
        copy[entry.key] = entry.value;
      }
    }
    return copy;
  }
}
