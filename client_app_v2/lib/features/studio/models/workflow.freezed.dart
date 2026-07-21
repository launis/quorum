// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$QuestionnaireItem {

 String get questionId; I18nText get question; String get type;
/// Create a copy of QuestionnaireItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$QuestionnaireItemCopyWith<QuestionnaireItem> get copyWith => _$QuestionnaireItemCopyWithImpl<QuestionnaireItem>(this as QuestionnaireItem, _$identity);

  /// Serializes this QuestionnaireItem to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'QuestionnaireItem(questionId: $questionId, question: $question, type: $type)';
}


}

/// @nodoc
abstract mixin class $QuestionnaireItemCopyWith<$Res>  {
  factory $QuestionnaireItemCopyWith(QuestionnaireItem value, $Res Function(QuestionnaireItem) _then) = _$QuestionnaireItemCopyWithImpl;
@useResult
$Res call({
 String questionId, I18nText question, String type
});


$I18nTextCopyWith<$Res> get question;

}
/// @nodoc
class _$QuestionnaireItemCopyWithImpl<$Res>
    implements $QuestionnaireItemCopyWith<$Res> {
  _$QuestionnaireItemCopyWithImpl(this._self, this._then);

  final QuestionnaireItem _self;
  final $Res Function(QuestionnaireItem) _then;

/// Create a copy of QuestionnaireItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? questionId = null,Object? question = null,Object? type = null,}) {
  return _then(_self.copyWith(
questionId: null == questionId ? _self.questionId : questionId // ignore: cast_nullable_to_non_nullable
as String,question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as I18nText,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of QuestionnaireItem
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get question {
  
  return $I18nTextCopyWith<$Res>(_self.question, (value) {
    return _then(_self.copyWith(question: value));
  });
}
}


/// Adds pattern-matching-related methods to [QuestionnaireItem].
extension QuestionnaireItemPatterns on QuestionnaireItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _QuestionnaireItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _QuestionnaireItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _QuestionnaireItem value)  $default,){
final _that = this;
switch (_that) {
case _QuestionnaireItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _QuestionnaireItem value)?  $default,){
final _that = this;
switch (_that) {
case _QuestionnaireItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String questionId,  I18nText question,  String type)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _QuestionnaireItem() when $default != null:
return $default(_that.questionId,_that.question,_that.type);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String questionId,  I18nText question,  String type)  $default,) {final _that = this;
switch (_that) {
case _QuestionnaireItem():
return $default(_that.questionId,_that.question,_that.type);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String questionId,  I18nText question,  String type)?  $default,) {final _that = this;
switch (_that) {
case _QuestionnaireItem() when $default != null:
return $default(_that.questionId,_that.question,_that.type);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _QuestionnaireItem extends QuestionnaireItem {
  const _QuestionnaireItem({required this.questionId, required this.question, required this.type}): super._();
  factory _QuestionnaireItem.fromJson(Map<String, dynamic> json) => _$QuestionnaireItemFromJson(json);

@override final  String questionId;
@override final  I18nText question;
@override final  String type;

/// Create a copy of QuestionnaireItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$QuestionnaireItemCopyWith<_QuestionnaireItem> get copyWith => __$QuestionnaireItemCopyWithImpl<_QuestionnaireItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$QuestionnaireItemToJson(this, );
}



@override
String toString() {
  return 'QuestionnaireItem(questionId: $questionId, question: $question, type: $type)';
}


}

/// @nodoc
abstract mixin class _$QuestionnaireItemCopyWith<$Res> implements $QuestionnaireItemCopyWith<$Res> {
  factory _$QuestionnaireItemCopyWith(_QuestionnaireItem value, $Res Function(_QuestionnaireItem) _then) = __$QuestionnaireItemCopyWithImpl;
@override @useResult
$Res call({
 String questionId, I18nText question, String type
});


@override $I18nTextCopyWith<$Res> get question;

}
/// @nodoc
class __$QuestionnaireItemCopyWithImpl<$Res>
    implements _$QuestionnaireItemCopyWith<$Res> {
  __$QuestionnaireItemCopyWithImpl(this._self, this._then);

  final _QuestionnaireItem _self;
  final $Res Function(_QuestionnaireItem) _then;

/// Create a copy of QuestionnaireItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? questionId = null,Object? question = null,Object? type = null,}) {
  return _then(_QuestionnaireItem(
questionId: null == questionId ? _self.questionId : questionId // ignore: cast_nullable_to_non_nullable
as String,question: null == question ? _self.question : question // ignore: cast_nullable_to_non_nullable
as I18nText,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of QuestionnaireItem
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get question {
  
  return $I18nTextCopyWith<$Res>(_self.question, (value) {
    return _then(_self.copyWith(question: value));
  });
}
}


/// @nodoc
mixin _$ExpectedInput {

 String get inputKey; I18nText get label; bool get required; bool get isChatHistory; List<String> get inputModes; I18nText get description; bool get scanForPerformativePatterns; String? get aiDescription; List<QuestionnaireItem> get questionnaireDefinition;
/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExpectedInputCopyWith<ExpectedInput> get copyWith => _$ExpectedInputCopyWithImpl<ExpectedInput>(this as ExpectedInput, _$identity);

  /// Serializes this ExpectedInput to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExpectedInput(inputKey: $inputKey, label: $label, required: $required, isChatHistory: $isChatHistory, inputModes: $inputModes, description: $description, scanForPerformativePatterns: $scanForPerformativePatterns, aiDescription: $aiDescription, questionnaireDefinition: $questionnaireDefinition)';
}


}

/// @nodoc
abstract mixin class $ExpectedInputCopyWith<$Res>  {
  factory $ExpectedInputCopyWith(ExpectedInput value, $Res Function(ExpectedInput) _then) = _$ExpectedInputCopyWithImpl;
@useResult
$Res call({
 String inputKey, I18nText label, bool required, bool isChatHistory, List<String> inputModes, I18nText description, bool scanForPerformativePatterns, String? aiDescription, List<QuestionnaireItem> questionnaireDefinition
});


$I18nTextCopyWith<$Res> get label;$I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class _$ExpectedInputCopyWithImpl<$Res>
    implements $ExpectedInputCopyWith<$Res> {
  _$ExpectedInputCopyWithImpl(this._self, this._then);

  final ExpectedInput _self;
  final $Res Function(ExpectedInput) _then;

/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? inputKey = null,Object? label = null,Object? required = null,Object? isChatHistory = null,Object? inputModes = null,Object? description = null,Object? scanForPerformativePatterns = null,Object? aiDescription = freezed,Object? questionnaireDefinition = null,}) {
  return _then(_self.copyWith(
inputKey: null == inputKey ? _self.inputKey : inputKey // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,isChatHistory: null == isChatHistory ? _self.isChatHistory : isChatHistory // ignore: cast_nullable_to_non_nullable
as bool,inputModes: null == inputModes ? _self.inputModes : inputModes // ignore: cast_nullable_to_non_nullable
as List<String>,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,scanForPerformativePatterns: null == scanForPerformativePatterns ? _self.scanForPerformativePatterns : scanForPerformativePatterns // ignore: cast_nullable_to_non_nullable
as bool,aiDescription: freezed == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String?,questionnaireDefinition: null == questionnaireDefinition ? _self.questionnaireDefinition : questionnaireDefinition // ignore: cast_nullable_to_non_nullable
as List<QuestionnaireItem>,
  ));
}
/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// Adds pattern-matching-related methods to [ExpectedInput].
extension ExpectedInputPatterns on ExpectedInput {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExpectedInput value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExpectedInput() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExpectedInput value)  $default,){
final _that = this;
switch (_that) {
case _ExpectedInput():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExpectedInput value)?  $default,){
final _that = this;
switch (_that) {
case _ExpectedInput() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String inputKey,  I18nText label,  bool required,  bool isChatHistory,  List<String> inputModes,  I18nText description,  bool scanForPerformativePatterns,  String? aiDescription,  List<QuestionnaireItem> questionnaireDefinition)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExpectedInput() when $default != null:
return $default(_that.inputKey,_that.label,_that.required,_that.isChatHistory,_that.inputModes,_that.description,_that.scanForPerformativePatterns,_that.aiDescription,_that.questionnaireDefinition);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String inputKey,  I18nText label,  bool required,  bool isChatHistory,  List<String> inputModes,  I18nText description,  bool scanForPerformativePatterns,  String? aiDescription,  List<QuestionnaireItem> questionnaireDefinition)  $default,) {final _that = this;
switch (_that) {
case _ExpectedInput():
return $default(_that.inputKey,_that.label,_that.required,_that.isChatHistory,_that.inputModes,_that.description,_that.scanForPerformativePatterns,_that.aiDescription,_that.questionnaireDefinition);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String inputKey,  I18nText label,  bool required,  bool isChatHistory,  List<String> inputModes,  I18nText description,  bool scanForPerformativePatterns,  String? aiDescription,  List<QuestionnaireItem> questionnaireDefinition)?  $default,) {final _that = this;
switch (_that) {
case _ExpectedInput() when $default != null:
return $default(_that.inputKey,_that.label,_that.required,_that.isChatHistory,_that.inputModes,_that.description,_that.scanForPerformativePatterns,_that.aiDescription,_that.questionnaireDefinition);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExpectedInput extends ExpectedInput {
  const _ExpectedInput({required this.inputKey, required this.label, required this.required, this.isChatHistory = false, final  List<String> inputModes = const [], required this.description, this.scanForPerformativePatterns = false, this.aiDescription, final  List<QuestionnaireItem> questionnaireDefinition = const []}): _inputModes = inputModes,_questionnaireDefinition = questionnaireDefinition,super._();
  factory _ExpectedInput.fromJson(Map<String, dynamic> json) => _$ExpectedInputFromJson(json);

@override final  String inputKey;
@override final  I18nText label;
@override final  bool required;
@override@JsonKey() final  bool isChatHistory;
 final  List<String> _inputModes;
@override@JsonKey() List<String> get inputModes {
  if (_inputModes is EqualUnmodifiableListView) return _inputModes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_inputModes);
}

@override final  I18nText description;
@override@JsonKey() final  bool scanForPerformativePatterns;
@override final  String? aiDescription;
 final  List<QuestionnaireItem> _questionnaireDefinition;
@override@JsonKey() List<QuestionnaireItem> get questionnaireDefinition {
  if (_questionnaireDefinition is EqualUnmodifiableListView) return _questionnaireDefinition;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_questionnaireDefinition);
}


/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExpectedInputCopyWith<_ExpectedInput> get copyWith => __$ExpectedInputCopyWithImpl<_ExpectedInput>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExpectedInputToJson(this, );
}



@override
String toString() {
  return 'ExpectedInput(inputKey: $inputKey, label: $label, required: $required, isChatHistory: $isChatHistory, inputModes: $inputModes, description: $description, scanForPerformativePatterns: $scanForPerformativePatterns, aiDescription: $aiDescription, questionnaireDefinition: $questionnaireDefinition)';
}


}

/// @nodoc
abstract mixin class _$ExpectedInputCopyWith<$Res> implements $ExpectedInputCopyWith<$Res> {
  factory _$ExpectedInputCopyWith(_ExpectedInput value, $Res Function(_ExpectedInput) _then) = __$ExpectedInputCopyWithImpl;
@override @useResult
$Res call({
 String inputKey, I18nText label, bool required, bool isChatHistory, List<String> inputModes, I18nText description, bool scanForPerformativePatterns, String? aiDescription, List<QuestionnaireItem> questionnaireDefinition
});


@override $I18nTextCopyWith<$Res> get label;@override $I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class __$ExpectedInputCopyWithImpl<$Res>
    implements _$ExpectedInputCopyWith<$Res> {
  __$ExpectedInputCopyWithImpl(this._self, this._then);

  final _ExpectedInput _self;
  final $Res Function(_ExpectedInput) _then;

/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? inputKey = null,Object? label = null,Object? required = null,Object? isChatHistory = null,Object? inputModes = null,Object? description = null,Object? scanForPerformativePatterns = null,Object? aiDescription = freezed,Object? questionnaireDefinition = null,}) {
  return _then(_ExpectedInput(
inputKey: null == inputKey ? _self.inputKey : inputKey // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,isChatHistory: null == isChatHistory ? _self.isChatHistory : isChatHistory // ignore: cast_nullable_to_non_nullable
as bool,inputModes: null == inputModes ? _self._inputModes : inputModes // ignore: cast_nullable_to_non_nullable
as List<String>,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,scanForPerformativePatterns: null == scanForPerformativePatterns ? _self.scanForPerformativePatterns : scanForPerformativePatterns // ignore: cast_nullable_to_non_nullable
as bool,aiDescription: freezed == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String?,questionnaireDefinition: null == questionnaireDefinition ? _self._questionnaireDefinition : questionnaireDefinition // ignore: cast_nullable_to_non_nullable
as List<QuestionnaireItem>,
  ));
}

/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}/// Create a copy of ExpectedInput
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
mixin _$StepRule {

@StrictOpaqueIdConverter() String get id;@StrictOpaqueIdConverter() String get taskBlueprint; List<String> get dependsOn; Map<String, String> get inputMappings;@JsonKey(name: 'expected_sdui_type') SduiBlockType? get expectedSduiType; double get uiPosX; double get uiPosY;
/// Create a copy of StepRule
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepRuleCopyWith<StepRule> get copyWith => _$StepRuleCopyWithImpl<StepRule>(this as StepRule, _$identity);

  /// Serializes this StepRule to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'StepRule(id: $id, taskBlueprint: $taskBlueprint, dependsOn: $dependsOn, inputMappings: $inputMappings, expectedSduiType: $expectedSduiType, uiPosX: $uiPosX, uiPosY: $uiPosY)';
}


}

/// @nodoc
abstract mixin class $StepRuleCopyWith<$Res>  {
  factory $StepRuleCopyWith(StepRule value, $Res Function(StepRule) _then) = _$StepRuleCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter() String taskBlueprint, List<String> dependsOn, Map<String, String> inputMappings,@JsonKey(name: 'expected_sdui_type') SduiBlockType? expectedSduiType, double uiPosX, double uiPosY
});




}
/// @nodoc
class _$StepRuleCopyWithImpl<$Res>
    implements $StepRuleCopyWith<$Res> {
  _$StepRuleCopyWithImpl(this._self, this._then);

  final StepRule _self;
  final $Res Function(StepRule) _then;

/// Create a copy of StepRule
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? taskBlueprint = null,Object? dependsOn = null,Object? inputMappings = null,Object? expectedSduiType = freezed,Object? uiPosX = null,Object? uiPosY = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,taskBlueprint: null == taskBlueprint ? _self.taskBlueprint : taskBlueprint // ignore: cast_nullable_to_non_nullable
as String,dependsOn: null == dependsOn ? _self.dependsOn : dependsOn // ignore: cast_nullable_to_non_nullable
as List<String>,inputMappings: null == inputMappings ? _self.inputMappings : inputMappings // ignore: cast_nullable_to_non_nullable
as Map<String, String>,expectedSduiType: freezed == expectedSduiType ? _self.expectedSduiType : expectedSduiType // ignore: cast_nullable_to_non_nullable
as SduiBlockType?,uiPosX: null == uiPosX ? _self.uiPosX : uiPosX // ignore: cast_nullable_to_non_nullable
as double,uiPosY: null == uiPosY ? _self.uiPosY : uiPosY // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [StepRule].
extension StepRulePatterns on StepRule {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StepRule value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StepRule() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StepRule value)  $default,){
final _that = this;
switch (_that) {
case _StepRule():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StepRule value)?  $default,){
final _that = this;
switch (_that) {
case _StepRule() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()  String taskBlueprint,  List<String> dependsOn,  Map<String, String> inputMappings, @JsonKey(name: 'expected_sdui_type')  SduiBlockType? expectedSduiType,  double uiPosX,  double uiPosY)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepRule() when $default != null:
return $default(_that.id,_that.taskBlueprint,_that.dependsOn,_that.inputMappings,_that.expectedSduiType,_that.uiPosX,_that.uiPosY);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()  String taskBlueprint,  List<String> dependsOn,  Map<String, String> inputMappings, @JsonKey(name: 'expected_sdui_type')  SduiBlockType? expectedSduiType,  double uiPosX,  double uiPosY)  $default,) {final _that = this;
switch (_that) {
case _StepRule():
return $default(_that.id,_that.taskBlueprint,_that.dependsOn,_that.inputMappings,_that.expectedSduiType,_that.uiPosX,_that.uiPosY);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()  String taskBlueprint,  List<String> dependsOn,  Map<String, String> inputMappings, @JsonKey(name: 'expected_sdui_type')  SduiBlockType? expectedSduiType,  double uiPosX,  double uiPosY)?  $default,) {final _that = this;
switch (_that) {
case _StepRule() when $default != null:
return $default(_that.id,_that.taskBlueprint,_that.dependsOn,_that.inputMappings,_that.expectedSduiType,_that.uiPosX,_that.uiPosY);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _StepRule extends StepRule {
  const _StepRule({@StrictOpaqueIdConverter() required this.id, @StrictOpaqueIdConverter() required this.taskBlueprint, final  List<String> dependsOn = const [], final  Map<String, String> inputMappings = const {}, @JsonKey(name: 'expected_sdui_type') this.expectedSduiType, this.uiPosX = 0.0, this.uiPosY = 0.0}): _dependsOn = dependsOn,_inputMappings = inputMappings,super._();
  factory _StepRule.fromJson(Map<String, dynamic> json) => _$StepRuleFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@StrictOpaqueIdConverter() final  String taskBlueprint;
 final  List<String> _dependsOn;
@override@JsonKey() List<String> get dependsOn {
  if (_dependsOn is EqualUnmodifiableListView) return _dependsOn;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dependsOn);
}

 final  Map<String, String> _inputMappings;
@override@JsonKey() Map<String, String> get inputMappings {
  if (_inputMappings is EqualUnmodifiableMapView) return _inputMappings;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputMappings);
}

@override@JsonKey(name: 'expected_sdui_type') final  SduiBlockType? expectedSduiType;
@override@JsonKey() final  double uiPosX;
@override@JsonKey() final  double uiPosY;

/// Create a copy of StepRule
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StepRuleCopyWith<_StepRule> get copyWith => __$StepRuleCopyWithImpl<_StepRule>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StepRuleToJson(this, );
}



@override
String toString() {
  return 'StepRule(id: $id, taskBlueprint: $taskBlueprint, dependsOn: $dependsOn, inputMappings: $inputMappings, expectedSduiType: $expectedSduiType, uiPosX: $uiPosX, uiPosY: $uiPosY)';
}


}

/// @nodoc
abstract mixin class _$StepRuleCopyWith<$Res> implements $StepRuleCopyWith<$Res> {
  factory _$StepRuleCopyWith(_StepRule value, $Res Function(_StepRule) _then) = __$StepRuleCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter() String taskBlueprint, List<String> dependsOn, Map<String, String> inputMappings,@JsonKey(name: 'expected_sdui_type') SduiBlockType? expectedSduiType, double uiPosX, double uiPosY
});




}
/// @nodoc
class __$StepRuleCopyWithImpl<$Res>
    implements _$StepRuleCopyWith<$Res> {
  __$StepRuleCopyWithImpl(this._self, this._then);

  final _StepRule _self;
  final $Res Function(_StepRule) _then;

/// Create a copy of StepRule
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? taskBlueprint = null,Object? dependsOn = null,Object? inputMappings = null,Object? expectedSduiType = freezed,Object? uiPosX = null,Object? uiPosY = null,}) {
  return _then(_StepRule(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,taskBlueprint: null == taskBlueprint ? _self.taskBlueprint : taskBlueprint // ignore: cast_nullable_to_non_nullable
as String,dependsOn: null == dependsOn ? _self._dependsOn : dependsOn // ignore: cast_nullable_to_non_nullable
as List<String>,inputMappings: null == inputMappings ? _self._inputMappings : inputMappings // ignore: cast_nullable_to_non_nullable
as Map<String, String>,expectedSduiType: freezed == expectedSduiType ? _self.expectedSduiType : expectedSduiType // ignore: cast_nullable_to_non_nullable
as SduiBlockType?,uiPosX: null == uiPosX ? _self.uiPosX : uiPosX // ignore: cast_nullable_to_non_nullable
as double,uiPosY: null == uiPosY ? _self.uiPosY : uiPosY // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}

NodeStrategy _$NodeStrategyFromJson(
  Map<String, dynamic> json
) {
        switch (json['type']) {
                  case 'llm':
          return NodeStrategyLlm.fromJson(
            json
          );
                case 'logic':
          return NodeStrategyLogic.fromJson(
            json
          );
        
          default:
            throw CheckedFromJsonException(
  json,
  'type',
  'NodeStrategy',
  'Invalid union type "${json['type']}"!'
);
        }
      
}

/// @nodoc
mixin _$NodeStrategy {

@StrictOpaqueIdConverter() String get id; String get slug; I18nText get name; I18nText? get description; String? get hook;@StrictOpaqueIdConverter() String? get roleBlockId;@StrictOpaqueIdConverter() String? get extractionProtocolBlockId;@StrictOpaqueIdConverter() String? get executionPersonaBlockId; List<String> get criteriaBlockIds; List<String> get preHooks; List<String> get postHooks; String get safety; List<String> get allowedMcpTools; List<String> get expectedInputs; Map<String, dynamic>? get outputSchema; String? get modelStrategy; String? get organizationId;
/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NodeStrategyCopyWith<NodeStrategy> get copyWith => _$NodeStrategyCopyWithImpl<NodeStrategy>(this as NodeStrategy, _$identity);

  /// Serializes this NodeStrategy to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodeStrategy&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.hook, hook) || other.hook == hook)&&(identical(other.roleBlockId, roleBlockId) || other.roleBlockId == roleBlockId)&&(identical(other.extractionProtocolBlockId, extractionProtocolBlockId) || other.extractionProtocolBlockId == extractionProtocolBlockId)&&(identical(other.executionPersonaBlockId, executionPersonaBlockId) || other.executionPersonaBlockId == executionPersonaBlockId)&&const DeepCollectionEquality().equals(other.criteriaBlockIds, criteriaBlockIds)&&const DeepCollectionEquality().equals(other.preHooks, preHooks)&&const DeepCollectionEquality().equals(other.postHooks, postHooks)&&(identical(other.safety, safety) || other.safety == safety)&&const DeepCollectionEquality().equals(other.allowedMcpTools, allowedMcpTools)&&const DeepCollectionEquality().equals(other.expectedInputs, expectedInputs)&&const DeepCollectionEquality().equals(other.outputSchema, outputSchema)&&(identical(other.modelStrategy, modelStrategy) || other.modelStrategy == modelStrategy)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,name,description,hook,roleBlockId,extractionProtocolBlockId,executionPersonaBlockId,const DeepCollectionEquality().hash(criteriaBlockIds),const DeepCollectionEquality().hash(preHooks),const DeepCollectionEquality().hash(postHooks),safety,const DeepCollectionEquality().hash(allowedMcpTools),const DeepCollectionEquality().hash(expectedInputs),const DeepCollectionEquality().hash(outputSchema),modelStrategy,organizationId);

@override
String toString() {
  return 'NodeStrategy(id: $id, slug: $slug, name: $name, description: $description, hook: $hook, roleBlockId: $roleBlockId, extractionProtocolBlockId: $extractionProtocolBlockId, executionPersonaBlockId: $executionPersonaBlockId, criteriaBlockIds: $criteriaBlockIds, preHooks: $preHooks, postHooks: $postHooks, safety: $safety, allowedMcpTools: $allowedMcpTools, expectedInputs: $expectedInputs, outputSchema: $outputSchema, modelStrategy: $modelStrategy, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class $NodeStrategyCopyWith<$Res>  {
  factory $NodeStrategyCopyWith(NodeStrategy value, $Res Function(NodeStrategy) _then) = _$NodeStrategyCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText? description, String hook,@StrictOpaqueIdConverter() String? roleBlockId,@StrictOpaqueIdConverter() String? extractionProtocolBlockId,@StrictOpaqueIdConverter() String? executionPersonaBlockId, List<String> criteriaBlockIds, List<String> preHooks, List<String> postHooks, String safety, List<String> allowedMcpTools, List<String> expectedInputs, Map<String, dynamic>? outputSchema, String? modelStrategy, String? organizationId
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class _$NodeStrategyCopyWithImpl<$Res>
    implements $NodeStrategyCopyWith<$Res> {
  _$NodeStrategyCopyWithImpl(this._self, this._then);

  final NodeStrategy _self;
  final $Res Function(NodeStrategy) _then;

/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = freezed,Object? hook = null,Object? roleBlockId = freezed,Object? extractionProtocolBlockId = freezed,Object? executionPersonaBlockId = freezed,Object? criteriaBlockIds = null,Object? preHooks = null,Object? postHooks = null,Object? safety = null,Object? allowedMcpTools = null,Object? expectedInputs = null,Object? outputSchema = freezed,Object? modelStrategy = freezed,Object? organizationId = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,hook: null == hook ? _self.hook! : hook // ignore: cast_nullable_to_non_nullable
as String,roleBlockId: freezed == roleBlockId ? _self.roleBlockId : roleBlockId // ignore: cast_nullable_to_non_nullable
as String?,extractionProtocolBlockId: freezed == extractionProtocolBlockId ? _self.extractionProtocolBlockId : extractionProtocolBlockId // ignore: cast_nullable_to_non_nullable
as String?,executionPersonaBlockId: freezed == executionPersonaBlockId ? _self.executionPersonaBlockId : executionPersonaBlockId // ignore: cast_nullable_to_non_nullable
as String?,criteriaBlockIds: null == criteriaBlockIds ? _self.criteriaBlockIds : criteriaBlockIds // ignore: cast_nullable_to_non_nullable
as List<String>,preHooks: null == preHooks ? _self.preHooks : preHooks // ignore: cast_nullable_to_non_nullable
as List<String>,postHooks: null == postHooks ? _self.postHooks : postHooks // ignore: cast_nullable_to_non_nullable
as List<String>,safety: null == safety ? _self.safety : safety // ignore: cast_nullable_to_non_nullable
as String,allowedMcpTools: null == allowedMcpTools ? _self.allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,expectedInputs: null == expectedInputs ? _self.expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<String>,outputSchema: freezed == outputSchema ? _self.outputSchema : outputSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of NodeStrategy
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


/// Adds pattern-matching-related methods to [NodeStrategy].
extension NodeStrategyPatterns on NodeStrategy {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( NodeStrategyLlm value)?  llm,TResult Function( NodeStrategyLogic value)?  logic,required TResult orElse(),}){
final _that = this;
switch (_that) {
case NodeStrategyLlm() when llm != null:
return llm(_that);case NodeStrategyLogic() when logic != null:
return logic(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( NodeStrategyLlm value)  llm,required TResult Function( NodeStrategyLogic value)  logic,}){
final _that = this;
switch (_that) {
case NodeStrategyLlm():
return llm(_that);case NodeStrategyLogic():
return logic(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( NodeStrategyLlm value)?  llm,TResult? Function( NodeStrategyLogic value)?  logic,}){
final _that = this;
switch (_that) {
case NodeStrategyLlm() when llm != null:
return llm(_that);case NodeStrategyLogic() when logic != null:
return logic(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String? hook, @StrictOpaqueIdConverter()  String? roleBlockId, @StrictOpaqueIdConverter()  String? extractionProtocolBlockId, @StrictOpaqueIdConverter()  String? executionPersonaBlockId,  List<String> criteriaBlockIds,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  List<String> expectedInputs,  Map<String, dynamic>? outputSchema,  String? modelStrategy,  String? organizationId)?  llm,TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String hook, @StrictOpaqueIdConverter()  String? roleBlockId, @StrictOpaqueIdConverter()  String? extractionProtocolBlockId, @StrictOpaqueIdConverter()  String? executionPersonaBlockId,  List<String> criteriaBlockIds,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  List<String> expectedInputs,  Map<String, dynamic>? outputSchema,  String? modelStrategy,  String? organizationId)?  logic,required TResult orElse(),}) {final _that = this;
switch (_that) {
case NodeStrategyLlm() when llm != null:
return llm(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.roleBlockId,_that.extractionProtocolBlockId,_that.executionPersonaBlockId,_that.criteriaBlockIds,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.expectedInputs,_that.outputSchema,_that.modelStrategy,_that.organizationId);case NodeStrategyLogic() when logic != null:
return logic(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.roleBlockId,_that.extractionProtocolBlockId,_that.executionPersonaBlockId,_that.criteriaBlockIds,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.expectedInputs,_that.outputSchema,_that.modelStrategy,_that.organizationId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String? hook, @StrictOpaqueIdConverter()  String? roleBlockId, @StrictOpaqueIdConverter()  String? extractionProtocolBlockId, @StrictOpaqueIdConverter()  String? executionPersonaBlockId,  List<String> criteriaBlockIds,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  List<String> expectedInputs,  Map<String, dynamic>? outputSchema,  String? modelStrategy,  String? organizationId)  llm,required TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String hook, @StrictOpaqueIdConverter()  String? roleBlockId, @StrictOpaqueIdConverter()  String? extractionProtocolBlockId, @StrictOpaqueIdConverter()  String? executionPersonaBlockId,  List<String> criteriaBlockIds,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  List<String> expectedInputs,  Map<String, dynamic>? outputSchema,  String? modelStrategy,  String? organizationId)  logic,}) {final _that = this;
switch (_that) {
case NodeStrategyLlm():
return llm(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.roleBlockId,_that.extractionProtocolBlockId,_that.executionPersonaBlockId,_that.criteriaBlockIds,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.expectedInputs,_that.outputSchema,_that.modelStrategy,_that.organizationId);case NodeStrategyLogic():
return logic(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.roleBlockId,_that.extractionProtocolBlockId,_that.executionPersonaBlockId,_that.criteriaBlockIds,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.expectedInputs,_that.outputSchema,_that.modelStrategy,_that.organizationId);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String? hook, @StrictOpaqueIdConverter()  String? roleBlockId, @StrictOpaqueIdConverter()  String? extractionProtocolBlockId, @StrictOpaqueIdConverter()  String? executionPersonaBlockId,  List<String> criteriaBlockIds,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  List<String> expectedInputs,  Map<String, dynamic>? outputSchema,  String? modelStrategy,  String? organizationId)?  llm,TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String hook, @StrictOpaqueIdConverter()  String? roleBlockId, @StrictOpaqueIdConverter()  String? extractionProtocolBlockId, @StrictOpaqueIdConverter()  String? executionPersonaBlockId,  List<String> criteriaBlockIds,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  List<String> expectedInputs,  Map<String, dynamic>? outputSchema,  String? modelStrategy,  String? organizationId)?  logic,}) {final _that = this;
switch (_that) {
case NodeStrategyLlm() when llm != null:
return llm(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.roleBlockId,_that.extractionProtocolBlockId,_that.executionPersonaBlockId,_that.criteriaBlockIds,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.expectedInputs,_that.outputSchema,_that.modelStrategy,_that.organizationId);case NodeStrategyLogic() when logic != null:
return logic(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.roleBlockId,_that.extractionProtocolBlockId,_that.executionPersonaBlockId,_that.criteriaBlockIds,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.expectedInputs,_that.outputSchema,_that.modelStrategy,_that.organizationId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class NodeStrategyLlm extends NodeStrategy {
  const NodeStrategyLlm({@StrictOpaqueIdConverter() required this.id, required this.slug, required this.name, this.description, this.hook, @StrictOpaqueIdConverter() this.roleBlockId, @StrictOpaqueIdConverter() this.extractionProtocolBlockId, @StrictOpaqueIdConverter() this.executionPersonaBlockId, final  List<String> criteriaBlockIds = const [], final  List<String> preHooks = const [], final  List<String> postHooks = const [], this.safety = 'safe', final  List<String> allowedMcpTools = const [], final  List<String> expectedInputs = const [], final  Map<String, dynamic>? outputSchema, this.modelStrategy, this.organizationId, final  String? $type}): _criteriaBlockIds = criteriaBlockIds,_preHooks = preHooks,_postHooks = postHooks,_allowedMcpTools = allowedMcpTools,_expectedInputs = expectedInputs,_outputSchema = outputSchema,$type = $type ?? 'llm',super._();
  factory NodeStrategyLlm.fromJson(Map<String, dynamic> json) => _$NodeStrategyLlmFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override final  I18nText name;
@override final  I18nText? description;
@override final  String? hook;
@override@StrictOpaqueIdConverter() final  String? roleBlockId;
@override@StrictOpaqueIdConverter() final  String? extractionProtocolBlockId;
@override@StrictOpaqueIdConverter() final  String? executionPersonaBlockId;
 final  List<String> _criteriaBlockIds;
@override@JsonKey() List<String> get criteriaBlockIds {
  if (_criteriaBlockIds is EqualUnmodifiableListView) return _criteriaBlockIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_criteriaBlockIds);
}

 final  List<String> _preHooks;
@override@JsonKey() List<String> get preHooks {
  if (_preHooks is EqualUnmodifiableListView) return _preHooks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_preHooks);
}

 final  List<String> _postHooks;
@override@JsonKey() List<String> get postHooks {
  if (_postHooks is EqualUnmodifiableListView) return _postHooks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_postHooks);
}

@override@JsonKey() final  String safety;
 final  List<String> _allowedMcpTools;
@override@JsonKey() List<String> get allowedMcpTools {
  if (_allowedMcpTools is EqualUnmodifiableListView) return _allowedMcpTools;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedMcpTools);
}

 final  List<String> _expectedInputs;
@override@JsonKey() List<String> get expectedInputs {
  if (_expectedInputs is EqualUnmodifiableListView) return _expectedInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_expectedInputs);
}

 final  Map<String, dynamic>? _outputSchema;
@override Map<String, dynamic>? get outputSchema {
  final value = _outputSchema;
  if (value == null) return null;
  if (_outputSchema is EqualUnmodifiableMapView) return _outputSchema;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? modelStrategy;
@override final  String? organizationId;

@JsonKey(name: 'type')
final String $type;


/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NodeStrategyLlmCopyWith<NodeStrategyLlm> get copyWith => _$NodeStrategyLlmCopyWithImpl<NodeStrategyLlm>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NodeStrategyLlmToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodeStrategyLlm&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.hook, hook) || other.hook == hook)&&(identical(other.roleBlockId, roleBlockId) || other.roleBlockId == roleBlockId)&&(identical(other.extractionProtocolBlockId, extractionProtocolBlockId) || other.extractionProtocolBlockId == extractionProtocolBlockId)&&(identical(other.executionPersonaBlockId, executionPersonaBlockId) || other.executionPersonaBlockId == executionPersonaBlockId)&&const DeepCollectionEquality().equals(other._criteriaBlockIds, _criteriaBlockIds)&&const DeepCollectionEquality().equals(other._preHooks, _preHooks)&&const DeepCollectionEquality().equals(other._postHooks, _postHooks)&&(identical(other.safety, safety) || other.safety == safety)&&const DeepCollectionEquality().equals(other._allowedMcpTools, _allowedMcpTools)&&const DeepCollectionEquality().equals(other._expectedInputs, _expectedInputs)&&const DeepCollectionEquality().equals(other._outputSchema, _outputSchema)&&(identical(other.modelStrategy, modelStrategy) || other.modelStrategy == modelStrategy)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,name,description,hook,roleBlockId,extractionProtocolBlockId,executionPersonaBlockId,const DeepCollectionEquality().hash(_criteriaBlockIds),const DeepCollectionEquality().hash(_preHooks),const DeepCollectionEquality().hash(_postHooks),safety,const DeepCollectionEquality().hash(_allowedMcpTools),const DeepCollectionEquality().hash(_expectedInputs),const DeepCollectionEquality().hash(_outputSchema),modelStrategy,organizationId);

@override
String toString() {
  return 'NodeStrategy.llm(id: $id, slug: $slug, name: $name, description: $description, hook: $hook, roleBlockId: $roleBlockId, extractionProtocolBlockId: $extractionProtocolBlockId, executionPersonaBlockId: $executionPersonaBlockId, criteriaBlockIds: $criteriaBlockIds, preHooks: $preHooks, postHooks: $postHooks, safety: $safety, allowedMcpTools: $allowedMcpTools, expectedInputs: $expectedInputs, outputSchema: $outputSchema, modelStrategy: $modelStrategy, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class $NodeStrategyLlmCopyWith<$Res> implements $NodeStrategyCopyWith<$Res> {
  factory $NodeStrategyLlmCopyWith(NodeStrategyLlm value, $Res Function(NodeStrategyLlm) _then) = _$NodeStrategyLlmCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText? description, String? hook,@StrictOpaqueIdConverter() String? roleBlockId,@StrictOpaqueIdConverter() String? extractionProtocolBlockId,@StrictOpaqueIdConverter() String? executionPersonaBlockId, List<String> criteriaBlockIds, List<String> preHooks, List<String> postHooks, String safety, List<String> allowedMcpTools, List<String> expectedInputs, Map<String, dynamic>? outputSchema, String? modelStrategy, String? organizationId
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class _$NodeStrategyLlmCopyWithImpl<$Res>
    implements $NodeStrategyLlmCopyWith<$Res> {
  _$NodeStrategyLlmCopyWithImpl(this._self, this._then);

  final NodeStrategyLlm _self;
  final $Res Function(NodeStrategyLlm) _then;

/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = freezed,Object? hook = freezed,Object? roleBlockId = freezed,Object? extractionProtocolBlockId = freezed,Object? executionPersonaBlockId = freezed,Object? criteriaBlockIds = null,Object? preHooks = null,Object? postHooks = null,Object? safety = null,Object? allowedMcpTools = null,Object? expectedInputs = null,Object? outputSchema = freezed,Object? modelStrategy = freezed,Object? organizationId = freezed,}) {
  return _then(NodeStrategyLlm(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,hook: freezed == hook ? _self.hook : hook // ignore: cast_nullable_to_non_nullable
as String?,roleBlockId: freezed == roleBlockId ? _self.roleBlockId : roleBlockId // ignore: cast_nullable_to_non_nullable
as String?,extractionProtocolBlockId: freezed == extractionProtocolBlockId ? _self.extractionProtocolBlockId : extractionProtocolBlockId // ignore: cast_nullable_to_non_nullable
as String?,executionPersonaBlockId: freezed == executionPersonaBlockId ? _self.executionPersonaBlockId : executionPersonaBlockId // ignore: cast_nullable_to_non_nullable
as String?,criteriaBlockIds: null == criteriaBlockIds ? _self._criteriaBlockIds : criteriaBlockIds // ignore: cast_nullable_to_non_nullable
as List<String>,preHooks: null == preHooks ? _self._preHooks : preHooks // ignore: cast_nullable_to_non_nullable
as List<String>,postHooks: null == postHooks ? _self._postHooks : postHooks // ignore: cast_nullable_to_non_nullable
as List<String>,safety: null == safety ? _self.safety : safety // ignore: cast_nullable_to_non_nullable
as String,allowedMcpTools: null == allowedMcpTools ? _self._allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,expectedInputs: null == expectedInputs ? _self._expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<String>,outputSchema: freezed == outputSchema ? _self._outputSchema : outputSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of NodeStrategy
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

@JsonSerializable(disallowUnrecognizedKeys: true)
class NodeStrategyLogic extends NodeStrategy {
  const NodeStrategyLogic({@StrictOpaqueIdConverter() required this.id, required this.slug, required this.name, this.description, required this.hook, @StrictOpaqueIdConverter() this.roleBlockId, @StrictOpaqueIdConverter() this.extractionProtocolBlockId, @StrictOpaqueIdConverter() this.executionPersonaBlockId, final  List<String> criteriaBlockIds = const [], final  List<String> preHooks = const [], final  List<String> postHooks = const [], this.safety = 'safe', final  List<String> allowedMcpTools = const [], final  List<String> expectedInputs = const [], final  Map<String, dynamic>? outputSchema, this.modelStrategy, this.organizationId, final  String? $type}): _criteriaBlockIds = criteriaBlockIds,_preHooks = preHooks,_postHooks = postHooks,_allowedMcpTools = allowedMcpTools,_expectedInputs = expectedInputs,_outputSchema = outputSchema,$type = $type ?? 'logic',super._();
  factory NodeStrategyLogic.fromJson(Map<String, dynamic> json) => _$NodeStrategyLogicFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override final  I18nText name;
@override final  I18nText? description;
@override final  String hook;
@override@StrictOpaqueIdConverter() final  String? roleBlockId;
@override@StrictOpaqueIdConverter() final  String? extractionProtocolBlockId;
@override@StrictOpaqueIdConverter() final  String? executionPersonaBlockId;
 final  List<String> _criteriaBlockIds;
@override@JsonKey() List<String> get criteriaBlockIds {
  if (_criteriaBlockIds is EqualUnmodifiableListView) return _criteriaBlockIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_criteriaBlockIds);
}

 final  List<String> _preHooks;
@override@JsonKey() List<String> get preHooks {
  if (_preHooks is EqualUnmodifiableListView) return _preHooks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_preHooks);
}

 final  List<String> _postHooks;
@override@JsonKey() List<String> get postHooks {
  if (_postHooks is EqualUnmodifiableListView) return _postHooks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_postHooks);
}

@override@JsonKey() final  String safety;
 final  List<String> _allowedMcpTools;
@override@JsonKey() List<String> get allowedMcpTools {
  if (_allowedMcpTools is EqualUnmodifiableListView) return _allowedMcpTools;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedMcpTools);
}

 final  List<String> _expectedInputs;
@override@JsonKey() List<String> get expectedInputs {
  if (_expectedInputs is EqualUnmodifiableListView) return _expectedInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_expectedInputs);
}

 final  Map<String, dynamic>? _outputSchema;
@override Map<String, dynamic>? get outputSchema {
  final value = _outputSchema;
  if (value == null) return null;
  if (_outputSchema is EqualUnmodifiableMapView) return _outputSchema;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? modelStrategy;
@override final  String? organizationId;

@JsonKey(name: 'type')
final String $type;


/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NodeStrategyLogicCopyWith<NodeStrategyLogic> get copyWith => _$NodeStrategyLogicCopyWithImpl<NodeStrategyLogic>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$NodeStrategyLogicToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodeStrategyLogic&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.hook, hook) || other.hook == hook)&&(identical(other.roleBlockId, roleBlockId) || other.roleBlockId == roleBlockId)&&(identical(other.extractionProtocolBlockId, extractionProtocolBlockId) || other.extractionProtocolBlockId == extractionProtocolBlockId)&&(identical(other.executionPersonaBlockId, executionPersonaBlockId) || other.executionPersonaBlockId == executionPersonaBlockId)&&const DeepCollectionEquality().equals(other._criteriaBlockIds, _criteriaBlockIds)&&const DeepCollectionEquality().equals(other._preHooks, _preHooks)&&const DeepCollectionEquality().equals(other._postHooks, _postHooks)&&(identical(other.safety, safety) || other.safety == safety)&&const DeepCollectionEquality().equals(other._allowedMcpTools, _allowedMcpTools)&&const DeepCollectionEquality().equals(other._expectedInputs, _expectedInputs)&&const DeepCollectionEquality().equals(other._outputSchema, _outputSchema)&&(identical(other.modelStrategy, modelStrategy) || other.modelStrategy == modelStrategy)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,name,description,hook,roleBlockId,extractionProtocolBlockId,executionPersonaBlockId,const DeepCollectionEquality().hash(_criteriaBlockIds),const DeepCollectionEquality().hash(_preHooks),const DeepCollectionEquality().hash(_postHooks),safety,const DeepCollectionEquality().hash(_allowedMcpTools),const DeepCollectionEquality().hash(_expectedInputs),const DeepCollectionEquality().hash(_outputSchema),modelStrategy,organizationId);

@override
String toString() {
  return 'NodeStrategy.logic(id: $id, slug: $slug, name: $name, description: $description, hook: $hook, roleBlockId: $roleBlockId, extractionProtocolBlockId: $extractionProtocolBlockId, executionPersonaBlockId: $executionPersonaBlockId, criteriaBlockIds: $criteriaBlockIds, preHooks: $preHooks, postHooks: $postHooks, safety: $safety, allowedMcpTools: $allowedMcpTools, expectedInputs: $expectedInputs, outputSchema: $outputSchema, modelStrategy: $modelStrategy, organizationId: $organizationId)';
}


}

/// @nodoc
abstract mixin class $NodeStrategyLogicCopyWith<$Res> implements $NodeStrategyCopyWith<$Res> {
  factory $NodeStrategyLogicCopyWith(NodeStrategyLogic value, $Res Function(NodeStrategyLogic) _then) = _$NodeStrategyLogicCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText? description, String hook,@StrictOpaqueIdConverter() String? roleBlockId,@StrictOpaqueIdConverter() String? extractionProtocolBlockId,@StrictOpaqueIdConverter() String? executionPersonaBlockId, List<String> criteriaBlockIds, List<String> preHooks, List<String> postHooks, String safety, List<String> allowedMcpTools, List<String> expectedInputs, Map<String, dynamic>? outputSchema, String? modelStrategy, String? organizationId
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class _$NodeStrategyLogicCopyWithImpl<$Res>
    implements $NodeStrategyLogicCopyWith<$Res> {
  _$NodeStrategyLogicCopyWithImpl(this._self, this._then);

  final NodeStrategyLogic _self;
  final $Res Function(NodeStrategyLogic) _then;

/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = freezed,Object? hook = null,Object? roleBlockId = freezed,Object? extractionProtocolBlockId = freezed,Object? executionPersonaBlockId = freezed,Object? criteriaBlockIds = null,Object? preHooks = null,Object? postHooks = null,Object? safety = null,Object? allowedMcpTools = null,Object? expectedInputs = null,Object? outputSchema = freezed,Object? modelStrategy = freezed,Object? organizationId = freezed,}) {
  return _then(NodeStrategyLogic(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,hook: null == hook ? _self.hook : hook // ignore: cast_nullable_to_non_nullable
as String,roleBlockId: freezed == roleBlockId ? _self.roleBlockId : roleBlockId // ignore: cast_nullable_to_non_nullable
as String?,extractionProtocolBlockId: freezed == extractionProtocolBlockId ? _self.extractionProtocolBlockId : extractionProtocolBlockId // ignore: cast_nullable_to_non_nullable
as String?,executionPersonaBlockId: freezed == executionPersonaBlockId ? _self.executionPersonaBlockId : executionPersonaBlockId // ignore: cast_nullable_to_non_nullable
as String?,criteriaBlockIds: null == criteriaBlockIds ? _self._criteriaBlockIds : criteriaBlockIds // ignore: cast_nullable_to_non_nullable
as List<String>,preHooks: null == preHooks ? _self._preHooks : preHooks // ignore: cast_nullable_to_non_nullable
as List<String>,postHooks: null == postHooks ? _self._postHooks : postHooks // ignore: cast_nullable_to_non_nullable
as List<String>,safety: null == safety ? _self.safety : safety // ignore: cast_nullable_to_non_nullable
as String,allowedMcpTools: null == allowedMcpTools ? _self._allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,expectedInputs: null == expectedInputs ? _self._expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<String>,outputSchema: freezed == outputSchema ? _self._outputSchema : outputSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of NodeStrategy
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
mixin _$Workflow {

@StrictOpaqueIdConverter() String get id; String get slug; I18nText get name; I18nText get description; String get status; int get version; bool get isPublic; String? get organizationId; Map<String, dynamic> get uiSchema; Map<String, EmbeddedOutputProfile> get outputProfiles; String get defaultProfileId;@JsonKey(name: 'default_strictness_level') int get defaultStrictnessLevel;@JsonKey(name: 'default_scoring_strategy') ScoringStrategy get defaultScoringStrategy;@JsonKey(name: 'enable_contextual_overrides') bool get enableContextualOverrides;@JsonKey(name: 'enable_semantic_smoothing') bool get enableSemanticSmoothing;@JsonKey(name: 'enable_eager_anonymization') bool get enableEagerAnonymization;@JsonKey(name: 'system_audit_trail') bool get systemAuditTrail;@JsonKey(name: 'allowed_exports') List<String> get allowedExports;@JsonKey(name: 'historical_context_mode') String get historicalContextMode; List<ExpectedInput> get expectedInputs; List<StepRule> get steps;
/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowCopyWith<Workflow> get copyWith => _$WorkflowCopyWithImpl<Workflow>(this as Workflow, _$identity);

  /// Serializes this Workflow to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'Workflow(id: $id, slug: $slug, name: $name, description: $description, status: $status, version: $version, isPublic: $isPublic, organizationId: $organizationId, uiSchema: $uiSchema, outputProfiles: $outputProfiles, defaultProfileId: $defaultProfileId, defaultStrictnessLevel: $defaultStrictnessLevel, defaultScoringStrategy: $defaultScoringStrategy, enableContextualOverrides: $enableContextualOverrides, enableSemanticSmoothing: $enableSemanticSmoothing, enableEagerAnonymization: $enableEagerAnonymization, systemAuditTrail: $systemAuditTrail, allowedExports: $allowedExports, historicalContextMode: $historicalContextMode, expectedInputs: $expectedInputs, steps: $steps)';
}


}

/// @nodoc
abstract mixin class $WorkflowCopyWith<$Res>  {
  factory $WorkflowCopyWith(Workflow value, $Res Function(Workflow) _then) = _$WorkflowCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText description, String status, int version, bool isPublic, String? organizationId, Map<String, dynamic> uiSchema, Map<String, EmbeddedOutputProfile> outputProfiles, String defaultProfileId,@JsonKey(name: 'default_strictness_level') int defaultStrictnessLevel,@JsonKey(name: 'default_scoring_strategy') ScoringStrategy defaultScoringStrategy,@JsonKey(name: 'enable_contextual_overrides') bool enableContextualOverrides,@JsonKey(name: 'enable_semantic_smoothing') bool enableSemanticSmoothing,@JsonKey(name: 'enable_eager_anonymization') bool enableEagerAnonymization,@JsonKey(name: 'system_audit_trail') bool systemAuditTrail,@JsonKey(name: 'allowed_exports') List<String> allowedExports,@JsonKey(name: 'historical_context_mode') String historicalContextMode, List<ExpectedInput> expectedInputs, List<StepRule> steps
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class _$WorkflowCopyWithImpl<$Res>
    implements $WorkflowCopyWith<$Res> {
  _$WorkflowCopyWithImpl(this._self, this._then);

  final Workflow _self;
  final $Res Function(Workflow) _then;

/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = null,Object? status = null,Object? version = null,Object? isPublic = null,Object? organizationId = freezed,Object? uiSchema = null,Object? outputProfiles = null,Object? defaultProfileId = null,Object? defaultStrictnessLevel = null,Object? defaultScoringStrategy = null,Object? enableContextualOverrides = null,Object? enableSemanticSmoothing = null,Object? enableEagerAnonymization = null,Object? systemAuditTrail = null,Object? allowedExports = null,Object? historicalContextMode = null,Object? expectedInputs = null,Object? steps = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,version: null == version ? _self.version : version // ignore: cast_nullable_to_non_nullable
as int,isPublic: null == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,uiSchema: null == uiSchema ? _self.uiSchema : uiSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,outputProfiles: null == outputProfiles ? _self.outputProfiles : outputProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, EmbeddedOutputProfile>,defaultProfileId: null == defaultProfileId ? _self.defaultProfileId : defaultProfileId // ignore: cast_nullable_to_non_nullable
as String,defaultStrictnessLevel: null == defaultStrictnessLevel ? _self.defaultStrictnessLevel : defaultStrictnessLevel // ignore: cast_nullable_to_non_nullable
as int,defaultScoringStrategy: null == defaultScoringStrategy ? _self.defaultScoringStrategy : defaultScoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy,enableContextualOverrides: null == enableContextualOverrides ? _self.enableContextualOverrides : enableContextualOverrides // ignore: cast_nullable_to_non_nullable
as bool,enableSemanticSmoothing: null == enableSemanticSmoothing ? _self.enableSemanticSmoothing : enableSemanticSmoothing // ignore: cast_nullable_to_non_nullable
as bool,enableEagerAnonymization: null == enableEagerAnonymization ? _self.enableEagerAnonymization : enableEagerAnonymization // ignore: cast_nullable_to_non_nullable
as bool,systemAuditTrail: null == systemAuditTrail ? _self.systemAuditTrail : systemAuditTrail // ignore: cast_nullable_to_non_nullable
as bool,allowedExports: null == allowedExports ? _self.allowedExports : allowedExports // ignore: cast_nullable_to_non_nullable
as List<String>,historicalContextMode: null == historicalContextMode ? _self.historicalContextMode : historicalContextMode // ignore: cast_nullable_to_non_nullable
as String,expectedInputs: null == expectedInputs ? _self.expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<ExpectedInput>,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<StepRule>,
  ));
}
/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// Adds pattern-matching-related methods to [Workflow].
extension WorkflowPatterns on Workflow {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Workflow value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Workflow() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Workflow value)  $default,){
final _that = this;
switch (_that) {
case _Workflow():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Workflow value)?  $default,){
final _that = this;
switch (_that) {
case _Workflow() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText description,  String status,  int version,  bool isPublic,  String? organizationId,  Map<String, dynamic> uiSchema,  Map<String, EmbeddedOutputProfile> outputProfiles,  String defaultProfileId, @JsonKey(name: 'default_strictness_level')  int defaultStrictnessLevel, @JsonKey(name: 'default_scoring_strategy')  ScoringStrategy defaultScoringStrategy, @JsonKey(name: 'enable_contextual_overrides')  bool enableContextualOverrides, @JsonKey(name: 'enable_semantic_smoothing')  bool enableSemanticSmoothing, @JsonKey(name: 'enable_eager_anonymization')  bool enableEagerAnonymization, @JsonKey(name: 'system_audit_trail')  bool systemAuditTrail, @JsonKey(name: 'allowed_exports')  List<String> allowedExports, @JsonKey(name: 'historical_context_mode')  String historicalContextMode,  List<ExpectedInput> expectedInputs,  List<StepRule> steps)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Workflow() when $default != null:
return $default(_that.id,_that.slug,_that.name,_that.description,_that.status,_that.version,_that.isPublic,_that.organizationId,_that.uiSchema,_that.outputProfiles,_that.defaultProfileId,_that.defaultStrictnessLevel,_that.defaultScoringStrategy,_that.enableContextualOverrides,_that.enableSemanticSmoothing,_that.enableEagerAnonymization,_that.systemAuditTrail,_that.allowedExports,_that.historicalContextMode,_that.expectedInputs,_that.steps);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText description,  String status,  int version,  bool isPublic,  String? organizationId,  Map<String, dynamic> uiSchema,  Map<String, EmbeddedOutputProfile> outputProfiles,  String defaultProfileId, @JsonKey(name: 'default_strictness_level')  int defaultStrictnessLevel, @JsonKey(name: 'default_scoring_strategy')  ScoringStrategy defaultScoringStrategy, @JsonKey(name: 'enable_contextual_overrides')  bool enableContextualOverrides, @JsonKey(name: 'enable_semantic_smoothing')  bool enableSemanticSmoothing, @JsonKey(name: 'enable_eager_anonymization')  bool enableEagerAnonymization, @JsonKey(name: 'system_audit_trail')  bool systemAuditTrail, @JsonKey(name: 'allowed_exports')  List<String> allowedExports, @JsonKey(name: 'historical_context_mode')  String historicalContextMode,  List<ExpectedInput> expectedInputs,  List<StepRule> steps)  $default,) {final _that = this;
switch (_that) {
case _Workflow():
return $default(_that.id,_that.slug,_that.name,_that.description,_that.status,_that.version,_that.isPublic,_that.organizationId,_that.uiSchema,_that.outputProfiles,_that.defaultProfileId,_that.defaultStrictnessLevel,_that.defaultScoringStrategy,_that.enableContextualOverrides,_that.enableSemanticSmoothing,_that.enableEagerAnonymization,_that.systemAuditTrail,_that.allowedExports,_that.historicalContextMode,_that.expectedInputs,_that.steps);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText description,  String status,  int version,  bool isPublic,  String? organizationId,  Map<String, dynamic> uiSchema,  Map<String, EmbeddedOutputProfile> outputProfiles,  String defaultProfileId, @JsonKey(name: 'default_strictness_level')  int defaultStrictnessLevel, @JsonKey(name: 'default_scoring_strategy')  ScoringStrategy defaultScoringStrategy, @JsonKey(name: 'enable_contextual_overrides')  bool enableContextualOverrides, @JsonKey(name: 'enable_semantic_smoothing')  bool enableSemanticSmoothing, @JsonKey(name: 'enable_eager_anonymization')  bool enableEagerAnonymization, @JsonKey(name: 'system_audit_trail')  bool systemAuditTrail, @JsonKey(name: 'allowed_exports')  List<String> allowedExports, @JsonKey(name: 'historical_context_mode')  String historicalContextMode,  List<ExpectedInput> expectedInputs,  List<StepRule> steps)?  $default,) {final _that = this;
switch (_that) {
case _Workflow() when $default != null:
return $default(_that.id,_that.slug,_that.name,_that.description,_that.status,_that.version,_that.isPublic,_that.organizationId,_that.uiSchema,_that.outputProfiles,_that.defaultProfileId,_that.defaultStrictnessLevel,_that.defaultScoringStrategy,_that.enableContextualOverrides,_that.enableSemanticSmoothing,_that.enableEagerAnonymization,_that.systemAuditTrail,_that.allowedExports,_that.historicalContextMode,_that.expectedInputs,_that.steps);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _Workflow extends Workflow {
  const _Workflow({@StrictOpaqueIdConverter() required this.id, required this.slug, required this.name, required this.description, this.status = "draft", this.version = 1, this.isPublic = false, this.organizationId, final  Map<String, dynamic> uiSchema = const {}, final  Map<String, EmbeddedOutputProfile> outputProfiles = const {}, this.defaultProfileId = "default", @JsonKey(name: 'default_strictness_level') this.defaultStrictnessLevel = 50, @JsonKey(name: 'default_scoring_strategy') this.defaultScoringStrategy = ScoringStrategy.average, @JsonKey(name: 'enable_contextual_overrides') this.enableContextualOverrides = false, @JsonKey(name: 'enable_semantic_smoothing') this.enableSemanticSmoothing = false, @JsonKey(name: 'enable_eager_anonymization') this.enableEagerAnonymization = false, @JsonKey(name: 'system_audit_trail') this.systemAuditTrail = false, @JsonKey(name: 'allowed_exports') final  List<String> allowedExports = const ['pdf', 'docx'], @JsonKey(name: 'historical_context_mode') this.historicalContextMode = 'DISABLED', final  List<ExpectedInput> expectedInputs = const [], final  List<StepRule> steps = const []}): _uiSchema = uiSchema,_outputProfiles = outputProfiles,_allowedExports = allowedExports,_expectedInputs = expectedInputs,_steps = steps,super._();
  factory _Workflow.fromJson(Map<String, dynamic> json) => _$WorkflowFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override final  I18nText name;
@override final  I18nText description;
@override@JsonKey() final  String status;
@override@JsonKey() final  int version;
@override@JsonKey() final  bool isPublic;
@override final  String? organizationId;
 final  Map<String, dynamic> _uiSchema;
@override@JsonKey() Map<String, dynamic> get uiSchema {
  if (_uiSchema is EqualUnmodifiableMapView) return _uiSchema;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_uiSchema);
}

 final  Map<String, EmbeddedOutputProfile> _outputProfiles;
@override@JsonKey() Map<String, EmbeddedOutputProfile> get outputProfiles {
  if (_outputProfiles is EqualUnmodifiableMapView) return _outputProfiles;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_outputProfiles);
}

@override@JsonKey() final  String defaultProfileId;
@override@JsonKey(name: 'default_strictness_level') final  int defaultStrictnessLevel;
@override@JsonKey(name: 'default_scoring_strategy') final  ScoringStrategy defaultScoringStrategy;
@override@JsonKey(name: 'enable_contextual_overrides') final  bool enableContextualOverrides;
@override@JsonKey(name: 'enable_semantic_smoothing') final  bool enableSemanticSmoothing;
@override@JsonKey(name: 'enable_eager_anonymization') final  bool enableEagerAnonymization;
@override@JsonKey(name: 'system_audit_trail') final  bool systemAuditTrail;
 final  List<String> _allowedExports;
@override@JsonKey(name: 'allowed_exports') List<String> get allowedExports {
  if (_allowedExports is EqualUnmodifiableListView) return _allowedExports;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedExports);
}

@override@JsonKey(name: 'historical_context_mode') final  String historicalContextMode;
 final  List<ExpectedInput> _expectedInputs;
@override@JsonKey() List<ExpectedInput> get expectedInputs {
  if (_expectedInputs is EqualUnmodifiableListView) return _expectedInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_expectedInputs);
}

 final  List<StepRule> _steps;
@override@JsonKey() List<StepRule> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}


/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowCopyWith<_Workflow> get copyWith => __$WorkflowCopyWithImpl<_Workflow>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowToJson(this, );
}



@override
String toString() {
  return 'Workflow(id: $id, slug: $slug, name: $name, description: $description, status: $status, version: $version, isPublic: $isPublic, organizationId: $organizationId, uiSchema: $uiSchema, outputProfiles: $outputProfiles, defaultProfileId: $defaultProfileId, defaultStrictnessLevel: $defaultStrictnessLevel, defaultScoringStrategy: $defaultScoringStrategy, enableContextualOverrides: $enableContextualOverrides, enableSemanticSmoothing: $enableSemanticSmoothing, enableEagerAnonymization: $enableEagerAnonymization, systemAuditTrail: $systemAuditTrail, allowedExports: $allowedExports, historicalContextMode: $historicalContextMode, expectedInputs: $expectedInputs, steps: $steps)';
}


}

/// @nodoc
abstract mixin class _$WorkflowCopyWith<$Res> implements $WorkflowCopyWith<$Res> {
  factory _$WorkflowCopyWith(_Workflow value, $Res Function(_Workflow) _then) = __$WorkflowCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText description, String status, int version, bool isPublic, String? organizationId, Map<String, dynamic> uiSchema, Map<String, EmbeddedOutputProfile> outputProfiles, String defaultProfileId,@JsonKey(name: 'default_strictness_level') int defaultStrictnessLevel,@JsonKey(name: 'default_scoring_strategy') ScoringStrategy defaultScoringStrategy,@JsonKey(name: 'enable_contextual_overrides') bool enableContextualOverrides,@JsonKey(name: 'enable_semantic_smoothing') bool enableSemanticSmoothing,@JsonKey(name: 'enable_eager_anonymization') bool enableEagerAnonymization,@JsonKey(name: 'system_audit_trail') bool systemAuditTrail,@JsonKey(name: 'allowed_exports') List<String> allowedExports,@JsonKey(name: 'historical_context_mode') String historicalContextMode, List<ExpectedInput> expectedInputs, List<StepRule> steps
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res> get description;

}
/// @nodoc
class __$WorkflowCopyWithImpl<$Res>
    implements _$WorkflowCopyWith<$Res> {
  __$WorkflowCopyWithImpl(this._self, this._then);

  final _Workflow _self;
  final $Res Function(_Workflow) _then;

/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = null,Object? status = null,Object? version = null,Object? isPublic = null,Object? organizationId = freezed,Object? uiSchema = null,Object? outputProfiles = null,Object? defaultProfileId = null,Object? defaultStrictnessLevel = null,Object? defaultScoringStrategy = null,Object? enableContextualOverrides = null,Object? enableSemanticSmoothing = null,Object? enableEagerAnonymization = null,Object? systemAuditTrail = null,Object? allowedExports = null,Object? historicalContextMode = null,Object? expectedInputs = null,Object? steps = null,}) {
  return _then(_Workflow(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,version: null == version ? _self.version : version // ignore: cast_nullable_to_non_nullable
as int,isPublic: null == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,uiSchema: null == uiSchema ? _self._uiSchema : uiSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,outputProfiles: null == outputProfiles ? _self._outputProfiles : outputProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, EmbeddedOutputProfile>,defaultProfileId: null == defaultProfileId ? _self.defaultProfileId : defaultProfileId // ignore: cast_nullable_to_non_nullable
as String,defaultStrictnessLevel: null == defaultStrictnessLevel ? _self.defaultStrictnessLevel : defaultStrictnessLevel // ignore: cast_nullable_to_non_nullable
as int,defaultScoringStrategy: null == defaultScoringStrategy ? _self.defaultScoringStrategy : defaultScoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy,enableContextualOverrides: null == enableContextualOverrides ? _self.enableContextualOverrides : enableContextualOverrides // ignore: cast_nullable_to_non_nullable
as bool,enableSemanticSmoothing: null == enableSemanticSmoothing ? _self.enableSemanticSmoothing : enableSemanticSmoothing // ignore: cast_nullable_to_non_nullable
as bool,enableEagerAnonymization: null == enableEagerAnonymization ? _self.enableEagerAnonymization : enableEagerAnonymization // ignore: cast_nullable_to_non_nullable
as bool,systemAuditTrail: null == systemAuditTrail ? _self.systemAuditTrail : systemAuditTrail // ignore: cast_nullable_to_non_nullable
as bool,allowedExports: null == allowedExports ? _self._allowedExports : allowedExports // ignore: cast_nullable_to_non_nullable
as List<String>,historicalContextMode: null == historicalContextMode ? _self.historicalContextMode : historicalContextMode // ignore: cast_nullable_to_non_nullable
as String,expectedInputs: null == expectedInputs ? _self._expectedInputs : expectedInputs // ignore: cast_nullable_to_non_nullable
as List<ExpectedInput>,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<StepRule>,
  ));
}

/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of Workflow
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
