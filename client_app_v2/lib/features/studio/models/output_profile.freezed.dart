// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'output_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$OutputLayoutBlock {

 String get presetView; I18nText? get title; I18nText? get description; List<String> get steps; List<String> get targetBlocks; bool get showText;
/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputLayoutBlockCopyWith<OutputLayoutBlock> get copyWith => _$OutputLayoutBlockCopyWithImpl<OutputLayoutBlock>(this as OutputLayoutBlock, _$identity);

  /// Serializes this OutputLayoutBlock to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputLayoutBlock(presetView: $presetView, title: $title, description: $description, steps: $steps, targetBlocks: $targetBlocks, showText: $showText)';
}


}

/// @nodoc
abstract mixin class $OutputLayoutBlockCopyWith<$Res>  {
  factory $OutputLayoutBlockCopyWith(OutputLayoutBlock value, $Res Function(OutputLayoutBlock) _then) = _$OutputLayoutBlockCopyWithImpl;
@useResult
$Res call({
 String presetView, I18nText? title, I18nText? description, List<String> steps, List<String> targetBlocks, bool showText
});


$I18nTextCopyWith<$Res>? get title;$I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class _$OutputLayoutBlockCopyWithImpl<$Res>
    implements $OutputLayoutBlockCopyWith<$Res> {
  _$OutputLayoutBlockCopyWithImpl(this._self, this._then);

  final OutputLayoutBlock _self;
  final $Res Function(OutputLayoutBlock) _then;

/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? steps = null,Object? targetBlocks = null,Object? showText = null,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as String,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<String>,targetBlocks: null == targetBlocks ? _self.targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,showText: null == showText ? _self.showText : showText // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}
/// Create a copy of OutputLayoutBlock
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
}/// Create a copy of OutputLayoutBlock
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
}
}


/// Adds pattern-matching-related methods to [OutputLayoutBlock].
extension OutputLayoutBlockPatterns on OutputLayoutBlock {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OutputLayoutBlock value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OutputLayoutBlock value)  $default,){
final _that = this;
switch (_that) {
case _OutputLayoutBlock():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OutputLayoutBlock value)?  $default,){
final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String presetView,  I18nText? title,  I18nText? description,  List<String> steps,  List<String> targetBlocks,  bool showText)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.steps,_that.targetBlocks,_that.showText);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String presetView,  I18nText? title,  I18nText? description,  List<String> steps,  List<String> targetBlocks,  bool showText)  $default,) {final _that = this;
switch (_that) {
case _OutputLayoutBlock():
return $default(_that.presetView,_that.title,_that.description,_that.steps,_that.targetBlocks,_that.showText);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String presetView,  I18nText? title,  I18nText? description,  List<String> steps,  List<String> targetBlocks,  bool showText)?  $default,) {final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.steps,_that.targetBlocks,_that.showText);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OutputLayoutBlock extends OutputLayoutBlock {
  const _OutputLayoutBlock({this.presetView = 'default', this.title, this.description, final  List<String> steps = const [], final  List<String> targetBlocks = const [], this.showText = true}): _steps = steps,_targetBlocks = targetBlocks,super._();
  factory _OutputLayoutBlock.fromJson(Map<String, dynamic> json) => _$OutputLayoutBlockFromJson(json);

@override@JsonKey() final  String presetView;
@override final  I18nText? title;
@override final  I18nText? description;
 final  List<String> _steps;
@override@JsonKey() List<String> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}

 final  List<String> _targetBlocks;
@override@JsonKey() List<String> get targetBlocks {
  if (_targetBlocks is EqualUnmodifiableListView) return _targetBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_targetBlocks);
}

@override@JsonKey() final  bool showText;

/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OutputLayoutBlockCopyWith<_OutputLayoutBlock> get copyWith => __$OutputLayoutBlockCopyWithImpl<_OutputLayoutBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OutputLayoutBlockToJson(this, );
}



@override
String toString() {
  return 'OutputLayoutBlock(presetView: $presetView, title: $title, description: $description, steps: $steps, targetBlocks: $targetBlocks, showText: $showText)';
}


}

/// @nodoc
abstract mixin class _$OutputLayoutBlockCopyWith<$Res> implements $OutputLayoutBlockCopyWith<$Res> {
  factory _$OutputLayoutBlockCopyWith(_OutputLayoutBlock value, $Res Function(_OutputLayoutBlock) _then) = __$OutputLayoutBlockCopyWithImpl;
@override @useResult
$Res call({
 String presetView, I18nText? title, I18nText? description, List<String> steps, List<String> targetBlocks, bool showText
});


@override $I18nTextCopyWith<$Res>? get title;@override $I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class __$OutputLayoutBlockCopyWithImpl<$Res>
    implements _$OutputLayoutBlockCopyWith<$Res> {
  __$OutputLayoutBlockCopyWithImpl(this._self, this._then);

  final _OutputLayoutBlock _self;
  final $Res Function(_OutputLayoutBlock) _then;

/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? steps = null,Object? targetBlocks = null,Object? showText = null,}) {
  return _then(_OutputLayoutBlock(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as String,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<String>,targetBlocks: null == targetBlocks ? _self._targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,showText: null == showText ? _self.showText : showText // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

/// Create a copy of OutputLayoutBlock
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
}/// Create a copy of OutputLayoutBlock
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
}
}


/// @nodoc
mixin _$OutputProfile {

@StrictOpaqueIdConverter() String get id; String get slug;@StrictOpaqueIdConverter() String get workflowId; I18nText get name; I18nText get description; List<OutputLayoutBlock> get layouts;
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputProfileCopyWith<OutputProfile> get copyWith => _$OutputProfileCopyWithImpl<OutputProfile>(this as OutputProfile, _$identity);

  /// Serializes this OutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, name: $name, description: $description, layouts: $layouts)';
}


}

/// @nodoc
abstract mixin class $OutputProfileCopyWith<$Res>  {
  factory $OutputProfileCopyWith(OutputProfile value, $Res Function(OutputProfile) _then) = _$OutputProfileCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, I18nText name, I18nText description, List<OutputLayoutBlock> layouts
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class _$OutputProfileCopyWithImpl<$Res>
    implements $OutputProfileCopyWith<$Res> {
  _$OutputProfileCopyWithImpl(this._self, this._then);

  final OutputProfile _self;
  final $Res Function(OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? name = null,Object? description = null,Object? layouts = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,
  ));
}
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// Adds pattern-matching-related methods to [OutputProfile].
extension OutputProfilePatterns on OutputProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OutputProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OutputProfile value)  $default,){
final _that = this;
switch (_that) {
case _OutputProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OutputProfile value)?  $default,){
final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  I18nText name,  I18nText description,  List<OutputLayoutBlock> layouts)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.name,_that.description,_that.layouts);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  I18nText name,  I18nText description,  List<OutputLayoutBlock> layouts)  $default,) {final _that = this;
switch (_that) {
case _OutputProfile():
return $default(_that.id,_that.slug,_that.workflowId,_that.name,_that.description,_that.layouts);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  I18nText name,  I18nText description,  List<OutputLayoutBlock> layouts)?  $default,) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.name,_that.description,_that.layouts);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OutputProfile extends OutputProfile {
  const _OutputProfile({@StrictOpaqueIdConverter() required this.id, this.slug = '', @StrictOpaqueIdConverter() required this.workflowId, required this.name, required this.description, final  List<OutputLayoutBlock> layouts = const []}): _layouts = layouts,super._();
  factory _OutputProfile.fromJson(Map<String, dynamic> json) => _$OutputProfileFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@JsonKey() final  String slug;
@override@StrictOpaqueIdConverter() final  String workflowId;
@override final  I18nText name;
@override final  I18nText description;
 final  List<OutputLayoutBlock> _layouts;
@override@JsonKey() List<OutputLayoutBlock> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}


/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OutputProfileCopyWith<_OutputProfile> get copyWith => __$OutputProfileCopyWithImpl<_OutputProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OutputProfileToJson(this, );
}



@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, name: $name, description: $description, layouts: $layouts)';
}


}

/// @nodoc
abstract mixin class _$OutputProfileCopyWith<$Res> implements $OutputProfileCopyWith<$Res> {
  factory _$OutputProfileCopyWith(_OutputProfile value, $Res Function(_OutputProfile) _then) = __$OutputProfileCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, I18nText name, I18nText description, List<OutputLayoutBlock> layouts
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class __$OutputProfileCopyWithImpl<$Res>
    implements _$OutputProfileCopyWith<$Res> {
  __$OutputProfileCopyWithImpl(this._self, this._then);

  final _OutputProfile _self;
  final $Res Function(_OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? name = null,Object? description = null,Object? layouts = null,}) {
  return _then(_OutputProfile(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,
  ));
}

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// @nodoc
mixin _$EmbeddedOutputProfile {

 I18nText get name; List<OutputLayoutBlock> get layouts;
/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EmbeddedOutputProfileCopyWith<EmbeddedOutputProfile> get copyWith => _$EmbeddedOutputProfileCopyWithImpl<EmbeddedOutputProfile>(this as EmbeddedOutputProfile, _$identity);

  /// Serializes this EmbeddedOutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'EmbeddedOutputProfile(name: $name, layouts: $layouts)';
}


}

/// @nodoc
abstract mixin class $EmbeddedOutputProfileCopyWith<$Res>  {
  factory $EmbeddedOutputProfileCopyWith(EmbeddedOutputProfile value, $Res Function(EmbeddedOutputProfile) _then) = _$EmbeddedOutputProfileCopyWithImpl;
@useResult
$Res call({
 I18nText name, List<OutputLayoutBlock> layouts
});


$I18nTextCopyWith<$Res> get name;

}
/// @nodoc
class _$EmbeddedOutputProfileCopyWithImpl<$Res>
    implements $EmbeddedOutputProfileCopyWith<$Res> {
  _$EmbeddedOutputProfileCopyWithImpl(this._self, this._then);

  final EmbeddedOutputProfile _self;
  final $Res Function(EmbeddedOutputProfile) _then;

/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? layouts = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,
  ));
}
/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}
}


/// Adds pattern-matching-related methods to [EmbeddedOutputProfile].
extension EmbeddedOutputProfilePatterns on EmbeddedOutputProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EmbeddedOutputProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EmbeddedOutputProfile value)  $default,){
final _that = this;
switch (_that) {
case _EmbeddedOutputProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EmbeddedOutputProfile value)?  $default,){
final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( I18nText name,  List<OutputLayoutBlock> layouts)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
return $default(_that.name,_that.layouts);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( I18nText name,  List<OutputLayoutBlock> layouts)  $default,) {final _that = this;
switch (_that) {
case _EmbeddedOutputProfile():
return $default(_that.name,_that.layouts);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( I18nText name,  List<OutputLayoutBlock> layouts)?  $default,) {final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
return $default(_that.name,_that.layouts);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _EmbeddedOutputProfile extends EmbeddedOutputProfile {
  const _EmbeddedOutputProfile({required this.name, final  List<OutputLayoutBlock> layouts = const []}): _layouts = layouts,super._();
  factory _EmbeddedOutputProfile.fromJson(Map<String, dynamic> json) => _$EmbeddedOutputProfileFromJson(json);

@override final  I18nText name;
 final  List<OutputLayoutBlock> _layouts;
@override@JsonKey() List<OutputLayoutBlock> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}


/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EmbeddedOutputProfileCopyWith<_EmbeddedOutputProfile> get copyWith => __$EmbeddedOutputProfileCopyWithImpl<_EmbeddedOutputProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EmbeddedOutputProfileToJson(this, );
}



@override
String toString() {
  return 'EmbeddedOutputProfile(name: $name, layouts: $layouts)';
}


}

/// @nodoc
abstract mixin class _$EmbeddedOutputProfileCopyWith<$Res> implements $EmbeddedOutputProfileCopyWith<$Res> {
  factory _$EmbeddedOutputProfileCopyWith(_EmbeddedOutputProfile value, $Res Function(_EmbeddedOutputProfile) _then) = __$EmbeddedOutputProfileCopyWithImpl;
@override @useResult
$Res call({
 I18nText name, List<OutputLayoutBlock> layouts
});


@override $I18nTextCopyWith<$Res> get name;

}
/// @nodoc
class __$EmbeddedOutputProfileCopyWithImpl<$Res>
    implements _$EmbeddedOutputProfileCopyWith<$Res> {
  __$EmbeddedOutputProfileCopyWithImpl(this._self, this._then);

  final _EmbeddedOutputProfile _self;
  final $Res Function(_EmbeddedOutputProfile) _then;

/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? layouts = null,}) {
  return _then(_EmbeddedOutputProfile(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,
  ));
}

/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}
}

// dart format on
