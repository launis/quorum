import 'dart:isolate';
import 'package:flutter/foundation.dart';

/// Web-safe wrapper for Isolate.run
Future<R> safeIsolateRun<R>(R Function() computation) {
  if (kIsWeb) {
    return Future.value(computation());
  }
  return Isolate.run(computation);
}
