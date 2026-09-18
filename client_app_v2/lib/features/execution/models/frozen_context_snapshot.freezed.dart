// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'frozen_context_snapshot.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$FrozenContextSnapshot {

@JsonKey(name: 'version_id') String? get versionId;@JsonKey(name: 'workflow_id') String? get workflowId;@JsonKey(name: 'workflow_name') String? get workflowName;@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'user_id') String? get userId;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'compiled_prompts') Map<String, String> get compiledPrompts;@JsonKey(name: 'injected_theory') Map<String, dynamic> get injectedTheory;@JsonKey(name: 'generated_schemas') Map<String, dynamic> get generatedSchemas;@JsonKey(name: 'ui_hints_snapshot') Map<String, dynamic> get uiHintsSnapshot;@JsonKey(name: 'mcp_tool_audit') List<Map<String, dynamic>> get mcpToolAudit;
/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FrozenContextSnapshotCopyWith<FrozenContextSnapshot> get copyWith => _$FrozenContextSnapshotCopyWithImpl<FrozenContextSnapshot>(this as FrozenContextSnapshot, _$identity);

  /// Serializes this FrozenContextSnapshot to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'FrozenContextSnapshot(versionId: $versionId, workflowId: $workflowId, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, createdAt: $createdAt, compiledPrompts: $compiledPrompts, injectedTheory: $injectedTheory, generatedSchemas: $generatedSchemas, uiHintsSnapshot: $uiHintsSnapshot, mcpToolAudit: $mcpToolAudit)';
}


}

/// @nodoc
abstract mixin class $FrozenContextSnapshotCopyWith<$Res>  {
  factory $FrozenContextSnapshotCopyWith(FrozenContextSnapshot value, $Res Function(FrozenContextSnapshot) _then) = _$FrozenContextSnapshotCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'version_id') String? versionId,@JsonKey(name: 'workflow_id') String? workflowId,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'compiled_prompts') Map<String, String> compiledPrompts,@JsonKey(name: 'injected_theory') Map<String, dynamic> injectedTheory,@JsonKey(name: 'generated_schemas') Map<String, dynamic> generatedSchemas,@JsonKey(name: 'ui_hints_snapshot') Map<String, dynamic> uiHintsSnapshot,@JsonKey(name: 'mcp_tool_audit') List<Map<String, dynamic>> mcpToolAudit
});




}
/// @nodoc
class _$FrozenContextSnapshotCopyWithImpl<$Res>
    implements $FrozenContextSnapshotCopyWith<$Res> {
  _$FrozenContextSnapshotCopyWithImpl(this._self, this._then);

  final FrozenContextSnapshot _self;
  final $Res Function(FrozenContextSnapshot) _then;

/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? versionId = freezed,Object? workflowId = freezed,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? createdAt = freezed,Object? compiledPrompts = null,Object? injectedTheory = null,Object? generatedSchemas = null,Object? uiHintsSnapshot = null,Object? mcpToolAudit = null,}) {
  return _then(_self.copyWith(
versionId: freezed == versionId ? _self.versionId : versionId // ignore: cast_nullable_to_non_nullable
as String?,workflowId: freezed == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String?,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,compiledPrompts: null == compiledPrompts ? _self.compiledPrompts : compiledPrompts // ignore: cast_nullable_to_non_nullable
as Map<String, String>,injectedTheory: null == injectedTheory ? _self.injectedTheory : injectedTheory // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,generatedSchemas: null == generatedSchemas ? _self.generatedSchemas : generatedSchemas // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,uiHintsSnapshot: null == uiHintsSnapshot ? _self.uiHintsSnapshot : uiHintsSnapshot // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,mcpToolAudit: null == mcpToolAudit ? _self.mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>,
  ));
}

}


/// Adds pattern-matching-related methods to [FrozenContextSnapshot].
extension FrozenContextSnapshotPatterns on FrozenContextSnapshot {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FrozenContextSnapshot value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FrozenContextSnapshot value)  $default,){
final _that = this;
switch (_that) {
case _FrozenContextSnapshot():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FrozenContextSnapshot value)?  $default,){
final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'version_id')  String? versionId, @JsonKey(name: 'workflow_id')  String? workflowId, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'compiled_prompts')  Map<String, String> compiledPrompts, @JsonKey(name: 'injected_theory')  Map<String, dynamic> injectedTheory, @JsonKey(name: 'generated_schemas')  Map<String, dynamic> generatedSchemas, @JsonKey(name: 'ui_hints_snapshot')  Map<String, dynamic> uiHintsSnapshot, @JsonKey(name: 'mcp_tool_audit')  List<Map<String, dynamic>> mcpToolAudit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
return $default(_that.versionId,_that.workflowId,_that.workflowName,_that.organizationId,_that.userId,_that.createdAt,_that.compiledPrompts,_that.injectedTheory,_that.generatedSchemas,_that.uiHintsSnapshot,_that.mcpToolAudit);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'version_id')  String? versionId, @JsonKey(name: 'workflow_id')  String? workflowId, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'compiled_prompts')  Map<String, String> compiledPrompts, @JsonKey(name: 'injected_theory')  Map<String, dynamic> injectedTheory, @JsonKey(name: 'generated_schemas')  Map<String, dynamic> generatedSchemas, @JsonKey(name: 'ui_hints_snapshot')  Map<String, dynamic> uiHintsSnapshot, @JsonKey(name: 'mcp_tool_audit')  List<Map<String, dynamic>> mcpToolAudit)  $default,) {final _that = this;
switch (_that) {
case _FrozenContextSnapshot():
return $default(_that.versionId,_that.workflowId,_that.workflowName,_that.organizationId,_that.userId,_that.createdAt,_that.compiledPrompts,_that.injectedTheory,_that.generatedSchemas,_that.uiHintsSnapshot,_that.mcpToolAudit);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'version_id')  String? versionId, @JsonKey(name: 'workflow_id')  String? workflowId, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'compiled_prompts')  Map<String, String> compiledPrompts, @JsonKey(name: 'injected_theory')  Map<String, dynamic> injectedTheory, @JsonKey(name: 'generated_schemas')  Map<String, dynamic> generatedSchemas, @JsonKey(name: 'ui_hints_snapshot')  Map<String, dynamic> uiHintsSnapshot, @JsonKey(name: 'mcp_tool_audit')  List<Map<String, dynamic>> mcpToolAudit)?  $default,) {final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
return $default(_that.versionId,_that.workflowId,_that.workflowName,_that.organizationId,_that.userId,_that.createdAt,_that.compiledPrompts,_that.injectedTheory,_that.generatedSchemas,_that.uiHintsSnapshot,_that.mcpToolAudit);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _FrozenContextSnapshot extends FrozenContextSnapshot {
  const _FrozenContextSnapshot({@JsonKey(name: 'version_id') this.versionId, @JsonKey(name: 'workflow_id') this.workflowId, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'compiled_prompts') final  Map<String, String> compiledPrompts = const {}, @JsonKey(name: 'injected_theory') final  Map<String, dynamic> injectedTheory = const {}, @JsonKey(name: 'generated_schemas') final  Map<String, dynamic> generatedSchemas = const {}, @JsonKey(name: 'ui_hints_snapshot') final  Map<String, dynamic> uiHintsSnapshot = const {}, @JsonKey(name: 'mcp_tool_audit') final  List<Map<String, dynamic>> mcpToolAudit = const []}): _compiledPrompts = compiledPrompts,_injectedTheory = injectedTheory,_generatedSchemas = generatedSchemas,_uiHintsSnapshot = uiHintsSnapshot,_mcpToolAudit = mcpToolAudit,super._();
  factory _FrozenContextSnapshot.fromJson(Map<String, dynamic> json) => _$FrozenContextSnapshotFromJson(json);

@override@JsonKey(name: 'version_id') final  String? versionId;
@override@JsonKey(name: 'workflow_id') final  String? workflowId;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
@override@JsonKey(name: 'organization_id') final  String? organizationId;
@override@JsonKey(name: 'user_id') final  String? userId;
@override@JsonKey(name: 'created_at') final  String? createdAt;
 final  Map<String, String> _compiledPrompts;
@override@JsonKey(name: 'compiled_prompts') Map<String, String> get compiledPrompts {
  if (_compiledPrompts is EqualUnmodifiableMapView) return _compiledPrompts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_compiledPrompts);
}

 final  Map<String, dynamic> _injectedTheory;
@override@JsonKey(name: 'injected_theory') Map<String, dynamic> get injectedTheory {
  if (_injectedTheory is EqualUnmodifiableMapView) return _injectedTheory;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_injectedTheory);
}

 final  Map<String, dynamic> _generatedSchemas;
@override@JsonKey(name: 'generated_schemas') Map<String, dynamic> get generatedSchemas {
  if (_generatedSchemas is EqualUnmodifiableMapView) return _generatedSchemas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_generatedSchemas);
}

 final  Map<String, dynamic> _uiHintsSnapshot;
@override@JsonKey(name: 'ui_hints_snapshot') Map<String, dynamic> get uiHintsSnapshot {
  if (_uiHintsSnapshot is EqualUnmodifiableMapView) return _uiHintsSnapshot;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_uiHintsSnapshot);
}

 final  List<Map<String, dynamic>> _mcpToolAudit;
@override@JsonKey(name: 'mcp_tool_audit') List<Map<String, dynamic>> get mcpToolAudit {
  if (_mcpToolAudit is EqualUnmodifiableListView) return _mcpToolAudit;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mcpToolAudit);
}


/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FrozenContextSnapshotCopyWith<_FrozenContextSnapshot> get copyWith => __$FrozenContextSnapshotCopyWithImpl<_FrozenContextSnapshot>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FrozenContextSnapshotToJson(this, );
}



@override
String toString() {
  return 'FrozenContextSnapshot(versionId: $versionId, workflowId: $workflowId, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, createdAt: $createdAt, compiledPrompts: $compiledPrompts, injectedTheory: $injectedTheory, generatedSchemas: $generatedSchemas, uiHintsSnapshot: $uiHintsSnapshot, mcpToolAudit: $mcpToolAudit)';
}


}

/// @nodoc
abstract mixin class _$FrozenContextSnapshotCopyWith<$Res> implements $FrozenContextSnapshotCopyWith<$Res> {
  factory _$FrozenContextSnapshotCopyWith(_FrozenContextSnapshot value, $Res Function(_FrozenContextSnapshot) _then) = __$FrozenContextSnapshotCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'version_id') String? versionId,@JsonKey(name: 'workflow_id') String? workflowId,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'compiled_prompts') Map<String, String> compiledPrompts,@JsonKey(name: 'injected_theory') Map<String, dynamic> injectedTheory,@JsonKey(name: 'generated_schemas') Map<String, dynamic> generatedSchemas,@JsonKey(name: 'ui_hints_snapshot') Map<String, dynamic> uiHintsSnapshot,@JsonKey(name: 'mcp_tool_audit') List<Map<String, dynamic>> mcpToolAudit
});




}
/// @nodoc
class __$FrozenContextSnapshotCopyWithImpl<$Res>
    implements _$FrozenContextSnapshotCopyWith<$Res> {
  __$FrozenContextSnapshotCopyWithImpl(this._self, this._then);

  final _FrozenContextSnapshot _self;
  final $Res Function(_FrozenContextSnapshot) _then;

/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? versionId = freezed,Object? workflowId = freezed,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? createdAt = freezed,Object? compiledPrompts = null,Object? injectedTheory = null,Object? generatedSchemas = null,Object? uiHintsSnapshot = null,Object? mcpToolAudit = null,}) {
  return _then(_FrozenContextSnapshot(
versionId: freezed == versionId ? _self.versionId : versionId // ignore: cast_nullable_to_non_nullable
as String?,workflowId: freezed == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String?,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,compiledPrompts: null == compiledPrompts ? _self._compiledPrompts : compiledPrompts // ignore: cast_nullable_to_non_nullable
as Map<String, String>,injectedTheory: null == injectedTheory ? _self._injectedTheory : injectedTheory // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,generatedSchemas: null == generatedSchemas ? _self._generatedSchemas : generatedSchemas // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,uiHintsSnapshot: null == uiHintsSnapshot ? _self._uiHintsSnapshot : uiHintsSnapshot // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,mcpToolAudit: null == mcpToolAudit ? _self._mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<Map<String, dynamic>>,
  ));
}


}

// dart format on
