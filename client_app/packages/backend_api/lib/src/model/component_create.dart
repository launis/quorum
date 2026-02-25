//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'component_create.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ComponentCreate {
  /// Returns a new [ComponentCreate] instance.
  ComponentCreate({

     this.id,

    required  this.name,

    required  this.type,

    required  this.content,

     this.description,

     this.citation,

     this.citationFull,

     this.module,

     this.componentClass,
  });

  @JsonKey(
    
    name: r'id',
    required: false,
    
  )


  final Object? id;



  @JsonKey(
    
    name: r'name',
    required: true,
    includeIfNull: true,
  )


  final Object? name;



  @JsonKey(
    
    name: r'type',
    required: true,
    includeIfNull: true,
  )


  final Object? type;



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
    
    name: r'module',
    required: false,
    
  )


  final Object? module;



  @JsonKey(
    
    name: r'component_class',
    required: false,
    
  )


  final Object? componentClass;





    @override
    bool operator ==(Object other) => identical(this, other) || other is ComponentCreate &&
      other.id == id &&
      other.name == name &&
      other.type == type &&
      other.content == content &&
      other.description == description &&
      other.citation == citation &&
      other.citationFull == citationFull &&
      other.module == module &&
      other.componentClass == componentClass;

    @override
    int get hashCode =>
        (id == null ? 0 : id.hashCode) +
        (name == null ? 0 : name.hashCode) +
        (type == null ? 0 : type.hashCode) +
        (content == null ? 0 : content.hashCode) +
        (description == null ? 0 : description.hashCode) +
        (citation == null ? 0 : citation.hashCode) +
        (citationFull == null ? 0 : citationFull.hashCode) +
        (module == null ? 0 : module.hashCode) +
        (componentClass == null ? 0 : componentClass.hashCode);

  factory ComponentCreate.fromJson(Map<String, dynamic> json) => _$ComponentCreateFromJson(json);

  Map<String, dynamic> toJson() => _$ComponentCreateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

