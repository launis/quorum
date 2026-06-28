// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_data_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
SduiBlockDTO _$SduiBlockDTOFromJson(
  Map<String, dynamic> json
) {
        switch (json['block_type']) {
                  case 'paragraph':
          return SduiParagraphBlock.fromJson(
            json
          );
                case 'bullet_list':
          return SduiBulletListBlock.fromJson(
            json
          );
                case 'alert_box':
          return SduiAlertBoxBlock.fromJson(
            json
          );
                case 'hero_insight':
          return SduiHeroInsightBlock.fromJson(
            json
          );
                case 'markdown':
          return SduiMarkdownBlock.fromJson(
            json
          );
        
          default:
            throw CheckedFromJsonException(
  json,
  'block_type',
  'SduiBlockDTO',
  'Invalid union type "${json['block_type']}"!'
);
        }
      
}

/// @nodoc
mixin _$SduiBlockDTO {



  /// Serializes this SduiBlockDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiBlockDTO);
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'SduiBlockDTO()';
}


}

/// @nodoc
class $SduiBlockDTOCopyWith<$Res>  {
$SduiBlockDTOCopyWith(SduiBlockDTO _, $Res Function(SduiBlockDTO) __);
}


/// Adds pattern-matching-related methods to [SduiBlockDTO].
extension SduiBlockDTOPatterns on SduiBlockDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( SduiParagraphBlock value)?  paragraph,TResult Function( SduiBulletListBlock value)?  bulletList,TResult Function( SduiAlertBoxBlock value)?  alertBox,TResult Function( SduiHeroInsightBlock value)?  heroInsight,TResult Function( SduiMarkdownBlock value)?  markdown,required TResult orElse(),}){
final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that);case SduiMarkdownBlock() when markdown != null:
return markdown(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( SduiParagraphBlock value)  paragraph,required TResult Function( SduiBulletListBlock value)  bulletList,required TResult Function( SduiAlertBoxBlock value)  alertBox,required TResult Function( SduiHeroInsightBlock value)  heroInsight,required TResult Function( SduiMarkdownBlock value)  markdown,}){
final _that = this;
switch (_that) {
case SduiParagraphBlock():
return paragraph(_that);case SduiBulletListBlock():
return bulletList(_that);case SduiAlertBoxBlock():
return alertBox(_that);case SduiHeroInsightBlock():
return heroInsight(_that);case SduiMarkdownBlock():
return markdown(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( SduiParagraphBlock value)?  paragraph,TResult? Function( SduiBulletListBlock value)?  bulletList,TResult? Function( SduiAlertBoxBlock value)?  alertBox,TResult? Function( SduiHeroInsightBlock value)?  heroInsight,TResult? Function( SduiMarkdownBlock value)?  markdown,}){
final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that);case SduiMarkdownBlock() when markdown != null:
return markdown(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( String text,  List<int> citations)?  paragraph,TResult Function( List<SduiBulletListItemDTO> items)?  bulletList,TResult Function( String text,  String severity,  List<int> citations)?  alertBox,TResult Function( String text)?  heroInsight,TResult Function( String text)?  markdown,required TResult orElse(),}) {final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that.text,_that.citations);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that.items);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that.text,_that.severity,_that.citations);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that.text);case SduiMarkdownBlock() when markdown != null:
return markdown(_that.text);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( String text,  List<int> citations)  paragraph,required TResult Function( List<SduiBulletListItemDTO> items)  bulletList,required TResult Function( String text,  String severity,  List<int> citations)  alertBox,required TResult Function( String text)  heroInsight,required TResult Function( String text)  markdown,}) {final _that = this;
switch (_that) {
case SduiParagraphBlock():
return paragraph(_that.text,_that.citations);case SduiBulletListBlock():
return bulletList(_that.items);case SduiAlertBoxBlock():
return alertBox(_that.text,_that.severity,_that.citations);case SduiHeroInsightBlock():
return heroInsight(_that.text);case SduiMarkdownBlock():
return markdown(_that.text);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( String text,  List<int> citations)?  paragraph,TResult? Function( List<SduiBulletListItemDTO> items)?  bulletList,TResult? Function( String text,  String severity,  List<int> citations)?  alertBox,TResult? Function( String text)?  heroInsight,TResult? Function( String text)?  markdown,}) {final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that.text,_that.citations);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that.items);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that.text,_that.severity,_that.citations);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that.text);case SduiMarkdownBlock() when markdown != null:
return markdown(_that.text);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiParagraphBlock extends SduiBlockDTO {
  const SduiParagraphBlock({required this.text, final  List<int> citations = const [], final  String? $type}): _citations = citations,$type = $type ?? 'paragraph',super._();
  factory SduiParagraphBlock.fromJson(Map<String, dynamic> json) => _$SduiParagraphBlockFromJson(json);

 final  String text;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiParagraphBlockCopyWith<SduiParagraphBlock> get copyWith => _$SduiParagraphBlockCopyWithImpl<SduiParagraphBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiParagraphBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiParagraphBlock&&(identical(other.text, text) || other.text == text)&&const DeepCollectionEquality().equals(other._citations, _citations));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,text,const DeepCollectionEquality().hash(_citations));

@override
String toString() {
  return 'SduiBlockDTO.paragraph(text: $text, citations: $citations)';
}


}

/// @nodoc
abstract mixin class $SduiParagraphBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiParagraphBlockCopyWith(SduiParagraphBlock value, $Res Function(SduiParagraphBlock) _then) = _$SduiParagraphBlockCopyWithImpl;
@useResult
$Res call({
 String text, List<int> citations
});




}
/// @nodoc
class _$SduiParagraphBlockCopyWithImpl<$Res>
    implements $SduiParagraphBlockCopyWith<$Res> {
  _$SduiParagraphBlockCopyWithImpl(this._self, this._then);

  final SduiParagraphBlock _self;
  final $Res Function(SduiParagraphBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? text = null,Object? citations = null,}) {
  return _then(SduiParagraphBlock(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiBulletListBlock extends SduiBlockDTO {
  const SduiBulletListBlock({required final  List<SduiBulletListItemDTO> items, final  String? $type}): _items = items,$type = $type ?? 'bullet_list',super._();
  factory SduiBulletListBlock.fromJson(Map<String, dynamic> json) => _$SduiBulletListBlockFromJson(json);

 final  List<SduiBulletListItemDTO> _items;
 List<SduiBulletListItemDTO> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBulletListBlockCopyWith<SduiBulletListBlock> get copyWith => _$SduiBulletListBlockCopyWithImpl<SduiBulletListBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiBulletListBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiBulletListBlock&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'SduiBlockDTO.bulletList(items: $items)';
}


}

/// @nodoc
abstract mixin class $SduiBulletListBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiBulletListBlockCopyWith(SduiBulletListBlock value, $Res Function(SduiBulletListBlock) _then) = _$SduiBulletListBlockCopyWithImpl;
@useResult
$Res call({
 List<SduiBulletListItemDTO> items
});




}
/// @nodoc
class _$SduiBulletListBlockCopyWithImpl<$Res>
    implements $SduiBulletListBlockCopyWith<$Res> {
  _$SduiBulletListBlockCopyWithImpl(this._self, this._then);

  final SduiBulletListBlock _self;
  final $Res Function(SduiBulletListBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? items = null,}) {
  return _then(SduiBulletListBlock(
items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<SduiBulletListItemDTO>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiAlertBoxBlock extends SduiBlockDTO {
  const SduiAlertBoxBlock({required this.text, required this.severity, final  List<int> citations = const [], final  String? $type}): _citations = citations,$type = $type ?? 'alert_box',super._();
  factory SduiAlertBoxBlock.fromJson(Map<String, dynamic> json) => _$SduiAlertBoxBlockFromJson(json);

 final  String text;
 final  String severity;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiAlertBoxBlockCopyWith<SduiAlertBoxBlock> get copyWith => _$SduiAlertBoxBlockCopyWithImpl<SduiAlertBoxBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiAlertBoxBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiAlertBoxBlock&&(identical(other.text, text) || other.text == text)&&(identical(other.severity, severity) || other.severity == severity)&&const DeepCollectionEquality().equals(other._citations, _citations));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,text,severity,const DeepCollectionEquality().hash(_citations));

@override
String toString() {
  return 'SduiBlockDTO.alertBox(text: $text, severity: $severity, citations: $citations)';
}


}

/// @nodoc
abstract mixin class $SduiAlertBoxBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiAlertBoxBlockCopyWith(SduiAlertBoxBlock value, $Res Function(SduiAlertBoxBlock) _then) = _$SduiAlertBoxBlockCopyWithImpl;
@useResult
$Res call({
 String text, String severity, List<int> citations
});




}
/// @nodoc
class _$SduiAlertBoxBlockCopyWithImpl<$Res>
    implements $SduiAlertBoxBlockCopyWith<$Res> {
  _$SduiAlertBoxBlockCopyWithImpl(this._self, this._then);

  final SduiAlertBoxBlock _self;
  final $Res Function(SduiAlertBoxBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? text = null,Object? severity = null,Object? citations = null,}) {
  return _then(SduiAlertBoxBlock(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiHeroInsightBlock extends SduiBlockDTO {
  const SduiHeroInsightBlock({required this.text, final  String? $type}): $type = $type ?? 'hero_insight',super._();
  factory SduiHeroInsightBlock.fromJson(Map<String, dynamic> json) => _$SduiHeroInsightBlockFromJson(json);

 final  String text;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiHeroInsightBlockCopyWith<SduiHeroInsightBlock> get copyWith => _$SduiHeroInsightBlockCopyWithImpl<SduiHeroInsightBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiHeroInsightBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiHeroInsightBlock&&(identical(other.text, text) || other.text == text));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,text);

@override
String toString() {
  return 'SduiBlockDTO.heroInsight(text: $text)';
}


}

/// @nodoc
abstract mixin class $SduiHeroInsightBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiHeroInsightBlockCopyWith(SduiHeroInsightBlock value, $Res Function(SduiHeroInsightBlock) _then) = _$SduiHeroInsightBlockCopyWithImpl;
@useResult
$Res call({
 String text
});




}
/// @nodoc
class _$SduiHeroInsightBlockCopyWithImpl<$Res>
    implements $SduiHeroInsightBlockCopyWith<$Res> {
  _$SduiHeroInsightBlockCopyWithImpl(this._self, this._then);

  final SduiHeroInsightBlock _self;
  final $Res Function(SduiHeroInsightBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? text = null,}) {
  return _then(SduiHeroInsightBlock(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiMarkdownBlock extends SduiBlockDTO {
  const SduiMarkdownBlock({required this.text, final  String? $type}): $type = $type ?? 'markdown',super._();
  factory SduiMarkdownBlock.fromJson(Map<String, dynamic> json) => _$SduiMarkdownBlockFromJson(json);

 final  String text;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiMarkdownBlockCopyWith<SduiMarkdownBlock> get copyWith => _$SduiMarkdownBlockCopyWithImpl<SduiMarkdownBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiMarkdownBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiMarkdownBlock&&(identical(other.text, text) || other.text == text));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,text);

@override
String toString() {
  return 'SduiBlockDTO.markdown(text: $text)';
}


}

/// @nodoc
abstract mixin class $SduiMarkdownBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiMarkdownBlockCopyWith(SduiMarkdownBlock value, $Res Function(SduiMarkdownBlock) _then) = _$SduiMarkdownBlockCopyWithImpl;
@useResult
$Res call({
 String text
});




}
/// @nodoc
class _$SduiMarkdownBlockCopyWithImpl<$Res>
    implements $SduiMarkdownBlockCopyWith<$Res> {
  _$SduiMarkdownBlockCopyWithImpl(this._self, this._then);

  final SduiMarkdownBlock _self;
  final $Res Function(SduiMarkdownBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? text = null,}) {
  return _then(SduiMarkdownBlock(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$SduiBulletListItemDTO {

 String get text; List<int> get citations;
/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBulletListItemDTOCopyWith<SduiBulletListItemDTO> get copyWith => _$SduiBulletListItemDTOCopyWithImpl<SduiBulletListItemDTO>(this as SduiBulletListItemDTO, _$identity);

  /// Serializes this SduiBulletListItemDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SduiBulletListItemDTO(text: $text, citations: $citations)';
}


}

/// @nodoc
abstract mixin class $SduiBulletListItemDTOCopyWith<$Res>  {
  factory $SduiBulletListItemDTOCopyWith(SduiBulletListItemDTO value, $Res Function(SduiBulletListItemDTO) _then) = _$SduiBulletListItemDTOCopyWithImpl;
@useResult
$Res call({
 String text, List<int> citations
});




}
/// @nodoc
class _$SduiBulletListItemDTOCopyWithImpl<$Res>
    implements $SduiBulletListItemDTOCopyWith<$Res> {
  _$SduiBulletListItemDTOCopyWithImpl(this._self, this._then);

  final SduiBulletListItemDTO _self;
  final $Res Function(SduiBulletListItemDTO) _then;

/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? text = null,Object? citations = null,}) {
  return _then(_self.copyWith(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self.citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}

}


/// Adds pattern-matching-related methods to [SduiBulletListItemDTO].
extension SduiBulletListItemDTOPatterns on SduiBulletListItemDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SduiBulletListItemDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SduiBulletListItemDTO value)  $default,){
final _that = this;
switch (_that) {
case _SduiBulletListItemDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SduiBulletListItemDTO value)?  $default,){
final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String text,  List<int> citations)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
return $default(_that.text,_that.citations);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String text,  List<int> citations)  $default,) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO():
return $default(_that.text,_that.citations);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String text,  List<int> citations)?  $default,) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
return $default(_that.text,_that.citations);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _SduiBulletListItemDTO implements SduiBulletListItemDTO {
  const _SduiBulletListItemDTO({required this.text, final  List<int> citations = const []}): _citations = citations;
  factory _SduiBulletListItemDTO.fromJson(Map<String, dynamic> json) => _$SduiBulletListItemDTOFromJson(json);

@override final  String text;
 final  List<int> _citations;
@override@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}


/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SduiBulletListItemDTOCopyWith<_SduiBulletListItemDTO> get copyWith => __$SduiBulletListItemDTOCopyWithImpl<_SduiBulletListItemDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiBulletListItemDTOToJson(this, );
}



@override
String toString() {
  return 'SduiBulletListItemDTO(text: $text, citations: $citations)';
}


}

/// @nodoc
abstract mixin class _$SduiBulletListItemDTOCopyWith<$Res> implements $SduiBulletListItemDTOCopyWith<$Res> {
  factory _$SduiBulletListItemDTOCopyWith(_SduiBulletListItemDTO value, $Res Function(_SduiBulletListItemDTO) _then) = __$SduiBulletListItemDTOCopyWithImpl;
@override @useResult
$Res call({
 String text, List<int> citations
});




}
/// @nodoc
class __$SduiBulletListItemDTOCopyWithImpl<$Res>
    implements _$SduiBulletListItemDTOCopyWith<$Res> {
  __$SduiBulletListItemDTOCopyWithImpl(this._self, this._then);

  final _SduiBulletListItemDTO _self;
  final $Res Function(_SduiBulletListItemDTO) _then;

/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? text = null,Object? citations = null,}) {
  return _then(_SduiBulletListItemDTO(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,
  ));
}


}


/// @nodoc
mixin _$ReportLayoutDTO {

@JsonKey(name: 'preset_view') PresetView get presetView;@JsonKey(name: 'matrix_type') String? get matrixType; I18nText? get title; I18nText? get description; List<MatrixScorecardRowDto> get axes;@JsonKey(name: 'visible_columns') List<String> get visibleColumns;@JsonKey(name: 'text_delivery_mode') String get textDeliveryMode; Map<String, dynamic>? get synthesis;@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> get synthesisBlocks;
/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportLayoutDTOCopyWith<ReportLayoutDTO> get copyWith => _$ReportLayoutDTOCopyWithImpl<ReportLayoutDTO>(this as ReportLayoutDTO, _$identity);

  /// Serializes this ReportLayoutDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportLayoutDTO(presetView: $presetView, matrixType: $matrixType, title: $title, description: $description, axes: $axes, visibleColumns: $visibleColumns, textDeliveryMode: $textDeliveryMode, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks)';
}


}

/// @nodoc
abstract mixin class $ReportLayoutDTOCopyWith<$Res>  {
  factory $ReportLayoutDTOCopyWith(ReportLayoutDTO value, $Res Function(ReportLayoutDTO) _then) = _$ReportLayoutDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'preset_view') PresetView presetView,@JsonKey(name: 'matrix_type') String? matrixType, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'visible_columns') List<String> visibleColumns,@JsonKey(name: 'text_delivery_mode') String textDeliveryMode, Map<String, dynamic>? synthesis,@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> synthesisBlocks
});


$I18nTextCopyWith<$Res>? get title;$I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class _$ReportLayoutDTOCopyWithImpl<$Res>
    implements $ReportLayoutDTOCopyWith<$Res> {
  _$ReportLayoutDTOCopyWithImpl(this._self, this._then);

  final ReportLayoutDTO _self;
  final $Res Function(ReportLayoutDTO) _then;

/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,Object? matrixType = freezed,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? visibleColumns = null,Object? textDeliveryMode = null,Object? synthesis = freezed,Object? synthesisBlocks = null,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,matrixType: freezed == matrixType ? _self.matrixType : matrixType // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self.axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,visibleColumns: null == visibleColumns ? _self.visibleColumns : visibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as String,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,synthesisBlocks: null == synthesisBlocks ? _self.synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}
/// Create a copy of ReportLayoutDTO
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
}/// Create a copy of ReportLayoutDTO
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


/// Adds pattern-matching-related methods to [ReportLayoutDTO].
extension ReportLayoutDTOPatterns on ReportLayoutDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportLayoutDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportLayoutDTO value)  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportLayoutDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  PresetView presetView, @JsonKey(name: 'matrix_type')  String? matrixType,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'visible_columns')  List<String> visibleColumns, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO> synthesisBlocks)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
return $default(_that.presetView,_that.matrixType,_that.title,_that.description,_that.axes,_that.visibleColumns,_that.textDeliveryMode,_that.synthesis,_that.synthesisBlocks);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  PresetView presetView, @JsonKey(name: 'matrix_type')  String? matrixType,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'visible_columns')  List<String> visibleColumns, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO> synthesisBlocks)  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDTO():
return $default(_that.presetView,_that.matrixType,_that.title,_that.description,_that.axes,_that.visibleColumns,_that.textDeliveryMode,_that.synthesis,_that.synthesisBlocks);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'preset_view')  PresetView presetView, @JsonKey(name: 'matrix_type')  String? matrixType,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'visible_columns')  List<String> visibleColumns, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO> synthesisBlocks)?  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
return $default(_that.presetView,_that.matrixType,_that.title,_that.description,_that.axes,_that.visibleColumns,_that.textDeliveryMode,_that.synthesis,_that.synthesisBlocks);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportLayoutDTO implements ReportLayoutDTO {
  const _ReportLayoutDTO({@JsonKey(name: 'preset_view') required this.presetView, @JsonKey(name: 'matrix_type') this.matrixType, this.title, this.description, final  List<MatrixScorecardRowDto> axes = const [], @JsonKey(name: 'visible_columns') final  List<String> visibleColumns = const ['label', 'score', 'distribution', 'row_explanation'], @JsonKey(name: 'text_delivery_mode') required this.textDeliveryMode, final  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_blocks') final  List<SduiBlockDTO> synthesisBlocks = const []}): _axes = axes,_visibleColumns = visibleColumns,_synthesis = synthesis,_synthesisBlocks = synthesisBlocks;
  factory _ReportLayoutDTO.fromJson(Map<String, dynamic> json) => _$ReportLayoutDTOFromJson(json);

@override@JsonKey(name: 'preset_view') final  PresetView presetView;
@override@JsonKey(name: 'matrix_type') final  String? matrixType;
@override final  I18nText? title;
@override final  I18nText? description;
 final  List<MatrixScorecardRowDto> _axes;
@override@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}

 final  List<String> _visibleColumns;
@override@JsonKey(name: 'visible_columns') List<String> get visibleColumns {
  if (_visibleColumns is EqualUnmodifiableListView) return _visibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleColumns);
}

@override@JsonKey(name: 'text_delivery_mode') final  String textDeliveryMode;
 final  Map<String, dynamic>? _synthesis;
@override Map<String, dynamic>? get synthesis {
  final value = _synthesis;
  if (value == null) return null;
  if (_synthesis is EqualUnmodifiableMapView) return _synthesis;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  List<SduiBlockDTO> _synthesisBlocks;
@override@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> get synthesisBlocks {
  if (_synthesisBlocks is EqualUnmodifiableListView) return _synthesisBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_synthesisBlocks);
}


/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportLayoutDTOCopyWith<_ReportLayoutDTO> get copyWith => __$ReportLayoutDTOCopyWithImpl<_ReportLayoutDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportLayoutDTOToJson(this, );
}



@override
String toString() {
  return 'ReportLayoutDTO(presetView: $presetView, matrixType: $matrixType, title: $title, description: $description, axes: $axes, visibleColumns: $visibleColumns, textDeliveryMode: $textDeliveryMode, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks)';
}


}

/// @nodoc
abstract mixin class _$ReportLayoutDTOCopyWith<$Res> implements $ReportLayoutDTOCopyWith<$Res> {
  factory _$ReportLayoutDTOCopyWith(_ReportLayoutDTO value, $Res Function(_ReportLayoutDTO) _then) = __$ReportLayoutDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'preset_view') PresetView presetView,@JsonKey(name: 'matrix_type') String? matrixType, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'visible_columns') List<String> visibleColumns,@JsonKey(name: 'text_delivery_mode') String textDeliveryMode, Map<String, dynamic>? synthesis,@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> synthesisBlocks
});


@override $I18nTextCopyWith<$Res>? get title;@override $I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class __$ReportLayoutDTOCopyWithImpl<$Res>
    implements _$ReportLayoutDTOCopyWith<$Res> {
  __$ReportLayoutDTOCopyWithImpl(this._self, this._then);

  final _ReportLayoutDTO _self;
  final $Res Function(_ReportLayoutDTO) _then;

/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,Object? matrixType = freezed,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? visibleColumns = null,Object? textDeliveryMode = null,Object? synthesis = freezed,Object? synthesisBlocks = null,}) {
  return _then(_ReportLayoutDTO(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,matrixType: freezed == matrixType ? _self.matrixType : matrixType // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,visibleColumns: null == visibleColumns ? _self._visibleColumns : visibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as String,synthesis: freezed == synthesis ? _self._synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,synthesisBlocks: null == synthesisBlocks ? _self._synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}

/// Create a copy of ReportLayoutDTO
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
}/// Create a copy of ReportLayoutDTO
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
mixin _$MCPToolAuditDTO {

 String? get id;@JsonKey(name: 'tool_id') String get toolId;@JsonKey(name: 'step_name') String get stepName;@JsonKey(name: 'claim_text') String? get claimText; String get query; String get reasoning;@JsonKey(name: 'knowledge_gap') String? get knowledgeGap;@JsonKey(name: 'search_rationale') String? get searchRationale;@JsonKey(name: 'response_summary') String get responseSummary;@JsonKey(name: 'source_urls') List<String> get sourceUrls;@JsonKey(name: 'impacted_axis_names') List<String> get impactedAxisNames; String? get timestamp;@JsonKey(name: 'duration_ms') int get durationMs;
/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MCPToolAuditDTOCopyWith<MCPToolAuditDTO> get copyWith => _$MCPToolAuditDTOCopyWithImpl<MCPToolAuditDTO>(this as MCPToolAuditDTO, _$identity);

  /// Serializes this MCPToolAuditDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MCPToolAuditDTO(id: $id, toolId: $toolId, stepName: $stepName, claimText: $claimText, query: $query, reasoning: $reasoning, knowledgeGap: $knowledgeGap, searchRationale: $searchRationale, responseSummary: $responseSummary, sourceUrls: $sourceUrls, impactedAxisNames: $impactedAxisNames, timestamp: $timestamp, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class $MCPToolAuditDTOCopyWith<$Res>  {
  factory $MCPToolAuditDTOCopyWith(MCPToolAuditDTO value, $Res Function(MCPToolAuditDTO) _then) = _$MCPToolAuditDTOCopyWithImpl;
@useResult
$Res call({
 String? id,@JsonKey(name: 'tool_id') String toolId,@JsonKey(name: 'step_name') String stepName,@JsonKey(name: 'claim_text') String? claimText, String query, String reasoning,@JsonKey(name: 'knowledge_gap') String? knowledgeGap,@JsonKey(name: 'search_rationale') String? searchRationale,@JsonKey(name: 'response_summary') String responseSummary,@JsonKey(name: 'source_urls') List<String> sourceUrls,@JsonKey(name: 'impacted_axis_names') List<String> impactedAxisNames, String? timestamp,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class _$MCPToolAuditDTOCopyWithImpl<$Res>
    implements $MCPToolAuditDTOCopyWith<$Res> {
  _$MCPToolAuditDTOCopyWithImpl(this._self, this._then);

  final MCPToolAuditDTO _self;
  final $Res Function(MCPToolAuditDTO) _then;

/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? toolId = null,Object? stepName = null,Object? claimText = freezed,Object? query = null,Object? reasoning = null,Object? knowledgeGap = freezed,Object? searchRationale = freezed,Object? responseSummary = null,Object? sourceUrls = null,Object? impactedAxisNames = null,Object? timestamp = freezed,Object? durationMs = null,}) {
  return _then(_self.copyWith(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,stepName: null == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String,claimText: freezed == claimText ? _self.claimText : claimText // ignore: cast_nullable_to_non_nullable
as String?,query: null == query ? _self.query : query // ignore: cast_nullable_to_non_nullable
as String,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,knowledgeGap: freezed == knowledgeGap ? _self.knowledgeGap : knowledgeGap // ignore: cast_nullable_to_non_nullable
as String?,searchRationale: freezed == searchRationale ? _self.searchRationale : searchRationale // ignore: cast_nullable_to_non_nullable
as String?,responseSummary: null == responseSummary ? _self.responseSummary : responseSummary // ignore: cast_nullable_to_non_nullable
as String,sourceUrls: null == sourceUrls ? _self.sourceUrls : sourceUrls // ignore: cast_nullable_to_non_nullable
as List<String>,impactedAxisNames: null == impactedAxisNames ? _self.impactedAxisNames : impactedAxisNames // ignore: cast_nullable_to_non_nullable
as List<String>,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [MCPToolAuditDTO].
extension MCPToolAuditDTOPatterns on MCPToolAuditDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MCPToolAuditDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MCPToolAuditDTO value)  $default,){
final _that = this;
switch (_that) {
case _MCPToolAuditDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MCPToolAuditDTO value)?  $default,){
final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName, @JsonKey(name: 'claim_text')  String? claimText,  String query,  String reasoning, @JsonKey(name: 'knowledge_gap')  String? knowledgeGap, @JsonKey(name: 'search_rationale')  String? searchRationale, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls, @JsonKey(name: 'impacted_axis_names')  List<String> impactedAxisNames,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
return $default(_that.id,_that.toolId,_that.stepName,_that.claimText,_that.query,_that.reasoning,_that.knowledgeGap,_that.searchRationale,_that.responseSummary,_that.sourceUrls,_that.impactedAxisNames,_that.timestamp,_that.durationMs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName, @JsonKey(name: 'claim_text')  String? claimText,  String query,  String reasoning, @JsonKey(name: 'knowledge_gap')  String? knowledgeGap, @JsonKey(name: 'search_rationale')  String? searchRationale, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls, @JsonKey(name: 'impacted_axis_names')  List<String> impactedAxisNames,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)  $default,) {final _that = this;
switch (_that) {
case _MCPToolAuditDTO():
return $default(_that.id,_that.toolId,_that.stepName,_that.claimText,_that.query,_that.reasoning,_that.knowledgeGap,_that.searchRationale,_that.responseSummary,_that.sourceUrls,_that.impactedAxisNames,_that.timestamp,_that.durationMs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName, @JsonKey(name: 'claim_text')  String? claimText,  String query,  String reasoning, @JsonKey(name: 'knowledge_gap')  String? knowledgeGap, @JsonKey(name: 'search_rationale')  String? searchRationale, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls, @JsonKey(name: 'impacted_axis_names')  List<String> impactedAxisNames,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,) {final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
return $default(_that.id,_that.toolId,_that.stepName,_that.claimText,_that.query,_that.reasoning,_that.knowledgeGap,_that.searchRationale,_that.responseSummary,_that.sourceUrls,_that.impactedAxisNames,_that.timestamp,_that.durationMs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MCPToolAuditDTO implements MCPToolAuditDTO {
  const _MCPToolAuditDTO({this.id, @JsonKey(name: 'tool_id') required this.toolId, @JsonKey(name: 'step_name') required this.stepName, @JsonKey(name: 'claim_text') this.claimText, required this.query, this.reasoning = '', @JsonKey(name: 'knowledge_gap') this.knowledgeGap, @JsonKey(name: 'search_rationale') this.searchRationale, @JsonKey(name: 'response_summary') this.responseSummary = '', @JsonKey(name: 'source_urls') final  List<String> sourceUrls = const [], @JsonKey(name: 'impacted_axis_names') final  List<String> impactedAxisNames = const [], this.timestamp, @JsonKey(name: 'duration_ms') this.durationMs = 0}): _sourceUrls = sourceUrls,_impactedAxisNames = impactedAxisNames;
  factory _MCPToolAuditDTO.fromJson(Map<String, dynamic> json) => _$MCPToolAuditDTOFromJson(json);

@override final  String? id;
@override@JsonKey(name: 'tool_id') final  String toolId;
@override@JsonKey(name: 'step_name') final  String stepName;
@override@JsonKey(name: 'claim_text') final  String? claimText;
@override final  String query;
@override@JsonKey() final  String reasoning;
@override@JsonKey(name: 'knowledge_gap') final  String? knowledgeGap;
@override@JsonKey(name: 'search_rationale') final  String? searchRationale;
@override@JsonKey(name: 'response_summary') final  String responseSummary;
 final  List<String> _sourceUrls;
@override@JsonKey(name: 'source_urls') List<String> get sourceUrls {
  if (_sourceUrls is EqualUnmodifiableListView) return _sourceUrls;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sourceUrls);
}

 final  List<String> _impactedAxisNames;
@override@JsonKey(name: 'impacted_axis_names') List<String> get impactedAxisNames {
  if (_impactedAxisNames is EqualUnmodifiableListView) return _impactedAxisNames;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_impactedAxisNames);
}

@override final  String? timestamp;
@override@JsonKey(name: 'duration_ms') final  int durationMs;

/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MCPToolAuditDTOCopyWith<_MCPToolAuditDTO> get copyWith => __$MCPToolAuditDTOCopyWithImpl<_MCPToolAuditDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MCPToolAuditDTOToJson(this, );
}



@override
String toString() {
  return 'MCPToolAuditDTO(id: $id, toolId: $toolId, stepName: $stepName, claimText: $claimText, query: $query, reasoning: $reasoning, knowledgeGap: $knowledgeGap, searchRationale: $searchRationale, responseSummary: $responseSummary, sourceUrls: $sourceUrls, impactedAxisNames: $impactedAxisNames, timestamp: $timestamp, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class _$MCPToolAuditDTOCopyWith<$Res> implements $MCPToolAuditDTOCopyWith<$Res> {
  factory _$MCPToolAuditDTOCopyWith(_MCPToolAuditDTO value, $Res Function(_MCPToolAuditDTO) _then) = __$MCPToolAuditDTOCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'tool_id') String toolId,@JsonKey(name: 'step_name') String stepName,@JsonKey(name: 'claim_text') String? claimText, String query, String reasoning,@JsonKey(name: 'knowledge_gap') String? knowledgeGap,@JsonKey(name: 'search_rationale') String? searchRationale,@JsonKey(name: 'response_summary') String responseSummary,@JsonKey(name: 'source_urls') List<String> sourceUrls,@JsonKey(name: 'impacted_axis_names') List<String> impactedAxisNames, String? timestamp,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class __$MCPToolAuditDTOCopyWithImpl<$Res>
    implements _$MCPToolAuditDTOCopyWith<$Res> {
  __$MCPToolAuditDTOCopyWithImpl(this._self, this._then);

  final _MCPToolAuditDTO _self;
  final $Res Function(_MCPToolAuditDTO) _then;

/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? toolId = null,Object? stepName = null,Object? claimText = freezed,Object? query = null,Object? reasoning = null,Object? knowledgeGap = freezed,Object? searchRationale = freezed,Object? responseSummary = null,Object? sourceUrls = null,Object? impactedAxisNames = null,Object? timestamp = freezed,Object? durationMs = null,}) {
  return _then(_MCPToolAuditDTO(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,stepName: null == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String,claimText: freezed == claimText ? _self.claimText : claimText // ignore: cast_nullable_to_non_nullable
as String?,query: null == query ? _self.query : query // ignore: cast_nullable_to_non_nullable
as String,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,knowledgeGap: freezed == knowledgeGap ? _self.knowledgeGap : knowledgeGap // ignore: cast_nullable_to_non_nullable
as String?,searchRationale: freezed == searchRationale ? _self.searchRationale : searchRationale // ignore: cast_nullable_to_non_nullable
as String?,responseSummary: null == responseSummary ? _self.responseSummary : responseSummary // ignore: cast_nullable_to_non_nullable
as String,sourceUrls: null == sourceUrls ? _self._sourceUrls : sourceUrls // ignore: cast_nullable_to_non_nullable
as List<String>,impactedAxisNames: null == impactedAxisNames ? _self._impactedAxisNames : impactedAxisNames // ignore: cast_nullable_to_non_nullable
as List<String>,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$ReportDataDTO {

@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'profile_id') String get profileId;@JsonKey(name: 'profile_name') I18nText? get profileName;@JsonKey(name: 'available_profiles') Map<String, I18nText> get availableProfiles;@JsonKey(name: 'global_score') double? get globalScore; List<ReportLayoutDTO> get layouts;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'local_time_str') String? get localTimeStr;@JsonKey(name: 'org_name') String? get orgName;@JsonKey(name: 'user_name') String? get userName;@JsonKey(name: 'scoring_engine_name') String? get scoringEngineName;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'custom_preface_md') String? get customPrefaceMd;@JsonKey(name: 'scoring_strategy') ScoringStrategy? get scoringStrategy;@JsonKey(name: 'cost_estimate') double? get costEstimate;@JsonKey(name: 'total_tokens') int? get totalTokens;@JsonKey(name: 'prompt_tokens') int? get promptTokens;@JsonKey(name: 'completion_tokens') int? get completionTokens;@JsonKey(name: 'reasoning_tokens') int? get reasoningTokens;@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> get mcpToolAudit;@JsonKey(name: 'has_warning') bool get hasWarning;@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks;@JsonKey(name: 'visible_metadata') List<String> get visibleMetadata;@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> get groupedExtensions;@JsonKey(name: 'penalties_applied') List<String> get penaltiesApplied;@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> get evaluativeMatrices;@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> get informationalMatrices;@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns;
/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportDataDTOCopyWith<ReportDataDTO> get copyWith => _$ReportDataDTOCopyWithImpl<ReportDataDTO>(this as ReportDataDTO, _$identity);

  /// Serializes this ReportDataDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportDataDTO(workflowId: $workflowId, profileId: $profileId, profileName: $profileName, availableProfiles: $availableProfiles, globalScore: $globalScore, layouts: $layouts, createdAt: $createdAt, localTimeStr: $localTimeStr, orgName: $orgName, userName: $userName, scoringEngineName: $scoringEngineName, strictnessLevel: $strictnessLevel, customPrefaceMd: $customPrefaceMd, scoringStrategy: $scoringStrategy, costEstimate: $costEstimate, totalTokens: $totalTokens, promptTokens: $promptTokens, completionTokens: $completionTokens, reasoningTokens: $reasoningTokens, mcpToolAudit: $mcpToolAudit, hasWarning: $hasWarning, contentBlocks: $contentBlocks, visibleMetadata: $visibleMetadata, groupedExtensions: $groupedExtensions, penaltiesApplied: $penaltiesApplied, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices, matrixVisibleColumns: $matrixVisibleColumns)';
}


}

/// @nodoc
abstract mixin class $ReportDataDTOCopyWith<$Res>  {
  factory $ReportDataDTOCopyWith(ReportDataDTO value, $Res Function(ReportDataDTO) _then) = _$ReportDataDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'profile_id') String profileId,@JsonKey(name: 'profile_name') I18nText? profileName,@JsonKey(name: 'available_profiles') Map<String, I18nText> availableProfiles,@JsonKey(name: 'global_score') double? globalScore, List<ReportLayoutDTO> layouts,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'local_time_str') String? localTimeStr,@JsonKey(name: 'org_name') String? orgName,@JsonKey(name: 'user_name') String? userName,@JsonKey(name: 'scoring_engine_name') String? scoringEngineName,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'total_tokens') int? totalTokens,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens,@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> mcpToolAudit,@JsonKey(name: 'has_warning') bool hasWarning,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks,@JsonKey(name: 'visible_metadata') List<String> visibleMetadata,@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> groupedExtensions,@JsonKey(name: 'penalties_applied') List<String> penaltiesApplied,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> informationalMatrices,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns
});


$I18nTextCopyWith<$Res>? get profileName;

}
/// @nodoc
class _$ReportDataDTOCopyWithImpl<$Res>
    implements $ReportDataDTOCopyWith<$Res> {
  _$ReportDataDTOCopyWithImpl(this._self, this._then);

  final ReportDataDTO _self;
  final $Res Function(ReportDataDTO) _then;

/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? workflowId = null,Object? profileId = null,Object? profileName = freezed,Object? availableProfiles = null,Object? globalScore = freezed,Object? layouts = null,Object? createdAt = freezed,Object? localTimeStr = freezed,Object? orgName = freezed,Object? userName = freezed,Object? scoringEngineName = freezed,Object? strictnessLevel = freezed,Object? customPrefaceMd = freezed,Object? scoringStrategy = freezed,Object? costEstimate = freezed,Object? totalTokens = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? reasoningTokens = freezed,Object? mcpToolAudit = null,Object? hasWarning = null,Object? contentBlocks = null,Object? visibleMetadata = null,Object? groupedExtensions = null,Object? penaltiesApplied = null,Object? evaluativeMatrices = null,Object? informationalMatrices = null,Object? matrixVisibleColumns = null,}) {
  return _then(_self.copyWith(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,profileName: freezed == profileName ? _self.profileName : profileName // ignore: cast_nullable_to_non_nullable
as I18nText?,availableProfiles: null == availableProfiles ? _self.availableProfiles : availableProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<ReportLayoutDTO>,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,localTimeStr: freezed == localTimeStr ? _self.localTimeStr : localTimeStr // ignore: cast_nullable_to_non_nullable
as String?,orgName: freezed == orgName ? _self.orgName : orgName // ignore: cast_nullable_to_non_nullable
as String?,userName: freezed == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String?,scoringEngineName: freezed == scoringEngineName ? _self.scoringEngineName : scoringEngineName // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,totalTokens: freezed == totalTokens ? _self.totalTokens : totalTokens // ignore: cast_nullable_to_non_nullable
as int?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,mcpToolAudit: null == mcpToolAudit ? _self.mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<MCPToolAuditDTO>,hasWarning: null == hasWarning ? _self.hasWarning : hasWarning // ignore: cast_nullable_to_non_nullable
as bool,contentBlocks: null == contentBlocks ? _self.contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,visibleMetadata: null == visibleMetadata ? _self.visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,groupedExtensions: null == groupedExtensions ? _self.groupedExtensions : groupedExtensions // ignore: cast_nullable_to_non_nullable
as Map<String, List<dynamic>>,penaltiesApplied: null == penaltiesApplied ? _self.penaltiesApplied : penaltiesApplied // ignore: cast_nullable_to_non_nullable
as List<String>,evaluativeMatrices: null == evaluativeMatrices ? _self.evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,informationalMatrices: null == informationalMatrices ? _self.informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,matrixVisibleColumns: null == matrixVisibleColumns ? _self.matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}
/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get profileName {
    if (_self.profileName == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.profileName!, (value) {
    return _then(_self.copyWith(profileName: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportDataDTO].
extension ReportDataDTOPatterns on ReportDataDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportDataDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportDataDTO value)  $default,){
final _that = this;
switch (_that) {
case _ReportDataDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportDataDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore,  List<ReportLayoutDTO> layouts, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'local_time_str')  String? localTimeStr, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'scoring_engine_name')  String? scoringEngineName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<MCPToolAuditDTO> mcpToolAudit, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>> groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
return $default(_that.workflowId,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.layouts,_that.createdAt,_that.localTimeStr,_that.orgName,_that.userName,_that.scoringEngineName,_that.strictnessLevel,_that.customPrefaceMd,_that.scoringStrategy,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.hasWarning,_that.contentBlocks,_that.visibleMetadata,_that.groupedExtensions,_that.penaltiesApplied,_that.evaluativeMatrices,_that.informationalMatrices,_that.matrixVisibleColumns);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore,  List<ReportLayoutDTO> layouts, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'local_time_str')  String? localTimeStr, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'scoring_engine_name')  String? scoringEngineName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<MCPToolAuditDTO> mcpToolAudit, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>> groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)  $default,) {final _that = this;
switch (_that) {
case _ReportDataDTO():
return $default(_that.workflowId,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.layouts,_that.createdAt,_that.localTimeStr,_that.orgName,_that.userName,_that.scoringEngineName,_that.strictnessLevel,_that.customPrefaceMd,_that.scoringStrategy,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.hasWarning,_that.contentBlocks,_that.visibleMetadata,_that.groupedExtensions,_that.penaltiesApplied,_that.evaluativeMatrices,_that.informationalMatrices,_that.matrixVisibleColumns);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore,  List<ReportLayoutDTO> layouts, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'local_time_str')  String? localTimeStr, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'user_name')  String? userName, @JsonKey(name: 'scoring_engine_name')  String? scoringEngineName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<MCPToolAuditDTO> mcpToolAudit, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>> groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)?  $default,) {final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
return $default(_that.workflowId,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.layouts,_that.createdAt,_that.localTimeStr,_that.orgName,_that.userName,_that.scoringEngineName,_that.strictnessLevel,_that.customPrefaceMd,_that.scoringStrategy,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.hasWarning,_that.contentBlocks,_that.visibleMetadata,_that.groupedExtensions,_that.penaltiesApplied,_that.evaluativeMatrices,_that.informationalMatrices,_that.matrixVisibleColumns);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportDataDTO extends ReportDataDTO {
  const _ReportDataDTO({@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'profile_id') required this.profileId, @JsonKey(name: 'profile_name') this.profileName, @JsonKey(name: 'available_profiles') final  Map<String, I18nText> availableProfiles = const {}, @JsonKey(name: 'global_score') this.globalScore, final  List<ReportLayoutDTO> layouts = const [], @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'local_time_str') this.localTimeStr, @JsonKey(name: 'org_name') this.orgName, @JsonKey(name: 'user_name') this.userName, @JsonKey(name: 'scoring_engine_name') this.scoringEngineName, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'custom_preface_md') this.customPrefaceMd, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'cost_estimate') this.costEstimate, @JsonKey(name: 'total_tokens') this.totalTokens, @JsonKey(name: 'prompt_tokens') this.promptTokens, @JsonKey(name: 'completion_tokens') this.completionTokens, @JsonKey(name: 'reasoning_tokens') this.reasoningTokens, @JsonKey(name: 'mcp_tool_audit') final  List<MCPToolAuditDTO> mcpToolAudit = const [], @JsonKey(name: 'has_warning') this.hasWarning = false, @JsonKey(name: 'content_blocks') final  List<SduiBlockDTO> contentBlocks = const [], @JsonKey(name: 'visible_metadata') final  List<String> visibleMetadata = const [], @JsonKey(name: 'grouped_extensions') final  Map<String, List<dynamic>> groupedExtensions = const {}, @JsonKey(name: 'penalties_applied') final  List<String> penaltiesApplied = const [], @JsonKey(name: 'evaluative_matrices') final  List<MatrixScorecardRowDto> evaluativeMatrices = const [], @JsonKey(name: 'informational_matrices') final  List<MatrixScorecardRowDto> informationalMatrices = const [], @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const ['label', 'score', 'distribution', 'row_explanation']}): _availableProfiles = availableProfiles,_layouts = layouts,_mcpToolAudit = mcpToolAudit,_contentBlocks = contentBlocks,_visibleMetadata = visibleMetadata,_groupedExtensions = groupedExtensions,_penaltiesApplied = penaltiesApplied,_evaluativeMatrices = evaluativeMatrices,_informationalMatrices = informationalMatrices,_matrixVisibleColumns = matrixVisibleColumns,super._();
  factory _ReportDataDTO.fromJson(Map<String, dynamic> json) => _$ReportDataDTOFromJson(json);

@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'profile_id') final  String profileId;
@override@JsonKey(name: 'profile_name') final  I18nText? profileName;
 final  Map<String, I18nText> _availableProfiles;
@override@JsonKey(name: 'available_profiles') Map<String, I18nText> get availableProfiles {
  if (_availableProfiles is EqualUnmodifiableMapView) return _availableProfiles;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_availableProfiles);
}

@override@JsonKey(name: 'global_score') final  double? globalScore;
 final  List<ReportLayoutDTO> _layouts;
@override@JsonKey() List<ReportLayoutDTO> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}

@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'local_time_str') final  String? localTimeStr;
@override@JsonKey(name: 'org_name') final  String? orgName;
@override@JsonKey(name: 'user_name') final  String? userName;
@override@JsonKey(name: 'scoring_engine_name') final  String? scoringEngineName;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'custom_preface_md') final  String? customPrefaceMd;
@override@JsonKey(name: 'scoring_strategy') final  ScoringStrategy? scoringStrategy;
@override@JsonKey(name: 'cost_estimate') final  double? costEstimate;
@override@JsonKey(name: 'total_tokens') final  int? totalTokens;
@override@JsonKey(name: 'prompt_tokens') final  int? promptTokens;
@override@JsonKey(name: 'completion_tokens') final  int? completionTokens;
@override@JsonKey(name: 'reasoning_tokens') final  int? reasoningTokens;
 final  List<MCPToolAuditDTO> _mcpToolAudit;
@override@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> get mcpToolAudit {
  if (_mcpToolAudit is EqualUnmodifiableListView) return _mcpToolAudit;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mcpToolAudit);
}

@override@JsonKey(name: 'has_warning') final  bool hasWarning;
 final  List<SduiBlockDTO> _contentBlocks;
@override@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks {
  if (_contentBlocks is EqualUnmodifiableListView) return _contentBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_contentBlocks);
}

 final  List<String> _visibleMetadata;
@override@JsonKey(name: 'visible_metadata') List<String> get visibleMetadata {
  if (_visibleMetadata is EqualUnmodifiableListView) return _visibleMetadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleMetadata);
}

 final  Map<String, List<dynamic>> _groupedExtensions;
@override@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> get groupedExtensions {
  if (_groupedExtensions is EqualUnmodifiableMapView) return _groupedExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_groupedExtensions);
}

 final  List<String> _penaltiesApplied;
@override@JsonKey(name: 'penalties_applied') List<String> get penaltiesApplied {
  if (_penaltiesApplied is EqualUnmodifiableListView) return _penaltiesApplied;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_penaltiesApplied);
}

 final  List<MatrixScorecardRowDto> _evaluativeMatrices;
@override@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> get evaluativeMatrices {
  if (_evaluativeMatrices is EqualUnmodifiableListView) return _evaluativeMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_evaluativeMatrices);
}

 final  List<MatrixScorecardRowDto> _informationalMatrices;
@override@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> get informationalMatrices {
  if (_informationalMatrices is EqualUnmodifiableListView) return _informationalMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_informationalMatrices);
}

 final  List<String> _matrixVisibleColumns;
@override@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
}


/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportDataDTOCopyWith<_ReportDataDTO> get copyWith => __$ReportDataDTOCopyWithImpl<_ReportDataDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportDataDTOToJson(this, );
}



@override
String toString() {
  return 'ReportDataDTO(workflowId: $workflowId, profileId: $profileId, profileName: $profileName, availableProfiles: $availableProfiles, globalScore: $globalScore, layouts: $layouts, createdAt: $createdAt, localTimeStr: $localTimeStr, orgName: $orgName, userName: $userName, scoringEngineName: $scoringEngineName, strictnessLevel: $strictnessLevel, customPrefaceMd: $customPrefaceMd, scoringStrategy: $scoringStrategy, costEstimate: $costEstimate, totalTokens: $totalTokens, promptTokens: $promptTokens, completionTokens: $completionTokens, reasoningTokens: $reasoningTokens, mcpToolAudit: $mcpToolAudit, hasWarning: $hasWarning, contentBlocks: $contentBlocks, visibleMetadata: $visibleMetadata, groupedExtensions: $groupedExtensions, penaltiesApplied: $penaltiesApplied, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices, matrixVisibleColumns: $matrixVisibleColumns)';
}


}

/// @nodoc
abstract mixin class _$ReportDataDTOCopyWith<$Res> implements $ReportDataDTOCopyWith<$Res> {
  factory _$ReportDataDTOCopyWith(_ReportDataDTO value, $Res Function(_ReportDataDTO) _then) = __$ReportDataDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'profile_id') String profileId,@JsonKey(name: 'profile_name') I18nText? profileName,@JsonKey(name: 'available_profiles') Map<String, I18nText> availableProfiles,@JsonKey(name: 'global_score') double? globalScore, List<ReportLayoutDTO> layouts,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'local_time_str') String? localTimeStr,@JsonKey(name: 'org_name') String? orgName,@JsonKey(name: 'user_name') String? userName,@JsonKey(name: 'scoring_engine_name') String? scoringEngineName,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'total_tokens') int? totalTokens,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens,@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> mcpToolAudit,@JsonKey(name: 'has_warning') bool hasWarning,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks,@JsonKey(name: 'visible_metadata') List<String> visibleMetadata,@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> groupedExtensions,@JsonKey(name: 'penalties_applied') List<String> penaltiesApplied,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> informationalMatrices,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns
});


@override $I18nTextCopyWith<$Res>? get profileName;

}
/// @nodoc
class __$ReportDataDTOCopyWithImpl<$Res>
    implements _$ReportDataDTOCopyWith<$Res> {
  __$ReportDataDTOCopyWithImpl(this._self, this._then);

  final _ReportDataDTO _self;
  final $Res Function(_ReportDataDTO) _then;

/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? workflowId = null,Object? profileId = null,Object? profileName = freezed,Object? availableProfiles = null,Object? globalScore = freezed,Object? layouts = null,Object? createdAt = freezed,Object? localTimeStr = freezed,Object? orgName = freezed,Object? userName = freezed,Object? scoringEngineName = freezed,Object? strictnessLevel = freezed,Object? customPrefaceMd = freezed,Object? scoringStrategy = freezed,Object? costEstimate = freezed,Object? totalTokens = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? reasoningTokens = freezed,Object? mcpToolAudit = null,Object? hasWarning = null,Object? contentBlocks = null,Object? visibleMetadata = null,Object? groupedExtensions = null,Object? penaltiesApplied = null,Object? evaluativeMatrices = null,Object? informationalMatrices = null,Object? matrixVisibleColumns = null,}) {
  return _then(_ReportDataDTO(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,profileName: freezed == profileName ? _self.profileName : profileName // ignore: cast_nullable_to_non_nullable
as I18nText?,availableProfiles: null == availableProfiles ? _self._availableProfiles : availableProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<ReportLayoutDTO>,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,localTimeStr: freezed == localTimeStr ? _self.localTimeStr : localTimeStr // ignore: cast_nullable_to_non_nullable
as String?,orgName: freezed == orgName ? _self.orgName : orgName // ignore: cast_nullable_to_non_nullable
as String?,userName: freezed == userName ? _self.userName : userName // ignore: cast_nullable_to_non_nullable
as String?,scoringEngineName: freezed == scoringEngineName ? _self.scoringEngineName : scoringEngineName // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,totalTokens: freezed == totalTokens ? _self.totalTokens : totalTokens // ignore: cast_nullable_to_non_nullable
as int?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,mcpToolAudit: null == mcpToolAudit ? _self._mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<MCPToolAuditDTO>,hasWarning: null == hasWarning ? _self.hasWarning : hasWarning // ignore: cast_nullable_to_non_nullable
as bool,contentBlocks: null == contentBlocks ? _self._contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,visibleMetadata: null == visibleMetadata ? _self._visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,groupedExtensions: null == groupedExtensions ? _self._groupedExtensions : groupedExtensions // ignore: cast_nullable_to_non_nullable
as Map<String, List<dynamic>>,penaltiesApplied: null == penaltiesApplied ? _self._penaltiesApplied : penaltiesApplied // ignore: cast_nullable_to_non_nullable
as List<String>,evaluativeMatrices: null == evaluativeMatrices ? _self._evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,informationalMatrices: null == informationalMatrices ? _self._informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get profileName {
    if (_self.profileName == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.profileName!, (value) {
    return _then(_self.copyWith(profileName: value));
  });
}
}

// dart format on
