//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'llm_provider_config.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class LLMProviderConfig {
  /// Returns a new [LLMProviderConfig] instance.
  LLMProviderConfig({

    required  this.id,

    required  this.provider,

    required  this.modelName,

     this.apiKey,

     this.baseUrl,

     this.temperature = 0.7,

    required  this.tpmLimit,

    required  this.rpmLimit,

     this.defaultMaxTokens,

     this.vertexLocation,

     this.supportsGrounding = false,

     this.isActive = true,

     this.additionalParams,
  });

      /// Configuration ID (unique key).
  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;



      /// Provider type (e.g. 'openai', 'vertex_ai').
  @JsonKey(
    
    name: r'provider',
    required: true,
    
  )


  final String provider;



      /// Model identifier (e.g. 'gpt-4', 'gemini-pro').
  @JsonKey(
    
    name: r'model_name',
    required: true,
    
  )


  final String modelName;



  @JsonKey(
    
    name: r'api_key',
    required: false,
    
  )


  final String? apiKey;



  @JsonKey(
    
    name: r'base_url',
    required: false,
    
  )


  final String? baseUrl;



      /// Sampling temperature.
          // minimum: 0.0
          // maximum: 2.0
  @JsonKey(
    defaultValue: 0.7,
    name: r'temperature',
    required: false,
    
  )


  final num? temperature;



      /// Tokens per minute limit. 0=unlimited.
          // minimum: 0
  @JsonKey(
    
    name: r'tpm_limit',
    required: true,
    
  )


  final int tpmLimit;



      /// Requests per minute limit. 0=unlimited.
          // minimum: 0
  @JsonKey(
    
    name: r'rpm_limit',
    required: true,
    
  )


  final int rpmLimit;



          // minimum: 1
  @JsonKey(
    
    name: r'default_max_tokens',
    required: false,
    
  )


  final int? defaultMaxTokens;



  @JsonKey(
    
    name: r'vertex_location',
    required: false,
    
  )


  final String? vertexLocation;



      /// Whether this model supports Google Search Grounding.
  @JsonKey(
    defaultValue: false,
    name: r'supports_grounding',
    required: false,
    
  )


  final bool? supportsGrounding;



      /// Whether this provider is active.
  @JsonKey(
    defaultValue: true,
    name: r'is_active',
    required: false,
    
  )


  final bool? isActive;



      /// Additional provider-specific parameters.
  @JsonKey(
    
    name: r'additional_params',
    required: false,
    
  )


  final Map<String, Object>? additionalParams;





    @override
    bool operator ==(Object other) => identical(this, other) || other is LLMProviderConfig &&
      other.id == id &&
      other.provider == provider &&
      other.modelName == modelName &&
      other.apiKey == apiKey &&
      other.baseUrl == baseUrl &&
      other.temperature == temperature &&
      other.tpmLimit == tpmLimit &&
      other.rpmLimit == rpmLimit &&
      other.defaultMaxTokens == defaultMaxTokens &&
      other.vertexLocation == vertexLocation &&
      other.supportsGrounding == supportsGrounding &&
      other.isActive == isActive &&
      other.additionalParams == additionalParams;

    @override
    int get hashCode =>
        id.hashCode +
        provider.hashCode +
        modelName.hashCode +
        (apiKey == null ? 0 : apiKey.hashCode) +
        (baseUrl == null ? 0 : baseUrl.hashCode) +
        temperature.hashCode +
        tpmLimit.hashCode +
        rpmLimit.hashCode +
        (defaultMaxTokens == null ? 0 : defaultMaxTokens.hashCode) +
        (vertexLocation == null ? 0 : vertexLocation.hashCode) +
        supportsGrounding.hashCode +
        isActive.hashCode +
        additionalParams.hashCode;

  factory LLMProviderConfig.fromJson(Map<String, dynamic> json) => _$LLMProviderConfigFromJson(json);

  Map<String, dynamic> toJson() => _$LLMProviderConfigToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

