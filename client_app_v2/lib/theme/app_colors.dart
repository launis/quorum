import 'package:flutter/material.dart';
import 'package:client_app/core/models/enums.dart';

class AppColors {
  static const Color intentSuccess = Colors.green;
  static const Color intentWarning = Colors.orange;
  static const Color intentCriticalOverride = Colors.red;
  static const Color intentInfo = Colors.blue;
  static const Color intentNeutral = Colors.grey;

  static Color fromIntent(VisualIntent intent) {
    switch (intent) {
      case VisualIntent.success:
        return intentSuccess;
      case VisualIntent.warning:
        return intentWarning;
      case VisualIntent.criticalOverride:
        return intentCriticalOverride;
      case VisualIntent.info:
        return intentInfo;
      case VisualIntent.neutral:
        return intentNeutral;
      case VisualIntent.error:
        return intentCriticalOverride;
    }
  }
}
