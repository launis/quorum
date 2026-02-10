// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'assessment_view.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$AssessmentView {

 String get sessionId; String get statusLabel;// e.g. "Analysoidaan..."
 String get uiVariant;// "default", "warning", "error"
 String get statusMessage;// Contextual help text
 bool get showWarningBanner;// Toggle for warning UI
 List<StepProgressItem> get steps;// Progress indicators
 int? get finalScore;
/// Create a copy of AssessmentView
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssessmentViewCopyWith<AssessmentView> get copyWith => _$AssessmentViewCopyWithImpl<AssessmentView>(this as AssessmentView, _$identity);

  /// Serializes this AssessmentView to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssessmentView&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.statusLabel, statusLabel) || other.statusLabel == statusLabel)&&(identical(other.uiVariant, uiVariant) || other.uiVariant == uiVariant)&&(identical(other.statusMessage, statusMessage) || other.statusMessage == statusMessage)&&(identical(other.showWarningBanner, showWarningBanner) || other.showWarningBanner == showWarningBanner)&&const DeepCollectionEquality().equals(other.steps, steps)&&(identical(other.finalScore, finalScore) || other.finalScore == finalScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,sessionId,statusLabel,uiVariant,statusMessage,showWarningBanner,const DeepCollectionEquality().hash(steps),finalScore);

@override
String toString() {
  return 'AssessmentView(sessionId: $sessionId, statusLabel: $statusLabel, uiVariant: $uiVariant, statusMessage: $statusMessage, showWarningBanner: $showWarningBanner, steps: $steps, finalScore: $finalScore)';
}


}

/// @nodoc
abstract mixin class $AssessmentViewCopyWith<$Res>  {
  factory $AssessmentViewCopyWith(AssessmentView value, $Res Function(AssessmentView) _then) = _$AssessmentViewCopyWithImpl;
@useResult
$Res call({
 String sessionId, String statusLabel, String uiVariant, String statusMessage, bool showWarningBanner, List<StepProgressItem> steps, int? finalScore
});




}
/// @nodoc
class _$AssessmentViewCopyWithImpl<$Res>
    implements $AssessmentViewCopyWith<$Res> {
  _$AssessmentViewCopyWithImpl(this._self, this._then);

  final AssessmentView _self;
  final $Res Function(AssessmentView) _then;

/// Create a copy of AssessmentView
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sessionId = null,Object? statusLabel = null,Object? uiVariant = null,Object? statusMessage = null,Object? showWarningBanner = null,Object? steps = null,Object? finalScore = freezed,}) {
  return _then(_self.copyWith(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,statusLabel: null == statusLabel ? _self.statusLabel : statusLabel // ignore: cast_nullable_to_non_nullable
as String,uiVariant: null == uiVariant ? _self.uiVariant : uiVariant // ignore: cast_nullable_to_non_nullable
as String,statusMessage: null == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String,showWarningBanner: null == showWarningBanner ? _self.showWarningBanner : showWarningBanner // ignore: cast_nullable_to_non_nullable
as bool,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<StepProgressItem>,finalScore: freezed == finalScore ? _self.finalScore : finalScore // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [AssessmentView].
extension AssessmentViewPatterns on AssessmentView {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AssessmentView value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AssessmentView() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AssessmentView value)  $default,){
final _that = this;
switch (_that) {
case _AssessmentView():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AssessmentView value)?  $default,){
final _that = this;
switch (_that) {
case _AssessmentView() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String sessionId,  String statusLabel,  String uiVariant,  String statusMessage,  bool showWarningBanner,  List<StepProgressItem> steps,  int? finalScore)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AssessmentView() when $default != null:
return $default(_that.sessionId,_that.statusLabel,_that.uiVariant,_that.statusMessage,_that.showWarningBanner,_that.steps,_that.finalScore);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String sessionId,  String statusLabel,  String uiVariant,  String statusMessage,  bool showWarningBanner,  List<StepProgressItem> steps,  int? finalScore)  $default,) {final _that = this;
switch (_that) {
case _AssessmentView():
return $default(_that.sessionId,_that.statusLabel,_that.uiVariant,_that.statusMessage,_that.showWarningBanner,_that.steps,_that.finalScore);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String sessionId,  String statusLabel,  String uiVariant,  String statusMessage,  bool showWarningBanner,  List<StepProgressItem> steps,  int? finalScore)?  $default,) {final _that = this;
switch (_that) {
case _AssessmentView() when $default != null:
return $default(_that.sessionId,_that.statusLabel,_that.uiVariant,_that.statusMessage,_that.showWarningBanner,_that.steps,_that.finalScore);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AssessmentView implements AssessmentView {
  const _AssessmentView({required this.sessionId, required this.statusLabel, required this.uiVariant, required this.statusMessage, required this.showWarningBanner, final  List<StepProgressItem> steps = const [], this.finalScore}): _steps = steps;
  factory _AssessmentView.fromJson(Map<String, dynamic> json) => _$AssessmentViewFromJson(json);

@override final  String sessionId;
@override final  String statusLabel;
// e.g. "Analysoidaan..."
@override final  String uiVariant;
// "default", "warning", "error"
@override final  String statusMessage;
// Contextual help text
@override final  bool showWarningBanner;
// Toggle for warning UI
 final  List<StepProgressItem> _steps;
// Toggle for warning UI
@override@JsonKey() List<StepProgressItem> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}

// Progress indicators
@override final  int? finalScore;

/// Create a copy of AssessmentView
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AssessmentViewCopyWith<_AssessmentView> get copyWith => __$AssessmentViewCopyWithImpl<_AssessmentView>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AssessmentViewToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AssessmentView&&(identical(other.sessionId, sessionId) || other.sessionId == sessionId)&&(identical(other.statusLabel, statusLabel) || other.statusLabel == statusLabel)&&(identical(other.uiVariant, uiVariant) || other.uiVariant == uiVariant)&&(identical(other.statusMessage, statusMessage) || other.statusMessage == statusMessage)&&(identical(other.showWarningBanner, showWarningBanner) || other.showWarningBanner == showWarningBanner)&&const DeepCollectionEquality().equals(other._steps, _steps)&&(identical(other.finalScore, finalScore) || other.finalScore == finalScore));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,sessionId,statusLabel,uiVariant,statusMessage,showWarningBanner,const DeepCollectionEquality().hash(_steps),finalScore);

@override
String toString() {
  return 'AssessmentView(sessionId: $sessionId, statusLabel: $statusLabel, uiVariant: $uiVariant, statusMessage: $statusMessage, showWarningBanner: $showWarningBanner, steps: $steps, finalScore: $finalScore)';
}


}

/// @nodoc
abstract mixin class _$AssessmentViewCopyWith<$Res> implements $AssessmentViewCopyWith<$Res> {
  factory _$AssessmentViewCopyWith(_AssessmentView value, $Res Function(_AssessmentView) _then) = __$AssessmentViewCopyWithImpl;
@override @useResult
$Res call({
 String sessionId, String statusLabel, String uiVariant, String statusMessage, bool showWarningBanner, List<StepProgressItem> steps, int? finalScore
});




}
/// @nodoc
class __$AssessmentViewCopyWithImpl<$Res>
    implements _$AssessmentViewCopyWith<$Res> {
  __$AssessmentViewCopyWithImpl(this._self, this._then);

  final _AssessmentView _self;
  final $Res Function(_AssessmentView) _then;

/// Create a copy of AssessmentView
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sessionId = null,Object? statusLabel = null,Object? uiVariant = null,Object? statusMessage = null,Object? showWarningBanner = null,Object? steps = null,Object? finalScore = freezed,}) {
  return _then(_AssessmentView(
sessionId: null == sessionId ? _self.sessionId : sessionId // ignore: cast_nullable_to_non_nullable
as String,statusLabel: null == statusLabel ? _self.statusLabel : statusLabel // ignore: cast_nullable_to_non_nullable
as String,uiVariant: null == uiVariant ? _self.uiVariant : uiVariant // ignore: cast_nullable_to_non_nullable
as String,statusMessage: null == statusMessage ? _self.statusMessage : statusMessage // ignore: cast_nullable_to_non_nullable
as String,showWarningBanner: null == showWarningBanner ? _self.showWarningBanner : showWarningBanner // ignore: cast_nullable_to_non_nullable
as bool,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<StepProgressItem>,finalScore: freezed == finalScore ? _self.finalScore : finalScore // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$StepProgressItem {

 String get id; String get label; String get status;
/// Create a copy of StepProgressItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepProgressItemCopyWith<StepProgressItem> get copyWith => _$StepProgressItemCopyWithImpl<StepProgressItem>(this as StepProgressItem, _$identity);

  /// Serializes this StepProgressItem to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StepProgressItem&&(identical(other.id, id) || other.id == id)&&(identical(other.label, label) || other.label == label)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,label,status);

@override
String toString() {
  return 'StepProgressItem(id: $id, label: $label, status: $status)';
}


}

/// @nodoc
abstract mixin class $StepProgressItemCopyWith<$Res>  {
  factory $StepProgressItemCopyWith(StepProgressItem value, $Res Function(StepProgressItem) _then) = _$StepProgressItemCopyWithImpl;
@useResult
$Res call({
 String id, String label, String status
});




}
/// @nodoc
class _$StepProgressItemCopyWithImpl<$Res>
    implements $StepProgressItemCopyWith<$Res> {
  _$StepProgressItemCopyWithImpl(this._self, this._then);

  final StepProgressItem _self;
  final $Res Function(StepProgressItem) _then;

/// Create a copy of StepProgressItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? label = null,Object? status = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [StepProgressItem].
extension StepProgressItemPatterns on StepProgressItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StepProgressItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StepProgressItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StepProgressItem value)  $default,){
final _that = this;
switch (_that) {
case _StepProgressItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StepProgressItem value)?  $default,){
final _that = this;
switch (_that) {
case _StepProgressItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String label,  String status)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepProgressItem() when $default != null:
return $default(_that.id,_that.label,_that.status);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String label,  String status)  $default,) {final _that = this;
switch (_that) {
case _StepProgressItem():
return $default(_that.id,_that.label,_that.status);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String label,  String status)?  $default,) {final _that = this;
switch (_that) {
case _StepProgressItem() when $default != null:
return $default(_that.id,_that.label,_that.status);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StepProgressItem implements StepProgressItem {
  const _StepProgressItem({required this.id, required this.label, required this.status});
  factory _StepProgressItem.fromJson(Map<String, dynamic> json) => _$StepProgressItemFromJson(json);

@override final  String id;
@override final  String label;
@override final  String status;

/// Create a copy of StepProgressItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StepProgressItemCopyWith<_StepProgressItem> get copyWith => __$StepProgressItemCopyWithImpl<_StepProgressItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StepProgressItemToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _StepProgressItem&&(identical(other.id, id) || other.id == id)&&(identical(other.label, label) || other.label == label)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,label,status);

@override
String toString() {
  return 'StepProgressItem(id: $id, label: $label, status: $status)';
}


}

/// @nodoc
abstract mixin class _$StepProgressItemCopyWith<$Res> implements $StepProgressItemCopyWith<$Res> {
  factory _$StepProgressItemCopyWith(_StepProgressItem value, $Res Function(_StepProgressItem) _then) = __$StepProgressItemCopyWithImpl;
@override @useResult
$Res call({
 String id, String label, String status
});




}
/// @nodoc
class __$StepProgressItemCopyWithImpl<$Res>
    implements _$StepProgressItemCopyWith<$Res> {
  __$StepProgressItemCopyWithImpl(this._self, this._then);

  final _StepProgressItem _self;
  final $Res Function(_StepProgressItem) _then;

/// Create a copy of StepProgressItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? label = null,Object? status = null,}) {
  return _then(_StepProgressItem(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
