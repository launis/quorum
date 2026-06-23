// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'performative_lexicon.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LexiconConfigPayload {

@JsonKey(name: 'language_code') String get languageCode;@JsonKey(name: 'language_name') String get languageName;@JsonKey(name: 'fuzz_threshold') int get fuzzThreshold; List<String> get words;
/// Create a copy of LexiconConfigPayload
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LexiconConfigPayloadCopyWith<LexiconConfigPayload> get copyWith => _$LexiconConfigPayloadCopyWithImpl<LexiconConfigPayload>(this as LexiconConfigPayload, _$identity);

  /// Serializes this LexiconConfigPayload to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LexiconConfigPayload&&(identical(other.languageCode, languageCode) || other.languageCode == languageCode)&&(identical(other.languageName, languageName) || other.languageName == languageName)&&(identical(other.fuzzThreshold, fuzzThreshold) || other.fuzzThreshold == fuzzThreshold)&&const DeepCollectionEquality().equals(other.words, words));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,languageCode,languageName,fuzzThreshold,const DeepCollectionEquality().hash(words));

@override
String toString() {
  return 'LexiconConfigPayload(languageCode: $languageCode, languageName: $languageName, fuzzThreshold: $fuzzThreshold, words: $words)';
}


}

/// @nodoc
abstract mixin class $LexiconConfigPayloadCopyWith<$Res>  {
  factory $LexiconConfigPayloadCopyWith(LexiconConfigPayload value, $Res Function(LexiconConfigPayload) _then) = _$LexiconConfigPayloadCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'language_code') String languageCode,@JsonKey(name: 'language_name') String languageName,@JsonKey(name: 'fuzz_threshold') int fuzzThreshold, List<String> words
});




}
/// @nodoc
class _$LexiconConfigPayloadCopyWithImpl<$Res>
    implements $LexiconConfigPayloadCopyWith<$Res> {
  _$LexiconConfigPayloadCopyWithImpl(this._self, this._then);

  final LexiconConfigPayload _self;
  final $Res Function(LexiconConfigPayload) _then;

/// Create a copy of LexiconConfigPayload
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? languageCode = null,Object? languageName = null,Object? fuzzThreshold = null,Object? words = null,}) {
  return _then(_self.copyWith(
languageCode: null == languageCode ? _self.languageCode : languageCode // ignore: cast_nullable_to_non_nullable
as String,languageName: null == languageName ? _self.languageName : languageName // ignore: cast_nullable_to_non_nullable
as String,fuzzThreshold: null == fuzzThreshold ? _self.fuzzThreshold : fuzzThreshold // ignore: cast_nullable_to_non_nullable
as int,words: null == words ? _self.words : words // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [LexiconConfigPayload].
extension LexiconConfigPayloadPatterns on LexiconConfigPayload {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LexiconConfigPayload value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LexiconConfigPayload() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LexiconConfigPayload value)  $default,){
final _that = this;
switch (_that) {
case _LexiconConfigPayload():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LexiconConfigPayload value)?  $default,){
final _that = this;
switch (_that) {
case _LexiconConfigPayload() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'language_code')  String languageCode, @JsonKey(name: 'language_name')  String languageName, @JsonKey(name: 'fuzz_threshold')  int fuzzThreshold,  List<String> words)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LexiconConfigPayload() when $default != null:
return $default(_that.languageCode,_that.languageName,_that.fuzzThreshold,_that.words);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'language_code')  String languageCode, @JsonKey(name: 'language_name')  String languageName, @JsonKey(name: 'fuzz_threshold')  int fuzzThreshold,  List<String> words)  $default,) {final _that = this;
switch (_that) {
case _LexiconConfigPayload():
return $default(_that.languageCode,_that.languageName,_that.fuzzThreshold,_that.words);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'language_code')  String languageCode, @JsonKey(name: 'language_name')  String languageName, @JsonKey(name: 'fuzz_threshold')  int fuzzThreshold,  List<String> words)?  $default,) {final _that = this;
switch (_that) {
case _LexiconConfigPayload() when $default != null:
return $default(_that.languageCode,_that.languageName,_that.fuzzThreshold,_that.words);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LexiconConfigPayload implements LexiconConfigPayload {
  const _LexiconConfigPayload({@JsonKey(name: 'language_code') required this.languageCode, @JsonKey(name: 'language_name') required this.languageName, @JsonKey(name: 'fuzz_threshold') this.fuzzThreshold = 90, final  List<String> words = const []}): _words = words;
  factory _LexiconConfigPayload.fromJson(Map<String, dynamic> json) => _$LexiconConfigPayloadFromJson(json);

@override@JsonKey(name: 'language_code') final  String languageCode;
@override@JsonKey(name: 'language_name') final  String languageName;
@override@JsonKey(name: 'fuzz_threshold') final  int fuzzThreshold;
 final  List<String> _words;
@override@JsonKey() List<String> get words {
  if (_words is EqualUnmodifiableListView) return _words;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_words);
}


/// Create a copy of LexiconConfigPayload
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LexiconConfigPayloadCopyWith<_LexiconConfigPayload> get copyWith => __$LexiconConfigPayloadCopyWithImpl<_LexiconConfigPayload>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LexiconConfigPayloadToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LexiconConfigPayload&&(identical(other.languageCode, languageCode) || other.languageCode == languageCode)&&(identical(other.languageName, languageName) || other.languageName == languageName)&&(identical(other.fuzzThreshold, fuzzThreshold) || other.fuzzThreshold == fuzzThreshold)&&const DeepCollectionEquality().equals(other._words, _words));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,languageCode,languageName,fuzzThreshold,const DeepCollectionEquality().hash(_words));

@override
String toString() {
  return 'LexiconConfigPayload(languageCode: $languageCode, languageName: $languageName, fuzzThreshold: $fuzzThreshold, words: $words)';
}


}

/// @nodoc
abstract mixin class _$LexiconConfigPayloadCopyWith<$Res> implements $LexiconConfigPayloadCopyWith<$Res> {
  factory _$LexiconConfigPayloadCopyWith(_LexiconConfigPayload value, $Res Function(_LexiconConfigPayload) _then) = __$LexiconConfigPayloadCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'language_code') String languageCode,@JsonKey(name: 'language_name') String languageName,@JsonKey(name: 'fuzz_threshold') int fuzzThreshold, List<String> words
});




}
/// @nodoc
class __$LexiconConfigPayloadCopyWithImpl<$Res>
    implements _$LexiconConfigPayloadCopyWith<$Res> {
  __$LexiconConfigPayloadCopyWithImpl(this._self, this._then);

  final _LexiconConfigPayload _self;
  final $Res Function(_LexiconConfigPayload) _then;

/// Create a copy of LexiconConfigPayload
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? languageCode = null,Object? languageName = null,Object? fuzzThreshold = null,Object? words = null,}) {
  return _then(_LexiconConfigPayload(
languageCode: null == languageCode ? _self.languageCode : languageCode // ignore: cast_nullable_to_non_nullable
as String,languageName: null == languageName ? _self.languageName : languageName // ignore: cast_nullable_to_non_nullable
as String,fuzzThreshold: null == fuzzThreshold ? _self.fuzzThreshold : fuzzThreshold // ignore: cast_nullable_to_non_nullable
as int,words: null == words ? _self._words : words // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}


/// @nodoc
mixin _$SystemConfigPerformativeLexicons {

 String get id; String get slug; String get type;@JsonKey(name: 'lexicon_configs') Map<String, LexiconConfigPayload> get lexiconConfigs;
/// Create a copy of SystemConfigPerformativeLexicons
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SystemConfigPerformativeLexiconsCopyWith<SystemConfigPerformativeLexicons> get copyWith => _$SystemConfigPerformativeLexiconsCopyWithImpl<SystemConfigPerformativeLexicons>(this as SystemConfigPerformativeLexicons, _$identity);

  /// Serializes this SystemConfigPerformativeLexicons to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SystemConfigPerformativeLexicons&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.type, type) || other.type == type)&&const DeepCollectionEquality().equals(other.lexiconConfigs, lexiconConfigs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,type,const DeepCollectionEquality().hash(lexiconConfigs));

@override
String toString() {
  return 'SystemConfigPerformativeLexicons(id: $id, slug: $slug, type: $type, lexiconConfigs: $lexiconConfigs)';
}


}

/// @nodoc
abstract mixin class $SystemConfigPerformativeLexiconsCopyWith<$Res>  {
  factory $SystemConfigPerformativeLexiconsCopyWith(SystemConfigPerformativeLexicons value, $Res Function(SystemConfigPerformativeLexicons) _then) = _$SystemConfigPerformativeLexiconsCopyWithImpl;
@useResult
$Res call({
 String id, String slug, String type,@JsonKey(name: 'lexicon_configs') Map<String, LexiconConfigPayload> lexiconConfigs
});




}
/// @nodoc
class _$SystemConfigPerformativeLexiconsCopyWithImpl<$Res>
    implements $SystemConfigPerformativeLexiconsCopyWith<$Res> {
  _$SystemConfigPerformativeLexiconsCopyWithImpl(this._self, this._then);

  final SystemConfigPerformativeLexicons _self;
  final $Res Function(SystemConfigPerformativeLexicons) _then;

/// Create a copy of SystemConfigPerformativeLexicons
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? type = null,Object? lexiconConfigs = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,lexiconConfigs: null == lexiconConfigs ? _self.lexiconConfigs : lexiconConfigs // ignore: cast_nullable_to_non_nullable
as Map<String, LexiconConfigPayload>,
  ));
}

}


/// Adds pattern-matching-related methods to [SystemConfigPerformativeLexicons].
extension SystemConfigPerformativeLexiconsPatterns on SystemConfigPerformativeLexicons {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SystemConfigPerformativeLexicons value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SystemConfigPerformativeLexicons() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SystemConfigPerformativeLexicons value)  $default,){
final _that = this;
switch (_that) {
case _SystemConfigPerformativeLexicons():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SystemConfigPerformativeLexicons value)?  $default,){
final _that = this;
switch (_that) {
case _SystemConfigPerformativeLexicons() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String slug,  String type, @JsonKey(name: 'lexicon_configs')  Map<String, LexiconConfigPayload> lexiconConfigs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SystemConfigPerformativeLexicons() when $default != null:
return $default(_that.id,_that.slug,_that.type,_that.lexiconConfigs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String slug,  String type, @JsonKey(name: 'lexicon_configs')  Map<String, LexiconConfigPayload> lexiconConfigs)  $default,) {final _that = this;
switch (_that) {
case _SystemConfigPerformativeLexicons():
return $default(_that.id,_that.slug,_that.type,_that.lexiconConfigs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String slug,  String type, @JsonKey(name: 'lexicon_configs')  Map<String, LexiconConfigPayload> lexiconConfigs)?  $default,) {final _that = this;
switch (_that) {
case _SystemConfigPerformativeLexicons() when $default != null:
return $default(_that.id,_that.slug,_that.type,_that.lexiconConfigs);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SystemConfigPerformativeLexicons implements SystemConfigPerformativeLexicons {
  const _SystemConfigPerformativeLexicons({required this.id, required this.slug, required this.type, @JsonKey(name: 'lexicon_configs') final  Map<String, LexiconConfigPayload> lexiconConfigs = const {}}): _lexiconConfigs = lexiconConfigs;
  factory _SystemConfigPerformativeLexicons.fromJson(Map<String, dynamic> json) => _$SystemConfigPerformativeLexiconsFromJson(json);

@override final  String id;
@override final  String slug;
@override final  String type;
 final  Map<String, LexiconConfigPayload> _lexiconConfigs;
@override@JsonKey(name: 'lexicon_configs') Map<String, LexiconConfigPayload> get lexiconConfigs {
  if (_lexiconConfigs is EqualUnmodifiableMapView) return _lexiconConfigs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_lexiconConfigs);
}


/// Create a copy of SystemConfigPerformativeLexicons
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SystemConfigPerformativeLexiconsCopyWith<_SystemConfigPerformativeLexicons> get copyWith => __$SystemConfigPerformativeLexiconsCopyWithImpl<_SystemConfigPerformativeLexicons>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SystemConfigPerformativeLexiconsToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _SystemConfigPerformativeLexicons&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.type, type) || other.type == type)&&const DeepCollectionEquality().equals(other._lexiconConfigs, _lexiconConfigs));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,type,const DeepCollectionEquality().hash(_lexiconConfigs));

@override
String toString() {
  return 'SystemConfigPerformativeLexicons(id: $id, slug: $slug, type: $type, lexiconConfigs: $lexiconConfigs)';
}


}

/// @nodoc
abstract mixin class _$SystemConfigPerformativeLexiconsCopyWith<$Res> implements $SystemConfigPerformativeLexiconsCopyWith<$Res> {
  factory _$SystemConfigPerformativeLexiconsCopyWith(_SystemConfigPerformativeLexicons value, $Res Function(_SystemConfigPerformativeLexicons) _then) = __$SystemConfigPerformativeLexiconsCopyWithImpl;
@override @useResult
$Res call({
 String id, String slug, String type,@JsonKey(name: 'lexicon_configs') Map<String, LexiconConfigPayload> lexiconConfigs
});




}
/// @nodoc
class __$SystemConfigPerformativeLexiconsCopyWithImpl<$Res>
    implements _$SystemConfigPerformativeLexiconsCopyWith<$Res> {
  __$SystemConfigPerformativeLexiconsCopyWithImpl(this._self, this._then);

  final _SystemConfigPerformativeLexicons _self;
  final $Res Function(_SystemConfigPerformativeLexicons) _then;

/// Create a copy of SystemConfigPerformativeLexicons
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? type = null,Object? lexiconConfigs = null,}) {
  return _then(_SystemConfigPerformativeLexicons(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,lexiconConfigs: null == lexiconConfigs ? _self._lexiconConfigs : lexiconConfigs // ignore: cast_nullable_to_non_nullable
as Map<String, LexiconConfigPayload>,
  ));
}


}


/// @nodoc
mixin _$LexiconSuggestionListDTO {

@JsonKey(name: 'suggested_phrases') List<String> get suggestedPhrases;
/// Create a copy of LexiconSuggestionListDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LexiconSuggestionListDTOCopyWith<LexiconSuggestionListDTO> get copyWith => _$LexiconSuggestionListDTOCopyWithImpl<LexiconSuggestionListDTO>(this as LexiconSuggestionListDTO, _$identity);

  /// Serializes this LexiconSuggestionListDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LexiconSuggestionListDTO&&const DeepCollectionEquality().equals(other.suggestedPhrases, suggestedPhrases));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(suggestedPhrases));

@override
String toString() {
  return 'LexiconSuggestionListDTO(suggestedPhrases: $suggestedPhrases)';
}


}

/// @nodoc
abstract mixin class $LexiconSuggestionListDTOCopyWith<$Res>  {
  factory $LexiconSuggestionListDTOCopyWith(LexiconSuggestionListDTO value, $Res Function(LexiconSuggestionListDTO) _then) = _$LexiconSuggestionListDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'suggested_phrases') List<String> suggestedPhrases
});




}
/// @nodoc
class _$LexiconSuggestionListDTOCopyWithImpl<$Res>
    implements $LexiconSuggestionListDTOCopyWith<$Res> {
  _$LexiconSuggestionListDTOCopyWithImpl(this._self, this._then);

  final LexiconSuggestionListDTO _self;
  final $Res Function(LexiconSuggestionListDTO) _then;

/// Create a copy of LexiconSuggestionListDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? suggestedPhrases = null,}) {
  return _then(_self.copyWith(
suggestedPhrases: null == suggestedPhrases ? _self.suggestedPhrases : suggestedPhrases // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [LexiconSuggestionListDTO].
extension LexiconSuggestionListDTOPatterns on LexiconSuggestionListDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LexiconSuggestionListDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LexiconSuggestionListDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LexiconSuggestionListDTO value)  $default,){
final _that = this;
switch (_that) {
case _LexiconSuggestionListDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LexiconSuggestionListDTO value)?  $default,){
final _that = this;
switch (_that) {
case _LexiconSuggestionListDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'suggested_phrases')  List<String> suggestedPhrases)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LexiconSuggestionListDTO() when $default != null:
return $default(_that.suggestedPhrases);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'suggested_phrases')  List<String> suggestedPhrases)  $default,) {final _that = this;
switch (_that) {
case _LexiconSuggestionListDTO():
return $default(_that.suggestedPhrases);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'suggested_phrases')  List<String> suggestedPhrases)?  $default,) {final _that = this;
switch (_that) {
case _LexiconSuggestionListDTO() when $default != null:
return $default(_that.suggestedPhrases);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LexiconSuggestionListDTO implements LexiconSuggestionListDTO {
  const _LexiconSuggestionListDTO({@JsonKey(name: 'suggested_phrases') final  List<String> suggestedPhrases = const []}): _suggestedPhrases = suggestedPhrases;
  factory _LexiconSuggestionListDTO.fromJson(Map<String, dynamic> json) => _$LexiconSuggestionListDTOFromJson(json);

 final  List<String> _suggestedPhrases;
@override@JsonKey(name: 'suggested_phrases') List<String> get suggestedPhrases {
  if (_suggestedPhrases is EqualUnmodifiableListView) return _suggestedPhrases;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_suggestedPhrases);
}


/// Create a copy of LexiconSuggestionListDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LexiconSuggestionListDTOCopyWith<_LexiconSuggestionListDTO> get copyWith => __$LexiconSuggestionListDTOCopyWithImpl<_LexiconSuggestionListDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LexiconSuggestionListDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LexiconSuggestionListDTO&&const DeepCollectionEquality().equals(other._suggestedPhrases, _suggestedPhrases));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_suggestedPhrases));

@override
String toString() {
  return 'LexiconSuggestionListDTO(suggestedPhrases: $suggestedPhrases)';
}


}

/// @nodoc
abstract mixin class _$LexiconSuggestionListDTOCopyWith<$Res> implements $LexiconSuggestionListDTOCopyWith<$Res> {
  factory _$LexiconSuggestionListDTOCopyWith(_LexiconSuggestionListDTO value, $Res Function(_LexiconSuggestionListDTO) _then) = __$LexiconSuggestionListDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'suggested_phrases') List<String> suggestedPhrases
});




}
/// @nodoc
class __$LexiconSuggestionListDTOCopyWithImpl<$Res>
    implements _$LexiconSuggestionListDTOCopyWith<$Res> {
  __$LexiconSuggestionListDTOCopyWithImpl(this._self, this._then);

  final _LexiconSuggestionListDTO _self;
  final $Res Function(_LexiconSuggestionListDTO) _then;

/// Create a copy of LexiconSuggestionListDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? suggestedPhrases = null,}) {
  return _then(_LexiconSuggestionListDTO(
suggestedPhrases: null == suggestedPhrases ? _self._suggestedPhrases : suggestedPhrases // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
