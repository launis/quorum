import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CacheExtension.cacheFor Tests', () {
    test(
      'Positive: retains autoDispose provider state during TTL window and cancels timer upon listener resume',
      () async {
        var buildCount = 0;
        var disposedCount = 0;

        final cachedProvider = Provider.autoDispose<int>((ref) {
          ref.cacheFor(const Duration(milliseconds: 60));
          ref.onDispose(() {
            disposedCount++;
          });
          return ++buildCount;
        });

        final container = ProviderContainer();
        addTearDown(container.dispose);

        final sub1 = container.listen<int>(cachedProvider, (_, _) {});
        expect(sub1.read(), equals(1));
        expect(buildCount, equals(1));
        expect(disposedCount, equals(0));

        // Cancel listener to start the 60ms TTL countdown.
        sub1.close();
        await Future<void>.delayed(const Duration(milliseconds: 25));
        expect(disposedCount, equals(0));

        // Resume listening before TTL expires; timer must be cancelled and state preserved.
        final sub2 = container.listen<int>(cachedProvider, (_, _) {});
        expect(sub2.read(), equals(1));
        expect(buildCount, equals(1));

        // Wait past original 60ms mark while still listened to.
        await Future<void>.delayed(const Duration(milliseconds: 50));
        expect(disposedCount, equals(0));

        // Close second listener and let full 60ms TTL expire.
        sub2.close();
        await Future<void>.delayed(const Duration(milliseconds: 80));
        expect(disposedCount, equals(1));
      },
    );

    test(
      'Negative 1: throws AppException.validation (VALIDATION_FAILED) when duration is negative (min-1 boundary)',
      () {
        Object? capturedError;
        final invalidProvider = Provider.autoDispose<int>((ref) {
          try {
            ref.cacheFor(const Duration(milliseconds: -1));
          } on Object catch (e) {
            capturedError = e;
            rethrow;
          }
          return 1;
        });

        final container = ProviderContainer();
        addTearDown(container.dispose);

        expect(() => container.read(invalidProvider), throwsA(anything));
        expect(capturedError, isA<AppException>());
        expect(
          (capturedError as AppException).errorCode,
          equals('VALIDATION_FAILED'),
        );
      },
    );

    test(
      'Negative 2 / Boundary: Duration.zero expires immediately on next event loop tick and container.dispose cancels active timer cleanly',
      () async {
        var zeroDisposed = 0;
        final zeroCacheProvider = Provider.autoDispose<String>((ref) {
          ref.cacheFor(Duration.zero);
          ref.onDispose(() {
            zeroDisposed++;
          });
          return 'zero-ttl';
        });

        var longDisposed = 0;
        final longCacheProvider = Provider.autoDispose<String>((ref) {
          ref.cacheFor(const Duration(minutes: 10));
          ref.onDispose(() {
            longDisposed++;
          });
          return 'long-ttl';
        });

        final container = ProviderContainer();

        final zeroSub = container.listen<String>(zeroCacheProvider, (_, _) {});
        expect(zeroSub.read(), equals('zero-ttl'));
        zeroSub.close();

        // Duration.zero timer fires on the next event loop turn.
        await Future<void>.delayed(const Duration(milliseconds: 10));
        expect(zeroDisposed, equals(1));

        // Start long-TTL timer, then dispose container while timer is active to verify onDispose cancels timer cleanly.
        final longSub = container.listen<String>(longCacheProvider, (_, _) {});
        expect(longSub.read(), equals('long-ttl'));
        longSub.close();

        container.dispose();
        expect(longDisposed, equals(1));
      },
    );
  });
}
