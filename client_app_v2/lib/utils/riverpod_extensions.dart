import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';

extension CacheExtension on Ref {
  /// Delays the disposal of an autoDispose provider for a specific duration.
  /// If the provider is listened to again before the duration expires,
  /// the disposal is cancelled and the state is preserved.
  /// Ideal for forms (Time-To-Live cache).
  void cacheFor(Duration duration) {
    Timer? timer;
    final link = keepAlive();

    onDispose(() {
      timer?.cancel();
    });

    onCancel(() {
      timer = Timer(duration, link.close);
    });

    onResume(() {
      timer?.cancel();
    });
  }
}
