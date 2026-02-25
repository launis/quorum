// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'system_settings.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SystemSettingsCWProxy {
  SystemSettings maintenanceMode(bool? maintenanceMode);

  SystemSettings allowSignups(bool? allowSignups);

  SystemSettings globalBanner(String? globalBanner);

  SystemSettings defaultModelStrategy(String? defaultModelStrategy);

  SystemSettings enableBetaFeatures(bool? enableBetaFeatures);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SystemSettings(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SystemSettings(...).copyWith(id: 12, name: "My name")
  /// ````
  SystemSettings call({
    bool? maintenanceMode,
    bool? allowSignups,
    String? globalBanner,
    String? defaultModelStrategy,
    bool? enableBetaFeatures,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSystemSettings.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSystemSettings.copyWith.fieldName(...)`
class _$SystemSettingsCWProxyImpl implements _$SystemSettingsCWProxy {
  const _$SystemSettingsCWProxyImpl(this._value);

  final SystemSettings _value;

  @override
  SystemSettings maintenanceMode(bool? maintenanceMode) =>
      this(maintenanceMode: maintenanceMode);

  @override
  SystemSettings allowSignups(bool? allowSignups) =>
      this(allowSignups: allowSignups);

  @override
  SystemSettings globalBanner(String? globalBanner) =>
      this(globalBanner: globalBanner);

  @override
  SystemSettings defaultModelStrategy(String? defaultModelStrategy) =>
      this(defaultModelStrategy: defaultModelStrategy);

  @override
  SystemSettings enableBetaFeatures(bool? enableBetaFeatures) =>
      this(enableBetaFeatures: enableBetaFeatures);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SystemSettings(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SystemSettings(...).copyWith(id: 12, name: "My name")
  /// ````
  SystemSettings call({
    Object? maintenanceMode = const $CopyWithPlaceholder(),
    Object? allowSignups = const $CopyWithPlaceholder(),
    Object? globalBanner = const $CopyWithPlaceholder(),
    Object? defaultModelStrategy = const $CopyWithPlaceholder(),
    Object? enableBetaFeatures = const $CopyWithPlaceholder(),
  }) {
    return SystemSettings(
      maintenanceMode: maintenanceMode == const $CopyWithPlaceholder()
          ? _value.maintenanceMode
          // ignore: cast_nullable_to_non_nullable
          : maintenanceMode as bool?,
      allowSignups: allowSignups == const $CopyWithPlaceholder()
          ? _value.allowSignups
          // ignore: cast_nullable_to_non_nullable
          : allowSignups as bool?,
      globalBanner: globalBanner == const $CopyWithPlaceholder()
          ? _value.globalBanner
          // ignore: cast_nullable_to_non_nullable
          : globalBanner as String?,
      defaultModelStrategy: defaultModelStrategy == const $CopyWithPlaceholder()
          ? _value.defaultModelStrategy
          // ignore: cast_nullable_to_non_nullable
          : defaultModelStrategy as String?,
      enableBetaFeatures: enableBetaFeatures == const $CopyWithPlaceholder()
          ? _value.enableBetaFeatures
          // ignore: cast_nullable_to_non_nullable
          : enableBetaFeatures as bool?,
    );
  }
}

extension $SystemSettingsCopyWith on SystemSettings {
  /// Returns a callable class that can be used as follows: `instanceOfSystemSettings.copyWith(...)` or like so:`instanceOfSystemSettings.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SystemSettingsCWProxy get copyWith => _$SystemSettingsCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SystemSettings _$SystemSettingsFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SystemSettings',
      json,
      ($checkedConvert) {
        final val = SystemSettings(
          maintenanceMode: $checkedConvert(
            'maintenance_mode',
            (v) => v as bool? ?? false,
          ),
          allowSignups: $checkedConvert(
            'allow_signups',
            (v) => v as bool? ?? true,
          ),
          globalBanner: $checkedConvert('global_banner', (v) => v as String?),
          defaultModelStrategy: $checkedConvert(
            'default_model_strategy',
            (v) => v as String? ?? 'fast',
          ),
          enableBetaFeatures: $checkedConvert(
            'enable_beta_features',
            (v) => v as bool? ?? false,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'maintenanceMode': 'maintenance_mode',
        'allowSignups': 'allow_signups',
        'globalBanner': 'global_banner',
        'defaultModelStrategy': 'default_model_strategy',
        'enableBetaFeatures': 'enable_beta_features',
      },
    );

Map<String, dynamic> _$SystemSettingsToJson(SystemSettings instance) =>
    <String, dynamic>{
      'maintenance_mode': ?instance.maintenanceMode,
      'allow_signups': ?instance.allowSignups,
      'global_banner': ?instance.globalBanner,
      'default_model_strategy': ?instance.defaultModelStrategy,
      'enable_beta_features': ?instance.enableBetaFeatures,
    };
