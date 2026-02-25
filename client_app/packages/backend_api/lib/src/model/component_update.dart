//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'component_update.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ComponentUpdate {
  /// Returns a new [ComponentUpdate] instance.
  ComponentUpdate({

    required  this.content,

     this.description,

     this.citation,

     this.citationFull,

     this.type,
  });

  @JsonKey(
    
    name: r'content',
    required: true,
    includeIfNull: true,
  )


  final Object? content;



  @JsonKey(
    
    name: r'description',
    required: false,
    
  )


  final Object? description;



  @JsonKey(
    
    name: r'citation',
    required: false,
    
  )


  final Object? citation;



  @JsonKey(
    
    name: r'citation_full',
    required: false,
    
  )


  final Object? citationFull;



  @JsonKey(
    
    name: r'type',
    required: false,
    
  )


  final Object? type;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ComponentUpdate &&
      other.content == content &&
      other.description == description &&
      other.citation == citation &&
      other.citationFull == citationFull &&
      other.type == type;

    @override
    int get hashCode =>
        (content == null ? 0 : content.hashCode) +
        (description == null ? 0 : description.hashCode) +
        (citation == null ? 0 : citation.hashCode) +
        (citationFull == null ? 0 : citationFull.hashCode) +
        (type == null ? 0 : type.hashCode);

  factory ComponentUpdate.fromJson(Map<String, dynamic> json) => _$ComponentUpdateFromJson(json);

  Map<String, dynamic> toJson() => _$ComponentUpdateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

