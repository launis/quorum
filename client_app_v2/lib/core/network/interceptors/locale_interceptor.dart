import 'dart:ui';
import 'package:dio/dio.dart';

/// Attaches the current system language code to outgoing HTTP requests
/// so the backend can resolve localized content when explicit overrides are absent.
class TargetLocaleInterceptor extends Interceptor {
  final Locale Function()? _localeResolver;

  TargetLocaleInterceptor({Locale Function()? localeResolver})
    : _localeResolver = localeResolver;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final Locale activeLocale =
        _localeResolver?.call() ?? PlatformDispatcher.instance.locale;
    final String languageCode = activeLocale.languageCode;

    options.headers['Accept-Language'] = languageCode;
    options.headers['X-Target-Locale'] = languageCode;

    super.onRequest(options, handler);
  }
}
