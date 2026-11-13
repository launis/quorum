// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'task_brief.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TaskBrief {

@StrictOpaqueIdConverter() String get id; String get slug;@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String get organizationId; I18nText get label; I18nText get description;@JsonKey(name: 'instruction_text') String? get instructionText;@JsonKey(name: 'source_url') String? get sourceUrl;
/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TaskBriefCopyWith<TaskBrief> get copyWith => _$TaskBriefCopyWithImpl<TaskBrief>(this as TaskBrief, _$identity);

  /// Serializes this TaskBrief to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TaskBrief(id: $id, slug: $slug, organizationId: $organizationId, label: $label, description: $description, instructionText: $instructionText, sourceUrl: $sourceUrl)';
}


}

/// @nodoc
abstract mixin class $TaskBriefCopyWith<$Res>  {
  factory $TaskBriefCopyWith(TaskBrief value, $Res Function(TaskBrief) _then) = _$TaskBriefCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId, I18nText label, I18nText description,@JsonKey(name: 'instruction_text') String? instructionText,@JsonKey(name: 'source_url') String? sourceUrl
});


$I18nTextCopyWith<$Res> get label;$I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class _$TaskBriefCopyWithImpl<$Res>
    implements $TaskBriefCopyWith<$Res> {
  _$TaskBriefCopyWithImpl(this._self, this._then);

  final TaskBrief _self;
  final $Res Function(TaskBrief) _then;

/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? organizationId = null,Object? label = null,Object? description = null,Object? instructionText = freezed,Object? sourceUrl = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,instructionText: freezed == instructionText ? _self.instructionText : instructionText // ignore: cast_nullable_to_non_nullable
as String?,sourceUrl: freezed == sourceUrl ? _self.sourceUrl : sourceUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// Adds pattern-matching-related methods to [TaskBrief].
extension TaskBriefPatterns on TaskBrief {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TaskBrief value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TaskBrief() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TaskBrief value)  $default,){
final _that = this;
switch (_that) {
case _TaskBrief():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TaskBrief value)?  $default,){
final _that = this;
switch (_that) {
case _TaskBrief() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  I18nText label,  I18nText description, @JsonKey(name: 'instruction_text')  String? instructionText, @JsonKey(name: 'source_url')  String? sourceUrl)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TaskBrief() when $default != null:
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.instructionText,_that.sourceUrl);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  I18nText label,  I18nText description, @JsonKey(name: 'instruction_text')  String? instructionText, @JsonKey(name: 'source_url')  String? sourceUrl)  $default,) {final _that = this;
switch (_that) {
case _TaskBrief():
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.instructionText,_that.sourceUrl);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id')  String organizationId,  I18nText label,  I18nText description, @JsonKey(name: 'instruction_text')  String? instructionText, @JsonKey(name: 'source_url')  String? sourceUrl)?  $default,) {final _that = this;
switch (_that) {
case _TaskBrief() when $default != null:
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.instructionText,_that.sourceUrl);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _TaskBrief extends TaskBrief {
  const _TaskBrief({@StrictOpaqueIdConverter() required this.id, required this.slug, @StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') required this.organizationId, required this.label, required this.description, @JsonKey(name: 'instruction_text') this.instructionText, @JsonKey(name: 'source_url') this.sourceUrl}): super._();
  factory _TaskBrief.fromJson(Map<String, dynamic> json) => _$TaskBriefFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') final  String organizationId;
@override final  I18nText label;
@override final  I18nText description;
@override@JsonKey(name: 'instruction_text') final  String? instructionText;
@override@JsonKey(name: 'source_url') final  String? sourceUrl;

/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TaskBriefCopyWith<_TaskBrief> get copyWith => __$TaskBriefCopyWithImpl<_TaskBrief>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TaskBriefToJson(this, );
}



@override
String toString() {
  return 'TaskBrief(id: $id, slug: $slug, organizationId: $organizationId, label: $label, description: $description, instructionText: $instructionText, sourceUrl: $sourceUrl)';
}


}

/// @nodoc
abstract mixin class _$TaskBriefCopyWith<$Res> implements $TaskBriefCopyWith<$Res> {
  factory _$TaskBriefCopyWith(_TaskBrief value, $Res Function(_TaskBrief) _then) = __$TaskBriefCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter()@JsonKey(name: 'organization_id') String organizationId, I18nText label, I18nText description,@JsonKey(name: 'instruction_text') String? instructionText,@JsonKey(name: 'source_url') String? sourceUrl
});


@override $I18nTextCopyWith<$Res> get label;@override $I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class __$TaskBriefCopyWithImpl<$Res>
    implements _$TaskBriefCopyWith<$Res> {
  __$TaskBriefCopyWithImpl(this._self, this._then);

  final _TaskBrief _self;
  final $Res Function(_TaskBrief) _then;

/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? organizationId = null,Object? label = null,Object? description = null,Object? instructionText = freezed,Object? sourceUrl = freezed,}) {
  return _then(_TaskBrief(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,organizationId: null == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,instructionText: freezed == instructionText ? _self.instructionText : instructionText // ignore: cast_nullable_to_non_nullable
as String?,sourceUrl: freezed == sourceUrl ? _self.sourceUrl : sourceUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}/// Create a copy of TaskBrief
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}

// dart format on
