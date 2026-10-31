import 'dart:async';
import 'package:client_app/core/error/app_exception.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

extension CacheExtension on Ref {
  /// Delays the disposal of an autoDispose provider for a specific duration.
  /// If the provider is listened to again before the duration expires,
  /// the disposal is cancelled and the state is preserved.
  /// Ideal for forms (Time-To-Live cache).
  void cacheFor(Duration duration) {
    if (duration.isNegative) {
      throw AppException.validation(
        'Fail-Fast: cacheFor duration cannot be negative ($duration).',
      );
    }

    Timer? timer;
    final link = keepAlive();

    onDispose(() {
      timer?.cancel();
    });

    onCancel(() {
      timer?.cancel();
      timer = Timer(duration, link.close);
    });

    onResume(() {
      timer?.cancel();
    });
  }
}
