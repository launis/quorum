//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'generic_action_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class GenericActionResponse {
  /// Returns a new [GenericActionResponse] instance.
  GenericActionResponse({

    required  this.status,

     this.id,
  });

  @JsonKey(
    
    name: r'status',
    required: true,
    
  )


  final String status;



  @JsonKey(
    
    name: r'id',
    required: false,
    
  )


  final String? id;





    @override
    bool operator ==(Object other) => identical(this, other) || other is GenericActionResponse &&
      other.status == status &&
      other.id == id;

    @override
    int get hashCode =>
        status.hashCode +
        (id == null ? 0 : id.hashCode);

  factory GenericActionResponse.fromJson(Map<String, dynamic> json) => _$GenericActionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$GenericActionResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

