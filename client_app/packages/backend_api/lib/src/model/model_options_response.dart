//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'model_options_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ModelOptionsResponse {
  /// Returns a new [ModelOptionsResponse] instance.
  ModelOptionsResponse({

    required  this.options,
  });

  @JsonKey(
    
    name: r'options',
    required: true,
    
  )


  final Map<String, List<String>> options;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ModelOptionsResponse &&
      other.options == options;

    @override
    int get hashCode =>
        options.hashCode;

  factory ModelOptionsResponse.fromJson(Map<String, dynamic> json) => _$ModelOptionsResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ModelOptionsResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

