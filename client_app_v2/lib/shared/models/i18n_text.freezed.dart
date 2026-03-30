// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'i18n_text.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$I18nText {

 String get defaultLocale; Map<String, String> get translations;
/// Create a copy of I18nText
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$I18nTextCopyWith<I18nText> get copyWith => _$I18nTextCopyWithImpl<I18nText>(this as I18nText, _$identity);

  /// Serializes this I18nText to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is I18nText&&(identical(other.defaultLocale, defaultLocale) || other.defaultLocale == defaultLocale)&&const DeepCollectionEquality().equals(other.translations, translations));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,defaultLocale,const DeepCollectionEquality().hash(translations));

@override
String toString() {
  return 'I18nText(defaultLocale: $defaultLocale, translations: $translations)';
}


}

/// @nodoc
abstract mixin class $I18nTextCopyWith<$Res>  {
  factory $I18nTextCopyWith(I18nText value, $Res Function(I18nText) _then) = _$I18nTextCopyWithImpl;
@useResult
$Res call({
 String defaultLocale, Map<String, String> translations
});




}
/// @nodoc
class _$I18nTextCopyWithImpl<$Res>
    implements $I18nTextCopyWith<$Res> {
  _$I18nTextCopyWithImpl(this._self, this._then);

  final I18nText _self;
  final $Res Function(I18nText) _then;

/// Create a copy of I18nText
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? defaultLocale = null,Object? translations = null,}) {
  return _then(_self.copyWith(
defaultLocale: null == defaultLocale ? _self.defaultLocale : defaultLocale // ignore: cast_nullable_to_non_nullable
as String,translations: null == translations ? _self.translations : translations // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}

}


/// Adds pattern-matching-related methods to [I18nText].
extension I18nTextPatterns on I18nText {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _I18nText value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _I18nText() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _I18nText value)  $default,){
final _that = this;
switch (_that) {
case _I18nText():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _I18nText value)?  $default,){
final _that = this;
switch (_that) {
case _I18nText() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String defaultLocale,  Map<String, String> translations)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _I18nText() when $default != null:
return $default(_that.defaultLocale,_that.translations);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String defaultLocale,  Map<String, String> translations)  $default,) {final _that = this;
switch (_that) {
case _I18nText():
return $default(_that.defaultLocale,_that.translations);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String defaultLocale,  Map<String, String> translations)?  $default,) {final _that = this;
switch (_that) {
case _I18nText() when $default != null:
return $default(_that.defaultLocale,_that.translations);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _I18nText extends I18nText {
  const _I18nText({this.defaultLocale = 'en', final  Map<String, String> translations = const {'en' : ''}}): _translations = translations,super._();
  factory _I18nText.fromJson(Map<String, dynamic> json) => _$I18nTextFromJson(json);

@override@JsonKey() final  String defaultLocale;
 final  Map<String, String> _translations;
@override@JsonKey() Map<String, String> get translations {
  if (_translations is EqualUnmodifiableMapView) return _translations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_translations);
}


/// Create a copy of I18nText
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$I18nTextCopyWith<_I18nText> get copyWith => __$I18nTextCopyWithImpl<_I18nText>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$I18nTextToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _I18nText&&(identical(other.defaultLocale, defaultLocale) || other.defaultLocale == defaultLocale)&&const DeepCollectionEquality().equals(other._translations, _translations));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,defaultLocale,const DeepCollectionEquality().hash(_translations));

@override
String toString() {
  return 'I18nText(defaultLocale: $defaultLocale, translations: $translations)';
}


}

/// @nodoc
abstract mixin class _$I18nTextCopyWith<$Res> implements $I18nTextCopyWith<$Res> {
  factory _$I18nTextCopyWith(_I18nText value, $Res Function(_I18nText) _then) = __$I18nTextCopyWithImpl;
@override @useResult
$Res call({
 String defaultLocale, Map<String, String> translations
});




}
/// @nodoc
class __$I18nTextCopyWithImpl<$Res>
    implements _$I18nTextCopyWith<$Res> {
  __$I18nTextCopyWithImpl(this._self, this._then);

  final _I18nText _self;
  final $Res Function(_I18nText) _then;

/// Create a copy of I18nText
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? defaultLocale = null,Object? translations = null,}) {
  return _then(_I18nText(
defaultLocale: null == defaultLocale ? _self.defaultLocale : defaultLocale // ignore: cast_nullable_to_non_nullable
as String,translations: null == translations ? _self._translations : translations // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}


}

// dart format on
