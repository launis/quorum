//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'system_settings.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class SystemSettings {
  /// Returns a new [SystemSettings] instance.
  SystemSettings({

     this.maintenanceMode = false,

     this.allowSignups = true,

     this.globalBanner,

     this.defaultModelStrategy = 'fast',

     this.enableBetaFeatures = false,
  });

      /// If True, only ROOT can login/act.
  @JsonKey(
    defaultValue: false,
    name: r'maintenance_mode',
    required: false,
    
  )


  final bool? maintenanceMode;



      /// If True, new users can register.
  @JsonKey(
    defaultValue: true,
    name: r'allow_signups',
    required: false,
    
  )


  final bool? allowSignups;



  @JsonKey(
    
    name: r'global_banner',
    required: false,
    
  )


  final String? globalBanner;



      /// Default LLM strategy for new agents.
  @JsonKey(
    defaultValue: 'fast',
    name: r'default_model_strategy',
    required: false,
    
  )


  final String? defaultModelStrategy;



      /// Toggle experimental features.
  @JsonKey(
    defaultValue: false,
    name: r'enable_beta_features',
    required: false,
    
  )


  final bool? enableBetaFeatures;





    @override
    bool operator ==(Object other) => identical(this, other) || other is SystemSettings &&
      other.maintenanceMode == maintenanceMode &&
      other.allowSignups == allowSignups &&
      other.globalBanner == globalBanner &&
      other.defaultModelStrategy == defaultModelStrategy &&
      other.enableBetaFeatures == enableBetaFeatures;

    @override
    int get hashCode =>
        maintenanceMode.hashCode +
        allowSignups.hashCode +
        (globalBanner == null ? 0 : globalBanner.hashCode) +
        defaultModelStrategy.hashCode +
        enableBetaFeatures.hashCode;

  factory SystemSettings.fromJson(Map<String, dynamic> json) => _$SystemSettingsFromJson(json);

  Map<String, dynamic> toJson() => _$SystemSettingsToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

