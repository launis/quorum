// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'tda_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
TDAState _$TDAStateFromJson(
  Map<String, dynamic> json
) {
        switch (json['runtimeType']) {
                  case 'pending':
          return Pending.fromJson(
            json
          );
                case 'evaluated':
          return Evaluated.fromJson(
            json
          );
                case 'dlq':
          return Dlq.fromJson(
            json
          );
        
          default:
            throw CheckedFromJsonException(
  json,
  'runtimeType',
  'TDAState',
  'Invalid union type "${json['runtimeType']}"!'
);
        }
      
}

/// @nodoc
mixin _$TDAState {



  /// Serializes this TDAState to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TDAState);
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'TDAState()';
}


}

/// @nodoc
class $TDAStateCopyWith<$Res>  {
$TDAStateCopyWith(TDAState _, $Res Function(TDAState) __);
}


/// Adds pattern-matching-related methods to [TDAState].
extension TDAStatePatterns on TDAState {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( Pending value)?  pending,TResult Function( Evaluated value)?  evaluated,TResult Function( Dlq value)?  dlq,required TResult orElse(),}){
final _that = this;
switch (_that) {
case Pending() when pending != null:
return pending(_that);case Evaluated() when evaluated != null:
return evaluated(_that);case Dlq() when dlq != null:
return dlq(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( Pending value)  pending,required TResult Function( Evaluated value)  evaluated,required TResult Function( Dlq value)  dlq,}){
final _that = this;
switch (_that) {
case Pending():
return pending(_that);case Evaluated():
return evaluated(_that);case Dlq():
return dlq(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( Pending value)?  pending,TResult? Function( Evaluated value)?  evaluated,TResult? Function( Dlq value)?  dlq,}){
final _that = this;
switch (_that) {
case Pending() when pending != null:
return pending(_that);case Evaluated() when evaluated != null:
return evaluated(_that);case Dlq() when dlq != null:
return dlq(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function()?  pending,TResult Function( bool passed,  String displayQuote,  String rawAnchor)?  evaluated,TResult Function( String userReason,  String backendTrace)?  dlq,required TResult orElse(),}) {final _that = this;
switch (_that) {
case Pending() when pending != null:
return pending();case Evaluated() when evaluated != null:
return evaluated(_that.passed,_that.displayQuote,_that.rawAnchor);case Dlq() when dlq != null:
return dlq(_that.userReason,_that.backendTrace);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function()  pending,required TResult Function( bool passed,  String displayQuote,  String rawAnchor)  evaluated,required TResult Function( String userReason,  String backendTrace)  dlq,}) {final _that = this;
switch (_that) {
case Pending():
return pending();case Evaluated():
return evaluated(_that.passed,_that.displayQuote,_that.rawAnchor);case Dlq():
return dlq(_that.userReason,_that.backendTrace);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function()?  pending,TResult? Function( bool passed,  String displayQuote,  String rawAnchor)?  evaluated,TResult? Function( String userReason,  String backendTrace)?  dlq,}) {final _that = this;
switch (_that) {
case Pending() when pending != null:
return pending();case Evaluated() when evaluated != null:
return evaluated(_that.passed,_that.displayQuote,_that.rawAnchor);case Dlq() when dlq != null:
return dlq(_that.userReason,_that.backendTrace);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class Pending implements TDAState {
  const Pending({final  String? $type}): $type = $type ?? 'pending';
  factory Pending.fromJson(Map<String, dynamic> json) => _$PendingFromJson(json);



@JsonKey(name: 'runtimeType')
final String $type;



@override
Map<String, dynamic> toJson() {
  return _$PendingToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Pending);
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'TDAState.pending()';
}


}




/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class Evaluated implements TDAState {
  const Evaluated({required this.passed, required this.displayQuote, required this.rawAnchor, final  String? $type}): $type = $type ?? 'evaluated';
  factory Evaluated.fromJson(Map<String, dynamic> json) => _$EvaluatedFromJson(json);

 final  bool passed;
 final  String displayQuote;
 final  String rawAnchor;

@JsonKey(name: 'runtimeType')
final String $type;


/// Create a copy of TDAState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EvaluatedCopyWith<Evaluated> get copyWith => _$EvaluatedCopyWithImpl<Evaluated>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EvaluatedToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Evaluated&&(identical(other.passed, passed) || other.passed == passed)&&(identical(other.displayQuote, displayQuote) || other.displayQuote == displayQuote)&&(identical(other.rawAnchor, rawAnchor) || other.rawAnchor == rawAnchor));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,passed,displayQuote,rawAnchor);

@override
String toString() {
  return 'TDAState.evaluated(passed: $passed, displayQuote: $displayQuote, rawAnchor: $rawAnchor)';
}


}

/// @nodoc
abstract mixin class $EvaluatedCopyWith<$Res> implements $TDAStateCopyWith<$Res> {
  factory $EvaluatedCopyWith(Evaluated value, $Res Function(Evaluated) _then) = _$EvaluatedCopyWithImpl;
@useResult
$Res call({
 bool passed, String displayQuote, String rawAnchor
});




}
/// @nodoc
class _$EvaluatedCopyWithImpl<$Res>
    implements $EvaluatedCopyWith<$Res> {
  _$EvaluatedCopyWithImpl(this._self, this._then);

  final Evaluated _self;
  final $Res Function(Evaluated) _then;

/// Create a copy of TDAState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? passed = null,Object? displayQuote = null,Object? rawAnchor = null,}) {
  return _then(Evaluated(
passed: null == passed ? _self.passed : passed // ignore: cast_nullable_to_non_nullable
as bool,displayQuote: null == displayQuote ? _self.displayQuote : displayQuote // ignore: cast_nullable_to_non_nullable
as String,rawAnchor: null == rawAnchor ? _self.rawAnchor : rawAnchor // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class Dlq implements TDAState {
  const Dlq({required this.userReason, required this.backendTrace, final  String? $type}): $type = $type ?? 'dlq';
  factory Dlq.fromJson(Map<String, dynamic> json) => _$DlqFromJson(json);

 final  String userReason;
 final  String backendTrace;

@JsonKey(name: 'runtimeType')
final String $type;


/// Create a copy of TDAState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DlqCopyWith<Dlq> get copyWith => _$DlqCopyWithImpl<Dlq>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DlqToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Dlq&&(identical(other.userReason, userReason) || other.userReason == userReason)&&(identical(other.backendTrace, backendTrace) || other.backendTrace == backendTrace));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,userReason,backendTrace);

@override
String toString() {
  return 'TDAState.dlq(userReason: $userReason, backendTrace: $backendTrace)';
}


}

/// @nodoc
abstract mixin class $DlqCopyWith<$Res> implements $TDAStateCopyWith<$Res> {
  factory $DlqCopyWith(Dlq value, $Res Function(Dlq) _then) = _$DlqCopyWithImpl;
@useResult
$Res call({
 String userReason, String backendTrace
});




}
/// @nodoc
class _$DlqCopyWithImpl<$Res>
    implements $DlqCopyWith<$Res> {
  _$DlqCopyWithImpl(this._self, this._then);

  final Dlq _self;
  final $Res Function(Dlq) _then;

/// Create a copy of TDAState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? userReason = null,Object? backendTrace = null,}) {
  return _then(Dlq(
userReason: null == userReason ? _self.userReason : userReason // ignore: cast_nullable_to_non_nullable
as String,backendTrace: null == backendTrace ? _self.backendTrace : backendTrace // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
