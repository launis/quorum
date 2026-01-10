// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'locale_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Locale Provider**
///
/// Manages the application's [Locale] (en, fi).
/// Persists the user's preference using [SharedPreferences].

@ProviderFor(LocaleNotifier)
final localeProvider = LocaleNotifierProvider._();

/// **Locale Provider**
///
/// Manages the application's [Locale] (en, fi).
/// Persists the user's preference using [SharedPreferences].
final class LocaleNotifierProvider
    extends $NotifierProvider<LocaleNotifier, Locale> {
  /// **Locale Provider**
  ///
  /// Manages the application's [Locale] (en, fi).
  /// Persists the user's preference using [SharedPreferences].
  LocaleNotifierProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'localeProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$localeNotifierHash();

  @$internal
  @override
  LocaleNotifier create() => LocaleNotifier();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Locale value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Locale>(value),
    );
  }
}

String _$localeNotifierHash() => r'52a55830da559cb7bde676f25997f3252305c93c';

/// **Locale Provider**
///
/// Manages the application's [Locale] (en, fi).
/// Persists the user's preference using [SharedPreferences].

abstract class _$LocaleNotifier extends $Notifier<Locale> {
  Locale build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<Locale, Locale>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<Locale, Locale>,
              Locale,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
