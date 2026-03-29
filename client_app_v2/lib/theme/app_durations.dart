/// **AppDurations**
///
/// Centralized duration tokens for all animations and timeouts across the Cognitive Quorum Flutter UI.
/// This strictly enforces the 'Enum-Style Settings Mandate' which bans magic logic numbers
/// (e.g., `const Duration(milliseconds: 300)`) floating inside widget code.
class AppDurations {
  // Private constructor to prevent instantiation
  const AppDurations._();

  // --- Animations ---

  /// Extremely fast animation (100ms) for snappy micro-interactions like clicks or hovers.
  static const Duration micro = Duration(milliseconds: 100);

  /// Fast animation (200ms) for standard UI transitions and state toggles.
  static const Duration fast = Duration(milliseconds: 200);

  /// Standard animation (300ms) for sliding panels, dialogs, and layout shifts.
  static const Duration standard = Duration(milliseconds: 300);

  /// Medium animation (500ms) for complex 2D canvas drawing and staggered list loading.
  static const Duration medium = Duration(milliseconds: 500);

  /// Slow animation (1s) for emphasizing significant state changes or success indicators.
  static const Duration slow = Duration(seconds: 1);

  /// Prolonged animation (3s) for lingering notifications or visual highlights (e.g. gauge fills).
  static const Duration display = Duration(seconds: 3);

  // --- Timeouts ---

  /// Standard API timeout (15s).
  static const Duration apiTimeout = Duration(seconds: 15);

  /// Standard cache timeout (3 minutes) for Riverpod UI Cache.
  static const Duration cacheTimeout = Duration(minutes: 3);
}
