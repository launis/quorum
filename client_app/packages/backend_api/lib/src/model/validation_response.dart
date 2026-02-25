//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'validation_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ValidationResponse {
  /// Returns a new [ValidationResponse] instance.
  ValidationResponse({

    required  this.valid,

     this.reason,
  });

      /// Whether the connection is valid.
  @JsonKey(
    
    name: r'valid',
    required: true,
    
  )


  final bool valid;



  @JsonKey(
    
    name: r'reason',
    required: false,
    
  )


  final String? reason;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ValidationResponse &&
      other.valid == valid &&
      other.reason == reason;

    @override
    int get hashCode =>
        valid.hashCode +
        (reason == null ? 0 : reason.hashCode);

  factory ValidationResponse.fromJson(Map<String, dynamic> json) => _$ValidationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ValidationResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

