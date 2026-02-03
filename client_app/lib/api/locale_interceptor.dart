import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/settings/locale_provider.dart';

/// **Locale Interceptor**
///
/// Injects the `Accept-Language` header into every request based on the
/// current application locale. This decouples [ApiClient] from [LocaleNotifier],
/// preventing circular dependencies.
class LocaleInterceptor extends Interceptor {
  final Ref _ref;

  LocaleInterceptor(this._ref);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    try {
      // Read current locale (non-reactive)
      final locale = _ref.read(localeProvider);
      options.headers['Accept-Language'] = locale.languageCode;
    } catch (_) {
      // Fallback if provider is not ready
      options.headers['Accept-Language'] = 'en';
    }
    handler.next(options);
  }
}
