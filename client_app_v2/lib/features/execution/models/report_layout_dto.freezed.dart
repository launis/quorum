// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_layout_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReportLayoutDto {

@JsonKey(name: 'preset_view') String get presetView; I18nText? get title; I18nText? get description; List<MatrixScorecardRowDto> get axes;@JsonKey(name: 'text_delivery_mode') String get textDeliveryMode; SynthesisConfigDto? get synthesis;@JsonKey(name: 'synthesis_blocks') List<Map<String, dynamic>>? get synthesisBlocks;
/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportLayoutDtoCopyWith<ReportLayoutDto> get copyWith => _$ReportLayoutDtoCopyWithImpl<ReportLayoutDto>(this as ReportLayoutDto, _$identity);

  /// Serializes this ReportLayoutDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportLayoutDto(presetView: $presetView, title: $title, description: $description, axes: $axes, textDeliveryMode: $textDeliveryMode, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks)';
}


}

/// @nodoc
abstract mixin class $ReportLayoutDtoCopyWith<$Res>  {
  factory $ReportLayoutDtoCopyWith(ReportLayoutDto value, $Res Function(ReportLayoutDto) _then) = _$ReportLayoutDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'preset_view') String presetView, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'text_delivery_mode') String textDeliveryMode, SynthesisConfigDto? synthesis,@JsonKey(name: 'synthesis_blocks') List<Map<String, dynamic>>? synthesisBlocks
});


$I18nTextCopyWith<$Res>? get title;$I18nTextCopyWith<$Res>? get description;$SynthesisConfigDtoCopyWith<$Res>? get synthesis;

}
/// @nodoc
class _$ReportLayoutDtoCopyWithImpl<$Res>
    implements $ReportLayoutDtoCopyWith<$Res> {
  _$ReportLayoutDtoCopyWithImpl(this._self, this._then);

  final ReportLayoutDto _self;
  final $Res Function(ReportLayoutDto) _then;

/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? textDeliveryMode = null,Object? synthesis = freezed,Object? synthesisBlocks = freezed,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as String,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self.axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as String,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDto?,synthesisBlocks: freezed == synthesisBlocks ? _self.synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>?,
  ));
}
/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get description {
    if (_self.description == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.description!, (value) {
    return _then(_self.copyWith(description: value));
  });
}/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDtoCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDtoCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportLayoutDto].
extension ReportLayoutDtoPatterns on ReportLayoutDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportLayoutDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportLayoutDto value)  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportLayoutDto value)?  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  String presetView,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  SynthesisConfigDto? synthesis, @JsonKey(name: 'synthesis_blocks')  List<Map<String, dynamic>>? synthesisBlocks)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.axes,_that.textDeliveryMode,_that.synthesis,_that.synthesisBlocks);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  String presetView,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  SynthesisConfigDto? synthesis, @JsonKey(name: 'synthesis_blocks')  List<Map<String, dynamic>>? synthesisBlocks)  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDto():
return $default(_that.presetView,_that.title,_that.description,_that.axes,_that.textDeliveryMode,_that.synthesis,_that.synthesisBlocks);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'preset_view')  String presetView,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  SynthesisConfigDto? synthesis, @JsonKey(name: 'synthesis_blocks')  List<Map<String, dynamic>>? synthesisBlocks)?  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.axes,_that.textDeliveryMode,_that.synthesis,_that.synthesisBlocks);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportLayoutDto implements ReportLayoutDto {
  const _ReportLayoutDto({@JsonKey(name: 'preset_view') required this.presetView, this.title, this.description, final  List<MatrixScorecardRowDto> axes = const [], @JsonKey(name: 'text_delivery_mode') this.textDeliveryMode = 'full', this.synthesis, @JsonKey(name: 'synthesis_blocks') final  List<Map<String, dynamic>>? synthesisBlocks}): _axes = axes,_synthesisBlocks = synthesisBlocks;
  factory _ReportLayoutDto.fromJson(Map<String, dynamic> json) => _$ReportLayoutDtoFromJson(json);

@override@JsonKey(name: 'preset_view') final  String presetView;
@override final  I18nText? title;
@override final  I18nText? description;
 final  List<MatrixScorecardRowDto> _axes;
@override@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}

@override@JsonKey(name: 'text_delivery_mode') final  String textDeliveryMode;
@override final  SynthesisConfigDto? synthesis;
 final  List<Map<String, dynamic>>? _synthesisBlocks;
@override@JsonKey(name: 'synthesis_blocks') List<Map<String, dynamic>>? get synthesisBlocks {
  final value = _synthesisBlocks;
  if (value == null) return null;
  if (_synthesisBlocks is EqualUnmodifiableListView) return _synthesisBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportLayoutDtoCopyWith<_ReportLayoutDto> get copyWith => __$ReportLayoutDtoCopyWithImpl<_ReportLayoutDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportLayoutDtoToJson(this, );
}



@override
String toString() {
  return 'ReportLayoutDto(presetView: $presetView, title: $title, description: $description, axes: $axes, textDeliveryMode: $textDeliveryMode, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks)';
}


}

/// @nodoc
abstract mixin class _$ReportLayoutDtoCopyWith<$Res> implements $ReportLayoutDtoCopyWith<$Res> {
  factory _$ReportLayoutDtoCopyWith(_ReportLayoutDto value, $Res Function(_ReportLayoutDto) _then) = __$ReportLayoutDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'preset_view') String presetView, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'text_delivery_mode') String textDeliveryMode, SynthesisConfigDto? synthesis,@JsonKey(name: 'synthesis_blocks') List<Map<String, dynamic>>? synthesisBlocks
});


@override $I18nTextCopyWith<$Res>? get title;@override $I18nTextCopyWith<$Res>? get description;@override $SynthesisConfigDtoCopyWith<$Res>? get synthesis;

}
/// @nodoc
class __$ReportLayoutDtoCopyWithImpl<$Res>
    implements _$ReportLayoutDtoCopyWith<$Res> {
  __$ReportLayoutDtoCopyWithImpl(this._self, this._then);

  final _ReportLayoutDto _self;
  final $Res Function(_ReportLayoutDto) _then;

/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? textDeliveryMode = null,Object? synthesis = freezed,Object? synthesisBlocks = freezed,}) {
  return _then(_ReportLayoutDto(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as String,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as String,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDto?,synthesisBlocks: freezed == synthesisBlocks ? _self._synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>?,
  ));
}

/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get description {
    if (_self.description == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.description!, (value) {
    return _then(_self.copyWith(description: value));
  });
}/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDtoCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDtoCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}

// dart format on
