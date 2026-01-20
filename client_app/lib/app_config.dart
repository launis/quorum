
import 'package:flutter/foundation.dart';

class AppConfig {
  static const String _localUrl = 'http://localhost:8000';
  static const String _androidUrl = 'http://10.0.2.2:8000';
  static const String _productionUrl = 'https://api.quorum.com'; // Placeholder

  static String get apiBaseUrl {
    if (kReleaseMode) {
      return _productionUrl;
    }
    // Simple logic for emulator vs web/desktop
    if (defaultTargetPlatform == TargetPlatform.android) {
        return _androidUrl;
    }
    return _localUrl;
  }
}
