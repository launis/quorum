//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'dimension_delete_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class DimensionDeleteResponse {
  /// Returns a new [DimensionDeleteResponse] instance.
  DimensionDeleteResponse({

    required  this.status,

    required  this.id,
  });

  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'id',
    required: true,
    
  )


  final String id;





    @override
    bool operator ==(Object other) => identical(this, other) || other is DimensionDeleteResponse &&
      other.status == status &&
      other.id == id;

    @override
    int get hashCode =>
        status.hashCode +
        id.hashCode;

  factory DimensionDeleteResponse.fromJson(Map<String, dynamic> json) => _$DimensionDeleteResponseFromJson(json);

  Map<String, dynamic> toJson() => _$DimensionDeleteResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

