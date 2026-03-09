import 'dart:io';
import 'package:dio/dio.dart';

/// **Target Locale Interceptor**
///
/// Ensures every outgoing HTTP request includes the device's current locale.
/// This fulfills the V2 Architecture "I18n Fallback" requirement by allowing
/// the backend to default to the user's language if translations are missing.
class TargetLocaleInterceptor extends Interceptor {
  TargetLocaleInterceptor();

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // 1. Get system locale (e.g., 'en_US', 'fi_FI')
    // For V2 we only need the primary language code (e.g., 'en', 'fi')
    final String localeName = Platform.localeName;
    final String languageCode = localeName.split('_').first;

    // 2. Attach to headers
    options.headers['Accept-Language'] = languageCode;

    // Optionally also as a custom header for explicit backend routing
    options.headers['X-Target-Locale'] = languageCode;

    super.onRequest(options, handler);
  }
}
