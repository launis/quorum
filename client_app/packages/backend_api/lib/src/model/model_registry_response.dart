//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'model_registry_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ModelRegistryResponse {
  /// Returns a new [ModelRegistryResponse] instance.
  ModelRegistryResponse({

     this.models,
  });

      /// Nested map of provider -> strategy -> config.
  @JsonKey(
    
    name: r'models',
    required: false,
    
  )


  final Map<String, Map<String, Object>>? models;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ModelRegistryResponse &&
      other.models == models;

    @override
    int get hashCode =>
        models.hashCode;

  factory ModelRegistryResponse.fromJson(Map<String, dynamic> json) => _$ModelRegistryResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ModelRegistryResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

