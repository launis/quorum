import 'dart:isolate';
import 'package:flutter/foundation.dart';

/// Offload heavy synchronous computations to a background isolate on native
/// desktop targets while preserving single-threaded event loop compatibility
/// and consistent Future error propagation on web targets.
Future<R> safeIsolateRun<R>(R Function() computation) {
  if (kIsWeb) {
    return Future.sync(computation);
  }
  return Isolate.run(computation);
}
