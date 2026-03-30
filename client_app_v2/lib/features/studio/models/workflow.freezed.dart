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
@JsonSerializable()

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

 String get inputKey; I18nText get label; bool get required; bool get isChatHistory; List<String> get inputModes; I18nText get description; String? get aiDescription; List<QuestionnaireItem> get questionnaireDefinition;
/// Create a copy of ExpectedInput
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExpectedInputCopyWith<ExpectedInput> get copyWith => _$ExpectedInputCopyWithImpl<ExpectedInput>(this as ExpectedInput, _$identity);

  /// Serializes this ExpectedInput to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ExpectedInput(inputKey: $inputKey, label: $label, required: $required, isChatHistory: $isChatHistory, inputModes: $inputModes, description: $description, aiDescription: $aiDescription, questionnaireDefinition: $questionnaireDefinition)';
}


}

/// @nodoc
abstract mixin class $ExpectedInputCopyWith<$Res>  {
  factory $ExpectedInputCopyWith(ExpectedInput value, $Res Function(ExpectedInput) _then) = _$ExpectedInputCopyWithImpl;
@useResult
$Res call({
 String inputKey, I18nText label, bool required, bool isChatHistory, List<String> inputModes, I18nText description, String? aiDescription, List<QuestionnaireItem> questionnaireDefinition
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
@pragma('vm:prefer-inline') @override $Res call({Object? inputKey = null,Object? label = null,Object? required = null,Object? isChatHistory = null,Object? inputModes = null,Object? description = null,Object? aiDescription = freezed,Object? questionnaireDefinition = null,}) {
  return _then(_self.copyWith(
inputKey: null == inputKey ? _self.inputKey : inputKey // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,isChatHistory: null == isChatHistory ? _self.isChatHistory : isChatHistory // ignore: cast_nullable_to_non_nullable
as bool,inputModes: null == inputModes ? _self.inputModes : inputModes // ignore: cast_nullable_to_non_nullable
as List<String>,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: freezed == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String inputKey,  I18nText label,  bool required,  bool isChatHistory,  List<String> inputModes,  I18nText description,  String? aiDescription,  List<QuestionnaireItem> questionnaireDefinition)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExpectedInput() when $default != null:
return $default(_that.inputKey,_that.label,_that.required,_that.isChatHistory,_that.inputModes,_that.description,_that.aiDescription,_that.questionnaireDefinition);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String inputKey,  I18nText label,  bool required,  bool isChatHistory,  List<String> inputModes,  I18nText description,  String? aiDescription,  List<QuestionnaireItem> questionnaireDefinition)  $default,) {final _that = this;
switch (_that) {
case _ExpectedInput():
return $default(_that.inputKey,_that.label,_that.required,_that.isChatHistory,_that.inputModes,_that.description,_that.aiDescription,_that.questionnaireDefinition);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String inputKey,  I18nText label,  bool required,  bool isChatHistory,  List<String> inputModes,  I18nText description,  String? aiDescription,  List<QuestionnaireItem> questionnaireDefinition)?  $default,) {final _that = this;
switch (_that) {
case _ExpectedInput() when $default != null:
return $default(_that.inputKey,_that.label,_that.required,_that.isChatHistory,_that.inputModes,_that.description,_that.aiDescription,_that.questionnaireDefinition);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ExpectedInput extends ExpectedInput {
  const _ExpectedInput({required this.inputKey, required this.label, required this.required, this.isChatHistory = false, final  List<String> inputModes = const [], required this.description, this.aiDescription, final  List<QuestionnaireItem> questionnaireDefinition = const []}): _inputModes = inputModes,_questionnaireDefinition = questionnaireDefinition,super._();
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
  return 'ExpectedInput(inputKey: $inputKey, label: $label, required: $required, isChatHistory: $isChatHistory, inputModes: $inputModes, description: $description, aiDescription: $aiDescription, questionnaireDefinition: $questionnaireDefinition)';
}


}

/// @nodoc
abstract mixin class _$ExpectedInputCopyWith<$Res> implements $ExpectedInputCopyWith<$Res> {
  factory _$ExpectedInputCopyWith(_ExpectedInput value, $Res Function(_ExpectedInput) _then) = __$ExpectedInputCopyWithImpl;
@override @useResult
$Res call({
 String inputKey, I18nText label, bool required, bool isChatHistory, List<String> inputModes, I18nText description, String? aiDescription, List<QuestionnaireItem> questionnaireDefinition
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
@override @pragma('vm:prefer-inline') $Res call({Object? inputKey = null,Object? label = null,Object? required = null,Object? isChatHistory = null,Object? inputModes = null,Object? description = null,Object? aiDescription = freezed,Object? questionnaireDefinition = null,}) {
  return _then(_ExpectedInput(
inputKey: null == inputKey ? _self.inputKey : inputKey // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,isChatHistory: null == isChatHistory ? _self.isChatHistory : isChatHistory // ignore: cast_nullable_to_non_nullable
as bool,inputModes: null == inputModes ? _self._inputModes : inputModes // ignore: cast_nullable_to_non_nullable
as List<String>,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: freezed == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
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
  const _OutputLayoutBlock({required this.presetView, this.title, this.description, final  List<String> steps = const [], final  List<String> targetBlocks = const [], this.showText = true}): _steps = steps,_targetBlocks = targetBlocks,super._();
  factory _OutputLayoutBlock.fromJson(Map<String, dynamic> json) => _$OutputLayoutBlockFromJson(json);

@override final  String presetView;
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

 I18nText get name; List<OutputLayoutBlock> get layouts;
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputProfileCopyWith<OutputProfile> get copyWith => _$OutputProfileCopyWithImpl<OutputProfile>(this as OutputProfile, _$identity);

  /// Serializes this OutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputProfile(name: $name, layouts: $layouts)';
}


}

/// @nodoc
abstract mixin class $OutputProfileCopyWith<$Res>  {
  factory $OutputProfileCopyWith(OutputProfile value, $Res Function(OutputProfile) _then) = _$OutputProfileCopyWithImpl;
@useResult
$Res call({
 I18nText name, List<OutputLayoutBlock> layouts
});


$I18nTextCopyWith<$Res> get name;

}
/// @nodoc
class _$OutputProfileCopyWithImpl<$Res>
    implements $OutputProfileCopyWith<$Res> {
  _$OutputProfileCopyWithImpl(this._self, this._then);

  final OutputProfile _self;
  final $Res Function(OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? layouts = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( I18nText name,  List<OutputLayoutBlock> layouts)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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
case _OutputProfile():
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
case _OutputProfile() when $default != null:
return $default(_that.name,_that.layouts);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OutputProfile extends OutputProfile {
  const _OutputProfile({required this.name, final  List<OutputLayoutBlock> layouts = const []}): _layouts = layouts,super._();
  factory _OutputProfile.fromJson(Map<String, dynamic> json) => _$OutputProfileFromJson(json);

@override final  I18nText name;
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
  return 'OutputProfile(name: $name, layouts: $layouts)';
}


}

/// @nodoc
abstract mixin class _$OutputProfileCopyWith<$Res> implements $OutputProfileCopyWith<$Res> {
  factory _$OutputProfileCopyWith(_OutputProfile value, $Res Function(_OutputProfile) _then) = __$OutputProfileCopyWithImpl;
@override @useResult
$Res call({
 I18nText name, List<OutputLayoutBlock> layouts
});


@override $I18nTextCopyWith<$Res> get name;

}
/// @nodoc
class __$OutputProfileCopyWithImpl<$Res>
    implements _$OutputProfileCopyWith<$Res> {
  __$OutputProfileCopyWithImpl(this._self, this._then);

  final _OutputProfile _self;
  final $Res Function(_OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? layouts = null,}) {
  return _then(_OutputProfile(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
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
}
}


/// @nodoc
mixin _$StepRule {

@StrictOpaqueIdConverter() String get id;@StrictOpaqueIdConverter() String get taskBlueprint; List<String> get dependsOn; Map<String, String> get inputMappings; List<String> get allowedMcpTools; double get uiPosX; double get uiPosY;
/// Create a copy of StepRule
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepRuleCopyWith<StepRule> get copyWith => _$StepRuleCopyWithImpl<StepRule>(this as StepRule, _$identity);

  /// Serializes this StepRule to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'StepRule(id: $id, taskBlueprint: $taskBlueprint, dependsOn: $dependsOn, inputMappings: $inputMappings, allowedMcpTools: $allowedMcpTools, uiPosX: $uiPosX, uiPosY: $uiPosY)';
}


}

/// @nodoc
abstract mixin class $StepRuleCopyWith<$Res>  {
  factory $StepRuleCopyWith(StepRule value, $Res Function(StepRule) _then) = _$StepRuleCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter() String taskBlueprint, List<String> dependsOn, Map<String, String> inputMappings, List<String> allowedMcpTools, double uiPosX, double uiPosY
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? taskBlueprint = null,Object? dependsOn = null,Object? inputMappings = null,Object? allowedMcpTools = null,Object? uiPosX = null,Object? uiPosY = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,taskBlueprint: null == taskBlueprint ? _self.taskBlueprint : taskBlueprint // ignore: cast_nullable_to_non_nullable
as String,dependsOn: null == dependsOn ? _self.dependsOn : dependsOn // ignore: cast_nullable_to_non_nullable
as List<String>,inputMappings: null == inputMappings ? _self.inputMappings : inputMappings // ignore: cast_nullable_to_non_nullable
as Map<String, String>,allowedMcpTools: null == allowedMcpTools ? _self.allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,uiPosX: null == uiPosX ? _self.uiPosX : uiPosX // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()  String taskBlueprint,  List<String> dependsOn,  Map<String, String> inputMappings,  List<String> allowedMcpTools,  double uiPosX,  double uiPosY)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepRule() when $default != null:
return $default(_that.id,_that.taskBlueprint,_that.dependsOn,_that.inputMappings,_that.allowedMcpTools,_that.uiPosX,_that.uiPosY);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()  String taskBlueprint,  List<String> dependsOn,  Map<String, String> inputMappings,  List<String> allowedMcpTools,  double uiPosX,  double uiPosY)  $default,) {final _that = this;
switch (_that) {
case _StepRule():
return $default(_that.id,_that.taskBlueprint,_that.dependsOn,_that.inputMappings,_that.allowedMcpTools,_that.uiPosX,_that.uiPosY);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id, @StrictOpaqueIdConverter()  String taskBlueprint,  List<String> dependsOn,  Map<String, String> inputMappings,  List<String> allowedMcpTools,  double uiPosX,  double uiPosY)?  $default,) {final _that = this;
switch (_that) {
case _StepRule() when $default != null:
return $default(_that.id,_that.taskBlueprint,_that.dependsOn,_that.inputMappings,_that.allowedMcpTools,_that.uiPosX,_that.uiPosY);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StepRule extends StepRule {
  const _StepRule({@StrictOpaqueIdConverter() required this.id, @StrictOpaqueIdConverter() required this.taskBlueprint, final  List<String> dependsOn = const [], final  Map<String, String> inputMappings = const {}, final  List<String> allowedMcpTools = const [], this.uiPosX = 0.0, this.uiPosY = 0.0}): _dependsOn = dependsOn,_inputMappings = inputMappings,_allowedMcpTools = allowedMcpTools,super._();
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

 final  List<String> _allowedMcpTools;
@override@JsonKey() List<String> get allowedMcpTools {
  if (_allowedMcpTools is EqualUnmodifiableListView) return _allowedMcpTools;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedMcpTools);
}

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
  return 'StepRule(id: $id, taskBlueprint: $taskBlueprint, dependsOn: $dependsOn, inputMappings: $inputMappings, allowedMcpTools: $allowedMcpTools, uiPosX: $uiPosX, uiPosY: $uiPosY)';
}


}

/// @nodoc
abstract mixin class _$StepRuleCopyWith<$Res> implements $StepRuleCopyWith<$Res> {
  factory _$StepRuleCopyWith(_StepRule value, $Res Function(_StepRule) _then) = __$StepRuleCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id,@StrictOpaqueIdConverter() String taskBlueprint, List<String> dependsOn, Map<String, String> inputMappings, List<String> allowedMcpTools, double uiPosX, double uiPosY
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? taskBlueprint = null,Object? dependsOn = null,Object? inputMappings = null,Object? allowedMcpTools = null,Object? uiPosX = null,Object? uiPosY = null,}) {
  return _then(_StepRule(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,taskBlueprint: null == taskBlueprint ? _self.taskBlueprint : taskBlueprint // ignore: cast_nullable_to_non_nullable
as String,dependsOn: null == dependsOn ? _self._dependsOn : dependsOn // ignore: cast_nullable_to_non_nullable
as List<String>,inputMappings: null == inputMappings ? _self._inputMappings : inputMappings // ignore: cast_nullable_to_non_nullable
as Map<String, String>,allowedMcpTools: null == allowedMcpTools ? _self._allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,uiPosX: null == uiPosX ? _self.uiPosX : uiPosX // ignore: cast_nullable_to_non_nullable
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

@StrictOpaqueIdConverter() String get id; String get slug; I18nText get name; I18nText? get description; List<String> get preHooks; List<String> get postHooks; String get safety; List<String> get allowedMcpTools;
/// Create a copy of NodeStrategy
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$NodeStrategyCopyWith<NodeStrategy> get copyWith => _$NodeStrategyCopyWithImpl<NodeStrategy>(this as NodeStrategy, _$identity);

  /// Serializes this NodeStrategy to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodeStrategy&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.preHooks, preHooks)&&const DeepCollectionEquality().equals(other.postHooks, postHooks)&&(identical(other.safety, safety) || other.safety == safety)&&const DeepCollectionEquality().equals(other.allowedMcpTools, allowedMcpTools));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,name,description,const DeepCollectionEquality().hash(preHooks),const DeepCollectionEquality().hash(postHooks),safety,const DeepCollectionEquality().hash(allowedMcpTools));

@override
String toString() {
  return 'NodeStrategy(id: $id, slug: $slug, name: $name, description: $description, preHooks: $preHooks, postHooks: $postHooks, safety: $safety, allowedMcpTools: $allowedMcpTools)';
}


}

/// @nodoc
abstract mixin class $NodeStrategyCopyWith<$Res>  {
  factory $NodeStrategyCopyWith(NodeStrategy value, $Res Function(NodeStrategy) _then) = _$NodeStrategyCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText? description, List<String> preHooks, List<String> postHooks, String safety, List<String> allowedMcpTools
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = freezed,Object? preHooks = null,Object? postHooks = null,Object? safety = null,Object? allowedMcpTools = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,preHooks: null == preHooks ? _self.preHooks : preHooks // ignore: cast_nullable_to_non_nullable
as List<String>,postHooks: null == postHooks ? _self.postHooks : postHooks // ignore: cast_nullable_to_non_nullable
as List<String>,safety: null == safety ? _self.safety : safety // ignore: cast_nullable_to_non_nullable
as String,allowedMcpTools: null == allowedMcpTools ? _self.allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  List<String> promptBlocks,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  String? modelStrategy)?  llm,TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String hook,  String? taskKey,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools)?  logic,required TResult orElse(),}) {final _that = this;
switch (_that) {
case NodeStrategyLlm() when llm != null:
return llm(_that.id,_that.slug,_that.name,_that.description,_that.promptBlocks,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.modelStrategy);case NodeStrategyLogic() when logic != null:
return logic(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.taskKey,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  List<String> promptBlocks,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  String? modelStrategy)  llm,required TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String hook,  String? taskKey,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools)  logic,}) {final _that = this;
switch (_that) {
case NodeStrategyLlm():
return llm(_that.id,_that.slug,_that.name,_that.description,_that.promptBlocks,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.modelStrategy);case NodeStrategyLogic():
return logic(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.taskKey,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  List<String> promptBlocks,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools,  String? modelStrategy)?  llm,TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText? description,  String hook,  String? taskKey,  List<String> preHooks,  List<String> postHooks,  String safety,  List<String> allowedMcpTools)?  logic,}) {final _that = this;
switch (_that) {
case NodeStrategyLlm() when llm != null:
return llm(_that.id,_that.slug,_that.name,_that.description,_that.promptBlocks,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools,_that.modelStrategy);case NodeStrategyLogic() when logic != null:
return logic(_that.id,_that.slug,_that.name,_that.description,_that.hook,_that.taskKey,_that.preHooks,_that.postHooks,_that.safety,_that.allowedMcpTools);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class NodeStrategyLlm extends NodeStrategy {
  const NodeStrategyLlm({@StrictOpaqueIdConverter() required this.id, required this.slug, required this.name, this.description, final  List<String> promptBlocks = const [], final  List<String> preHooks = const [], final  List<String> postHooks = const [], this.safety = 'safe', final  List<String> allowedMcpTools = const [], this.modelStrategy, final  String? $type}): _promptBlocks = promptBlocks,_preHooks = preHooks,_postHooks = postHooks,_allowedMcpTools = allowedMcpTools,$type = $type ?? 'llm',super._();
  factory NodeStrategyLlm.fromJson(Map<String, dynamic> json) => _$NodeStrategyLlmFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override final  I18nText name;
@override final  I18nText? description;
 final  List<String> _promptBlocks;
@JsonKey() List<String> get promptBlocks {
  if (_promptBlocks is EqualUnmodifiableListView) return _promptBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_promptBlocks);
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

 final  String? modelStrategy;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodeStrategyLlm&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._promptBlocks, _promptBlocks)&&const DeepCollectionEquality().equals(other._preHooks, _preHooks)&&const DeepCollectionEquality().equals(other._postHooks, _postHooks)&&(identical(other.safety, safety) || other.safety == safety)&&const DeepCollectionEquality().equals(other._allowedMcpTools, _allowedMcpTools)&&(identical(other.modelStrategy, modelStrategy) || other.modelStrategy == modelStrategy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,name,description,const DeepCollectionEquality().hash(_promptBlocks),const DeepCollectionEquality().hash(_preHooks),const DeepCollectionEquality().hash(_postHooks),safety,const DeepCollectionEquality().hash(_allowedMcpTools),modelStrategy);

@override
String toString() {
  return 'NodeStrategy.llm(id: $id, slug: $slug, name: $name, description: $description, promptBlocks: $promptBlocks, preHooks: $preHooks, postHooks: $postHooks, safety: $safety, allowedMcpTools: $allowedMcpTools, modelStrategy: $modelStrategy)';
}


}

/// @nodoc
abstract mixin class $NodeStrategyLlmCopyWith<$Res> implements $NodeStrategyCopyWith<$Res> {
  factory $NodeStrategyLlmCopyWith(NodeStrategyLlm value, $Res Function(NodeStrategyLlm) _then) = _$NodeStrategyLlmCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText? description, List<String> promptBlocks, List<String> preHooks, List<String> postHooks, String safety, List<String> allowedMcpTools, String? modelStrategy
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = freezed,Object? promptBlocks = null,Object? preHooks = null,Object? postHooks = null,Object? safety = null,Object? allowedMcpTools = null,Object? modelStrategy = freezed,}) {
  return _then(NodeStrategyLlm(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,promptBlocks: null == promptBlocks ? _self._promptBlocks : promptBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,preHooks: null == preHooks ? _self._preHooks : preHooks // ignore: cast_nullable_to_non_nullable
as List<String>,postHooks: null == postHooks ? _self._postHooks : postHooks // ignore: cast_nullable_to_non_nullable
as List<String>,safety: null == safety ? _self.safety : safety // ignore: cast_nullable_to_non_nullable
as String,allowedMcpTools: null == allowedMcpTools ? _self._allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
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
@JsonSerializable()

class NodeStrategyLogic extends NodeStrategy {
  const NodeStrategyLogic({@StrictOpaqueIdConverter() required this.id, required this.slug, required this.name, this.description, required this.hook, this.taskKey, final  List<String> preHooks = const [], final  List<String> postHooks = const [], this.safety = 'safe', final  List<String> allowedMcpTools = const [], final  String? $type}): _preHooks = preHooks,_postHooks = postHooks,_allowedMcpTools = allowedMcpTools,$type = $type ?? 'logic',super._();
  factory NodeStrategyLogic.fromJson(Map<String, dynamic> json) => _$NodeStrategyLogicFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override final  I18nText name;
@override final  I18nText? description;
 final  String hook;
 final  String? taskKey;
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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is NodeStrategyLogic&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.hook, hook) || other.hook == hook)&&(identical(other.taskKey, taskKey) || other.taskKey == taskKey)&&const DeepCollectionEquality().equals(other._preHooks, _preHooks)&&const DeepCollectionEquality().equals(other._postHooks, _postHooks)&&(identical(other.safety, safety) || other.safety == safety)&&const DeepCollectionEquality().equals(other._allowedMcpTools, _allowedMcpTools));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,name,description,hook,taskKey,const DeepCollectionEquality().hash(_preHooks),const DeepCollectionEquality().hash(_postHooks),safety,const DeepCollectionEquality().hash(_allowedMcpTools));

@override
String toString() {
  return 'NodeStrategy.logic(id: $id, slug: $slug, name: $name, description: $description, hook: $hook, taskKey: $taskKey, preHooks: $preHooks, postHooks: $postHooks, safety: $safety, allowedMcpTools: $allowedMcpTools)';
}


}

/// @nodoc
abstract mixin class $NodeStrategyLogicCopyWith<$Res> implements $NodeStrategyCopyWith<$Res> {
  factory $NodeStrategyLogicCopyWith(NodeStrategyLogic value, $Res Function(NodeStrategyLogic) _then) = _$NodeStrategyLogicCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText? description, String hook, String? taskKey, List<String> preHooks, List<String> postHooks, String safety, List<String> allowedMcpTools
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = freezed,Object? hook = null,Object? taskKey = freezed,Object? preHooks = null,Object? postHooks = null,Object? safety = null,Object? allowedMcpTools = null,}) {
  return _then(NodeStrategyLogic(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,hook: null == hook ? _self.hook : hook // ignore: cast_nullable_to_non_nullable
as String,taskKey: freezed == taskKey ? _self.taskKey : taskKey // ignore: cast_nullable_to_non_nullable
as String?,preHooks: null == preHooks ? _self._preHooks : preHooks // ignore: cast_nullable_to_non_nullable
as List<String>,postHooks: null == postHooks ? _self._postHooks : postHooks // ignore: cast_nullable_to_non_nullable
as List<String>,safety: null == safety ? _self.safety : safety // ignore: cast_nullable_to_non_nullable
as String,allowedMcpTools: null == allowedMcpTools ? _self._allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,
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

@StrictOpaqueIdConverter() String get id; String get slug; I18nText get name; I18nText get description; String get status; int get version; bool get isPublic; String? get organizationId; Map<String, dynamic> get uiSchema; Map<String, OutputProfile> get outputProfiles; String get defaultProfileId; List<ExpectedInput> get expectedInputs; List<StepRule> get steps;
/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowCopyWith<Workflow> get copyWith => _$WorkflowCopyWithImpl<Workflow>(this as Workflow, _$identity);

  /// Serializes this Workflow to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'Workflow(id: $id, slug: $slug, name: $name, description: $description, status: $status, version: $version, isPublic: $isPublic, organizationId: $organizationId, uiSchema: $uiSchema, outputProfiles: $outputProfiles, defaultProfileId: $defaultProfileId, expectedInputs: $expectedInputs, steps: $steps)';
}


}

/// @nodoc
abstract mixin class $WorkflowCopyWith<$Res>  {
  factory $WorkflowCopyWith(Workflow value, $Res Function(Workflow) _then) = _$WorkflowCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText description, String status, int version, bool isPublic, String? organizationId, Map<String, dynamic> uiSchema, Map<String, OutputProfile> outputProfiles, String defaultProfileId, List<ExpectedInput> expectedInputs, List<StepRule> steps
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = null,Object? status = null,Object? version = null,Object? isPublic = null,Object? organizationId = freezed,Object? uiSchema = null,Object? outputProfiles = null,Object? defaultProfileId = null,Object? expectedInputs = null,Object? steps = null,}) {
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
as Map<String, OutputProfile>,defaultProfileId: null == defaultProfileId ? _self.defaultProfileId : defaultProfileId // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText description,  String status,  int version,  bool isPublic,  String? organizationId,  Map<String, dynamic> uiSchema,  Map<String, OutputProfile> outputProfiles,  String defaultProfileId,  List<ExpectedInput> expectedInputs,  List<StepRule> steps)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Workflow() when $default != null:
return $default(_that.id,_that.slug,_that.name,_that.description,_that.status,_that.version,_that.isPublic,_that.organizationId,_that.uiSchema,_that.outputProfiles,_that.defaultProfileId,_that.expectedInputs,_that.steps);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText description,  String status,  int version,  bool isPublic,  String? organizationId,  Map<String, dynamic> uiSchema,  Map<String, OutputProfile> outputProfiles,  String defaultProfileId,  List<ExpectedInput> expectedInputs,  List<StepRule> steps)  $default,) {final _that = this;
switch (_that) {
case _Workflow():
return $default(_that.id,_that.slug,_that.name,_that.description,_that.status,_that.version,_that.isPublic,_that.organizationId,_that.uiSchema,_that.outputProfiles,_that.defaultProfileId,_that.expectedInputs,_that.steps);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  I18nText name,  I18nText description,  String status,  int version,  bool isPublic,  String? organizationId,  Map<String, dynamic> uiSchema,  Map<String, OutputProfile> outputProfiles,  String defaultProfileId,  List<ExpectedInput> expectedInputs,  List<StepRule> steps)?  $default,) {final _that = this;
switch (_that) {
case _Workflow() when $default != null:
return $default(_that.id,_that.slug,_that.name,_that.description,_that.status,_that.version,_that.isPublic,_that.organizationId,_that.uiSchema,_that.outputProfiles,_that.defaultProfileId,_that.expectedInputs,_that.steps);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Workflow extends Workflow {
  const _Workflow({@StrictOpaqueIdConverter() required this.id, required this.slug, required this.name, required this.description, this.status = "draft", this.version = 1, this.isPublic = false, this.organizationId, final  Map<String, dynamic> uiSchema = const {}, final  Map<String, OutputProfile> outputProfiles = const {}, this.defaultProfileId = "default", final  List<ExpectedInput> expectedInputs = const [], final  List<StepRule> steps = const []}): _uiSchema = uiSchema,_outputProfiles = outputProfiles,_expectedInputs = expectedInputs,_steps = steps,super._();
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

 final  Map<String, OutputProfile> _outputProfiles;
@override@JsonKey() Map<String, OutputProfile> get outputProfiles {
  if (_outputProfiles is EqualUnmodifiableMapView) return _outputProfiles;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_outputProfiles);
}

@override@JsonKey() final  String defaultProfileId;
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
  return 'Workflow(id: $id, slug: $slug, name: $name, description: $description, status: $status, version: $version, isPublic: $isPublic, organizationId: $organizationId, uiSchema: $uiSchema, outputProfiles: $outputProfiles, defaultProfileId: $defaultProfileId, expectedInputs: $expectedInputs, steps: $steps)';
}


}

/// @nodoc
abstract mixin class _$WorkflowCopyWith<$Res> implements $WorkflowCopyWith<$Res> {
  factory _$WorkflowCopyWith(_Workflow value, $Res Function(_Workflow) _then) = __$WorkflowCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, I18nText name, I18nText description, String status, int version, bool isPublic, String? organizationId, Map<String, dynamic> uiSchema, Map<String, OutputProfile> outputProfiles, String defaultProfileId, List<ExpectedInput> expectedInputs, List<StepRule> steps
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? name = null,Object? description = null,Object? status = null,Object? version = null,Object? isPublic = null,Object? organizationId = freezed,Object? uiSchema = null,Object? outputProfiles = null,Object? defaultProfileId = null,Object? expectedInputs = null,Object? steps = null,}) {
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
as Map<String, OutputProfile>,defaultProfileId: null == defaultProfileId ? _self.defaultProfileId : defaultProfileId // ignore: cast_nullable_to_non_nullable
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
