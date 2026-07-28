// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'sdui_block_dto.dart';

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
                case 'quote_card':
          return SduiQuoteCardBlock.fromJson(
            json
          );
                case 'warning_card':
          return SduiWarningCardBlock.fromJson(
            json
          );
                case 'n_a_card':
          return SduiNACardBlock.fromJson(
            json
          );
                case 'grid':
          return SduiGridBlock.fromJson(
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

 String? get id;
/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBlockDTOCopyWith<SduiBlockDTO> get copyWith => _$SduiBlockDTOCopyWithImpl<SduiBlockDTO>(this as SduiBlockDTO, _$identity);

  /// Serializes this SduiBlockDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiBlockDTO&&(identical(other.id, id) || other.id == id));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id);

@override
String toString() {
  return 'SduiBlockDTO(id: $id)';
}


}

/// @nodoc
abstract mixin class $SduiBlockDTOCopyWith<$Res>  {
  factory $SduiBlockDTOCopyWith(SduiBlockDTO value, $Res Function(SduiBlockDTO) _then) = _$SduiBlockDTOCopyWithImpl;
@useResult
$Res call({
 String? id
});




}
/// @nodoc
class _$SduiBlockDTOCopyWithImpl<$Res>
    implements $SduiBlockDTOCopyWith<$Res> {
  _$SduiBlockDTOCopyWithImpl(this._self, this._then);

  final SduiBlockDTO _self;
  final $Res Function(SduiBlockDTO) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,}) {
  return _then(_self.copyWith(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>({TResult Function( SduiParagraphBlock value)?  paragraph,TResult Function( SduiBulletListBlock value)?  bulletList,TResult Function( SduiAlertBoxBlock value)?  alertBox,TResult Function( SduiHeroInsightBlock value)?  heroInsight,TResult Function( SduiMarkdownBlock value)?  markdown,TResult Function( SduiQuoteCardBlock value)?  quoteCard,TResult Function( SduiWarningCardBlock value)?  warningCard,TResult Function( SduiNACardBlock value)?  nACard,TResult Function( SduiGridBlock value)?  grid,required TResult orElse(),}){
final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that);case SduiMarkdownBlock() when markdown != null:
return markdown(_that);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that);case SduiNACardBlock() when nACard != null:
return nACard(_that);case SduiGridBlock() when grid != null:
return grid(_that);case _:
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

@optionalTypeArgs TResult map<TResult extends Object?>({required TResult Function( SduiParagraphBlock value)  paragraph,required TResult Function( SduiBulletListBlock value)  bulletList,required TResult Function( SduiAlertBoxBlock value)  alertBox,required TResult Function( SduiHeroInsightBlock value)  heroInsight,required TResult Function( SduiMarkdownBlock value)  markdown,required TResult Function( SduiQuoteCardBlock value)  quoteCard,required TResult Function( SduiWarningCardBlock value)  warningCard,required TResult Function( SduiNACardBlock value)  nACard,required TResult Function( SduiGridBlock value)  grid,}){
final _that = this;
switch (_that) {
case SduiParagraphBlock():
return paragraph(_that);case SduiBulletListBlock():
return bulletList(_that);case SduiAlertBoxBlock():
return alertBox(_that);case SduiHeroInsightBlock():
return heroInsight(_that);case SduiMarkdownBlock():
return markdown(_that);case SduiQuoteCardBlock():
return quoteCard(_that);case SduiWarningCardBlock():
return warningCard(_that);case SduiNACardBlock():
return nACard(_that);case SduiGridBlock():
return grid(_that);}
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>({TResult? Function( SduiParagraphBlock value)?  paragraph,TResult? Function( SduiBulletListBlock value)?  bulletList,TResult? Function( SduiAlertBoxBlock value)?  alertBox,TResult? Function( SduiHeroInsightBlock value)?  heroInsight,TResult? Function( SduiMarkdownBlock value)?  markdown,TResult? Function( SduiQuoteCardBlock value)?  quoteCard,TResult? Function( SduiWarningCardBlock value)?  warningCard,TResult? Function( SduiNACardBlock value)?  nACard,TResult? Function( SduiGridBlock value)?  grid,}){
final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that);case SduiMarkdownBlock() when markdown != null:
return markdown(_that);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that);case SduiNACardBlock() when nACard != null:
return nACard(_that);case SduiGridBlock() when grid != null:
return grid(_that);case _:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>({TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  paragraph,TResult Function( String? id,  List<SduiBulletListItemDTO> items)?  bulletList,TResult Function( String? id,  String text,  String severity,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  alertBox,TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  heroInsight,TResult Function( String? id,  String text)?  markdown,TResult Function( String? id,  String quote, @JsonKey(name: 'source_aliases')  List<String> sourceAliases,  List<dynamic> citations)?  quoteCard,TResult Function( String? id,  String message, @JsonKey(name: 'quote_text')  String? quoteText)?  warningCard,TResult Function( String? id, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds,  String message)?  nACard,TResult Function( String? id,  List<dynamic> items)?  grid,required TResult orElse(),}) {final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that.id,_that.items);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that.id,_that.text,_that.severity,_that.citations,_that.exactQuotes);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiMarkdownBlock() when markdown != null:
return markdown(_that.id,_that.text);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that.id,_that.quote,_that.sourceAliases,_that.citations);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that.id,_that.message,_that.quoteText);case SduiNACardBlock() when nACard != null:
return nACard(_that.id,_that.shortCircuitReasonTdaIds,_that.message);case SduiGridBlock() when grid != null:
return grid(_that.id,_that.items);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>({required TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  paragraph,required TResult Function( String? id,  List<SduiBulletListItemDTO> items)  bulletList,required TResult Function( String? id,  String text,  String severity,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  alertBox,required TResult Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  heroInsight,required TResult Function( String? id,  String text)  markdown,required TResult Function( String? id,  String quote, @JsonKey(name: 'source_aliases')  List<String> sourceAliases,  List<dynamic> citations)  quoteCard,required TResult Function( String? id,  String message, @JsonKey(name: 'quote_text')  String? quoteText)  warningCard,required TResult Function( String? id, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds,  String message)  nACard,required TResult Function( String? id,  List<dynamic> items)  grid,}) {final _that = this;
switch (_that) {
case SduiParagraphBlock():
return paragraph(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiBulletListBlock():
return bulletList(_that.id,_that.items);case SduiAlertBoxBlock():
return alertBox(_that.id,_that.text,_that.severity,_that.citations,_that.exactQuotes);case SduiHeroInsightBlock():
return heroInsight(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiMarkdownBlock():
return markdown(_that.id,_that.text);case SduiQuoteCardBlock():
return quoteCard(_that.id,_that.quote,_that.sourceAliases,_that.citations);case SduiWarningCardBlock():
return warningCard(_that.id,_that.message,_that.quoteText);case SduiNACardBlock():
return nACard(_that.id,_that.shortCircuitReasonTdaIds,_that.message);case SduiGridBlock():
return grid(_that.id,_that.items);}
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>({TResult? Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  paragraph,TResult? Function( String? id,  List<SduiBulletListItemDTO> items)?  bulletList,TResult? Function( String? id,  String text,  String severity,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  alertBox,TResult? Function( String? id,  String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  heroInsight,TResult? Function( String? id,  String text)?  markdown,TResult? Function( String? id,  String quote, @JsonKey(name: 'source_aliases')  List<String> sourceAliases,  List<dynamic> citations)?  quoteCard,TResult? Function( String? id,  String message, @JsonKey(name: 'quote_text')  String? quoteText)?  warningCard,TResult? Function( String? id, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds,  String message)?  nACard,TResult? Function( String? id,  List<dynamic> items)?  grid,}) {final _that = this;
switch (_that) {
case SduiParagraphBlock() when paragraph != null:
return paragraph(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiBulletListBlock() when bulletList != null:
return bulletList(_that.id,_that.items);case SduiAlertBoxBlock() when alertBox != null:
return alertBox(_that.id,_that.text,_that.severity,_that.citations,_that.exactQuotes);case SduiHeroInsightBlock() when heroInsight != null:
return heroInsight(_that.id,_that.text,_that.citations,_that.exactQuotes);case SduiMarkdownBlock() when markdown != null:
return markdown(_that.id,_that.text);case SduiQuoteCardBlock() when quoteCard != null:
return quoteCard(_that.id,_that.quote,_that.sourceAliases,_that.citations);case SduiWarningCardBlock() when warningCard != null:
return warningCard(_that.id,_that.message,_that.quoteText);case SduiNACardBlock() when nACard != null:
return nACard(_that.id,_that.shortCircuitReasonTdaIds,_that.message);case SduiGridBlock() when grid != null:
return grid(_that.id,_that.items);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiParagraphBlock extends SduiBlockDTO {
  const SduiParagraphBlock({this.id, required this.text, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const [], final  String? $type}): _citations = citations,_exactQuotes = exactQuotes,$type = $type ?? 'paragraph',super._();
  factory SduiParagraphBlock.fromJson(Map<String, dynamic> json) => _$SduiParagraphBlockFromJson(json);

@override final  String? id;
 final  String text;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiParagraphBlockCopyWith<SduiParagraphBlock> get copyWith => _$SduiParagraphBlockCopyWithImpl<SduiParagraphBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiParagraphBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiParagraphBlock&&(identical(other.id, id) || other.id == id)&&(identical(other.text, text) || other.text == text)&&const DeepCollectionEquality().equals(other._citations, _citations)&&const DeepCollectionEquality().equals(other._exactQuotes, _exactQuotes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,text,const DeepCollectionEquality().hash(_citations),const DeepCollectionEquality().hash(_exactQuotes));

@override
String toString() {
  return 'SduiBlockDTO.paragraph(id: $id, text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiParagraphBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiParagraphBlockCopyWith(SduiParagraphBlock value, $Res Function(SduiParagraphBlock) _then) = _$SduiParagraphBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(SduiParagraphBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiBulletListBlock extends SduiBlockDTO {
  const SduiBulletListBlock({this.id, required final  List<SduiBulletListItemDTO> items, final  String? $type}): _items = items,$type = $type ?? 'bullet_list',super._();
  factory SduiBulletListBlock.fromJson(Map<String, dynamic> json) => _$SduiBulletListBlockFromJson(json);

@override final  String? id;
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
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBulletListBlockCopyWith<SduiBulletListBlock> get copyWith => _$SduiBulletListBlockCopyWithImpl<SduiBulletListBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiBulletListBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiBulletListBlock&&(identical(other.id, id) || other.id == id)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'SduiBlockDTO.bulletList(id: $id, items: $items)';
}


}

/// @nodoc
abstract mixin class $SduiBulletListBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiBulletListBlockCopyWith(SduiBulletListBlock value, $Res Function(SduiBulletListBlock) _then) = _$SduiBulletListBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, List<SduiBulletListItemDTO> items
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? items = null,}) {
  return _then(SduiBulletListBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<SduiBulletListItemDTO>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiAlertBoxBlock extends SduiBlockDTO {
  const SduiAlertBoxBlock({this.id, required this.text, required this.severity, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const [], final  String? $type}): _citations = citations,_exactQuotes = exactQuotes,$type = $type ?? 'alert_box',super._();
  factory SduiAlertBoxBlock.fromJson(Map<String, dynamic> json) => _$SduiAlertBoxBlockFromJson(json);

@override final  String? id;
 final  String text;
 final  String severity;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiAlertBoxBlockCopyWith<SduiAlertBoxBlock> get copyWith => _$SduiAlertBoxBlockCopyWithImpl<SduiAlertBoxBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiAlertBoxBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiAlertBoxBlock&&(identical(other.id, id) || other.id == id)&&(identical(other.text, text) || other.text == text)&&(identical(other.severity, severity) || other.severity == severity)&&const DeepCollectionEquality().equals(other._citations, _citations)&&const DeepCollectionEquality().equals(other._exactQuotes, _exactQuotes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,text,severity,const DeepCollectionEquality().hash(_citations),const DeepCollectionEquality().hash(_exactQuotes));

@override
String toString() {
  return 'SduiBlockDTO.alertBox(id: $id, text: $text, severity: $severity, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiAlertBoxBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiAlertBoxBlockCopyWith(SduiAlertBoxBlock value, $Res Function(SduiAlertBoxBlock) _then) = _$SduiAlertBoxBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text, String severity, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,Object? severity = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(SduiAlertBoxBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,severity: null == severity ? _self.severity : severity // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiHeroInsightBlock extends SduiBlockDTO {
  const SduiHeroInsightBlock({this.id, required this.text, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const [], final  String? $type}): _citations = citations,_exactQuotes = exactQuotes,$type = $type ?? 'hero_insight',super._();
  factory SduiHeroInsightBlock.fromJson(Map<String, dynamic> json) => _$SduiHeroInsightBlockFromJson(json);

@override final  String? id;
 final  String text;
 final  List<int> _citations;
@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiHeroInsightBlockCopyWith<SduiHeroInsightBlock> get copyWith => _$SduiHeroInsightBlockCopyWithImpl<SduiHeroInsightBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiHeroInsightBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiHeroInsightBlock&&(identical(other.id, id) || other.id == id)&&(identical(other.text, text) || other.text == text)&&const DeepCollectionEquality().equals(other._citations, _citations)&&const DeepCollectionEquality().equals(other._exactQuotes, _exactQuotes));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,text,const DeepCollectionEquality().hash(_citations),const DeepCollectionEquality().hash(_exactQuotes));

@override
String toString() {
  return 'SduiBlockDTO.heroInsight(id: $id, text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiHeroInsightBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiHeroInsightBlockCopyWith(SduiHeroInsightBlock value, $Res Function(SduiHeroInsightBlock) _then) = _$SduiHeroInsightBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(SduiHeroInsightBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiMarkdownBlock extends SduiBlockDTO {
  const SduiMarkdownBlock({this.id, required this.text, final  String? $type}): $type = $type ?? 'markdown',super._();
  factory SduiMarkdownBlock.fromJson(Map<String, dynamic> json) => _$SduiMarkdownBlockFromJson(json);

@override final  String? id;
 final  String text;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiMarkdownBlockCopyWith<SduiMarkdownBlock> get copyWith => _$SduiMarkdownBlockCopyWithImpl<SduiMarkdownBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiMarkdownBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiMarkdownBlock&&(identical(other.id, id) || other.id == id)&&(identical(other.text, text) || other.text == text));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,text);

@override
String toString() {
  return 'SduiBlockDTO.markdown(id: $id, text: $text)';
}


}

/// @nodoc
abstract mixin class $SduiMarkdownBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiMarkdownBlockCopyWith(SduiMarkdownBlock value, $Res Function(SduiMarkdownBlock) _then) = _$SduiMarkdownBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String text
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? text = null,}) {
  return _then(SduiMarkdownBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiQuoteCardBlock extends SduiBlockDTO {
  const SduiQuoteCardBlock({this.id, required this.quote, @JsonKey(name: 'source_aliases') required final  List<String> sourceAliases, required final  List<dynamic> citations, final  String? $type}): _sourceAliases = sourceAliases,_citations = citations,$type = $type ?? 'quote_card',super._();
  factory SduiQuoteCardBlock.fromJson(Map<String, dynamic> json) => _$SduiQuoteCardBlockFromJson(json);

@override final  String? id;
 final  String quote;
 final  List<String> _sourceAliases;
@JsonKey(name: 'source_aliases') List<String> get sourceAliases {
  if (_sourceAliases is EqualUnmodifiableListView) return _sourceAliases;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sourceAliases);
}

 final  List<dynamic> _citations;
 List<dynamic> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiQuoteCardBlockCopyWith<SduiQuoteCardBlock> get copyWith => _$SduiQuoteCardBlockCopyWithImpl<SduiQuoteCardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiQuoteCardBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiQuoteCardBlock&&(identical(other.id, id) || other.id == id)&&(identical(other.quote, quote) || other.quote == quote)&&const DeepCollectionEquality().equals(other._sourceAliases, _sourceAliases)&&const DeepCollectionEquality().equals(other._citations, _citations));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,quote,const DeepCollectionEquality().hash(_sourceAliases),const DeepCollectionEquality().hash(_citations));

@override
String toString() {
  return 'SduiBlockDTO.quoteCard(id: $id, quote: $quote, sourceAliases: $sourceAliases, citations: $citations)';
}


}

/// @nodoc
abstract mixin class $SduiQuoteCardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiQuoteCardBlockCopyWith(SduiQuoteCardBlock value, $Res Function(SduiQuoteCardBlock) _then) = _$SduiQuoteCardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String quote,@JsonKey(name: 'source_aliases') List<String> sourceAliases, List<dynamic> citations
});




}
/// @nodoc
class _$SduiQuoteCardBlockCopyWithImpl<$Res>
    implements $SduiQuoteCardBlockCopyWith<$Res> {
  _$SduiQuoteCardBlockCopyWithImpl(this._self, this._then);

  final SduiQuoteCardBlock _self;
  final $Res Function(SduiQuoteCardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? quote = null,Object? sourceAliases = null,Object? citations = null,}) {
  return _then(SduiQuoteCardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,quote: null == quote ? _self.quote : quote // ignore: cast_nullable_to_non_nullable
as String,sourceAliases: null == sourceAliases ? _self._sourceAliases : sourceAliases // ignore: cast_nullable_to_non_nullable
as List<String>,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<dynamic>,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiWarningCardBlock extends SduiBlockDTO {
  const SduiWarningCardBlock({this.id, required this.message, @JsonKey(name: 'quote_text') this.quoteText, final  String? $type}): $type = $type ?? 'warning_card',super._();
  factory SduiWarningCardBlock.fromJson(Map<String, dynamic> json) => _$SduiWarningCardBlockFromJson(json);

@override final  String? id;
 final  String message;
@JsonKey(name: 'quote_text') final  String? quoteText;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiWarningCardBlockCopyWith<SduiWarningCardBlock> get copyWith => _$SduiWarningCardBlockCopyWithImpl<SduiWarningCardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiWarningCardBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiWarningCardBlock&&(identical(other.id, id) || other.id == id)&&(identical(other.message, message) || other.message == message)&&(identical(other.quoteText, quoteText) || other.quoteText == quoteText));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,message,quoteText);

@override
String toString() {
  return 'SduiBlockDTO.warningCard(id: $id, message: $message, quoteText: $quoteText)';
}


}

/// @nodoc
abstract mixin class $SduiWarningCardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiWarningCardBlockCopyWith(SduiWarningCardBlock value, $Res Function(SduiWarningCardBlock) _then) = _$SduiWarningCardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, String message,@JsonKey(name: 'quote_text') String? quoteText
});




}
/// @nodoc
class _$SduiWarningCardBlockCopyWithImpl<$Res>
    implements $SduiWarningCardBlockCopyWith<$Res> {
  _$SduiWarningCardBlockCopyWithImpl(this._self, this._then);

  final SduiWarningCardBlock _self;
  final $Res Function(SduiWarningCardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? message = null,Object? quoteText = freezed,}) {
  return _then(SduiWarningCardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,quoteText: freezed == quoteText ? _self.quoteText : quoteText // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiNACardBlock extends SduiBlockDTO {
  const SduiNACardBlock({this.id, @JsonKey(name: 'short_circuit_reason_tda_ids') required final  List<String> shortCircuitReasonTdaIds, required this.message, final  String? $type}): _shortCircuitReasonTdaIds = shortCircuitReasonTdaIds,$type = $type ?? 'n_a_card',super._();
  factory SduiNACardBlock.fromJson(Map<String, dynamic> json) => _$SduiNACardBlockFromJson(json);

@override final  String? id;
 final  List<String> _shortCircuitReasonTdaIds;
@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> get shortCircuitReasonTdaIds {
  if (_shortCircuitReasonTdaIds is EqualUnmodifiableListView) return _shortCircuitReasonTdaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortCircuitReasonTdaIds);
}

 final  String message;

@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiNACardBlockCopyWith<SduiNACardBlock> get copyWith => _$SduiNACardBlockCopyWithImpl<SduiNACardBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiNACardBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiNACardBlock&&(identical(other.id, id) || other.id == id)&&const DeepCollectionEquality().equals(other._shortCircuitReasonTdaIds, _shortCircuitReasonTdaIds)&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,const DeepCollectionEquality().hash(_shortCircuitReasonTdaIds),message);

@override
String toString() {
  return 'SduiBlockDTO.nACard(id: $id, shortCircuitReasonTdaIds: $shortCircuitReasonTdaIds, message: $message)';
}


}

/// @nodoc
abstract mixin class $SduiNACardBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiNACardBlockCopyWith(SduiNACardBlock value, $Res Function(SduiNACardBlock) _then) = _$SduiNACardBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> shortCircuitReasonTdaIds, String message
});




}
/// @nodoc
class _$SduiNACardBlockCopyWithImpl<$Res>
    implements $SduiNACardBlockCopyWith<$Res> {
  _$SduiNACardBlockCopyWithImpl(this._self, this._then);

  final SduiNACardBlock _self;
  final $Res Function(SduiNACardBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? shortCircuitReasonTdaIds = null,Object? message = null,}) {
  return _then(SduiNACardBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,shortCircuitReasonTdaIds: null == shortCircuitReasonTdaIds ? _self._shortCircuitReasonTdaIds : shortCircuitReasonTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class SduiGridBlock extends SduiBlockDTO {
  const SduiGridBlock({this.id, required final  List<dynamic> items, final  String? $type}): _items = items,$type = $type ?? 'grid',super._();
  factory SduiGridBlock.fromJson(Map<String, dynamic> json) => _$SduiGridBlockFromJson(json);

@override final  String? id;
 final  List<dynamic> _items;
 List<dynamic> get items {
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_items);
}


@JsonKey(name: 'block_type')
final String $type;


/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiGridBlockCopyWith<SduiGridBlock> get copyWith => _$SduiGridBlockCopyWithImpl<SduiGridBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SduiGridBlockToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SduiGridBlock&&(identical(other.id, id) || other.id == id)&&const DeepCollectionEquality().equals(other._items, _items));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,const DeepCollectionEquality().hash(_items));

@override
String toString() {
  return 'SduiBlockDTO.grid(id: $id, items: $items)';
}


}

/// @nodoc
abstract mixin class $SduiGridBlockCopyWith<$Res> implements $SduiBlockDTOCopyWith<$Res> {
  factory $SduiGridBlockCopyWith(SduiGridBlock value, $Res Function(SduiGridBlock) _then) = _$SduiGridBlockCopyWithImpl;
@override @useResult
$Res call({
 String? id, List<dynamic> items
});




}
/// @nodoc
class _$SduiGridBlockCopyWithImpl<$Res>
    implements $SduiGridBlockCopyWith<$Res> {
  _$SduiGridBlockCopyWithImpl(this._self, this._then);

  final SduiGridBlock _self;
  final $Res Function(SduiGridBlock) _then;

/// Create a copy of SduiBlockDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? items = null,}) {
  return _then(SduiGridBlock(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,items: null == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<dynamic>,
  ));
}


}


/// @nodoc
mixin _$SduiBulletListItemDTO {

 String get text; List<int> get citations;@JsonKey(name: 'exact_quotes') List<String> get exactQuotes;
/// Create a copy of SduiBulletListItemDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SduiBulletListItemDTOCopyWith<SduiBulletListItemDTO> get copyWith => _$SduiBulletListItemDTOCopyWithImpl<SduiBulletListItemDTO>(this as SduiBulletListItemDTO, _$identity);

  /// Serializes this SduiBulletListItemDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SduiBulletListItemDTO(text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class $SduiBulletListItemDTOCopyWith<$Res>  {
  factory $SduiBulletListItemDTOCopyWith(SduiBulletListItemDTO value, $Res Function(SduiBulletListItemDTO) _then) = _$SduiBulletListItemDTOCopyWithImpl;
@useResult
$Res call({
 String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
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
@pragma('vm:prefer-inline') @override $Res call({Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(_self.copyWith(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self.citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self.exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
return $default(_that.text,_that.citations,_that.exactQuotes);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)  $default,) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO():
return $default(_that.text,_that.citations,_that.exactQuotes);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String text,  List<int> citations, @JsonKey(name: 'exact_quotes')  List<String> exactQuotes)?  $default,) {final _that = this;
switch (_that) {
case _SduiBulletListItemDTO() when $default != null:
return $default(_that.text,_that.citations,_that.exactQuotes);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _SduiBulletListItemDTO implements SduiBulletListItemDTO {
  const _SduiBulletListItemDTO({required this.text, final  List<int> citations = const [], @JsonKey(name: 'exact_quotes') final  List<String> exactQuotes = const []}): _citations = citations,_exactQuotes = exactQuotes;
  factory _SduiBulletListItemDTO.fromJson(Map<String, dynamic> json) => _$SduiBulletListItemDTOFromJson(json);

@override final  String text;
 final  List<int> _citations;
@override@JsonKey() List<int> get citations {
  if (_citations is EqualUnmodifiableListView) return _citations;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_citations);
}

 final  List<String> _exactQuotes;
@override@JsonKey(name: 'exact_quotes') List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
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
  return 'SduiBulletListItemDTO(text: $text, citations: $citations, exactQuotes: $exactQuotes)';
}


}

/// @nodoc
abstract mixin class _$SduiBulletListItemDTOCopyWith<$Res> implements $SduiBulletListItemDTOCopyWith<$Res> {
  factory _$SduiBulletListItemDTOCopyWith(_SduiBulletListItemDTO value, $Res Function(_SduiBulletListItemDTO) _then) = __$SduiBulletListItemDTOCopyWithImpl;
@override @useResult
$Res call({
 String text, List<int> citations,@JsonKey(name: 'exact_quotes') List<String> exactQuotes
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
@override @pragma('vm:prefer-inline') $Res call({Object? text = null,Object? citations = null,Object? exactQuotes = null,}) {
  return _then(_SduiBulletListItemDTO(
text: null == text ? _self.text : text // ignore: cast_nullable_to_non_nullable
as String,citations: null == citations ? _self._citations : citations // ignore: cast_nullable_to_non_nullable
as List<int>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
