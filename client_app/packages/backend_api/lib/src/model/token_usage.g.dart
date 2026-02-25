// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'token_usage.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TokenUsageCWProxy {
  TokenUsage promptTokens(int? promptTokens);

  TokenUsage completionTokens(int? completionTokens);

  TokenUsage totalTokens(int? totalTokens);

  TokenUsage costUsd(num? costUsd);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TokenUsage(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TokenUsage(...).copyWith(id: 12, name: "My name")
  /// ````
  TokenUsage call({
    int? promptTokens,
    int? completionTokens,
    int? totalTokens,
    num? costUsd,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTokenUsage.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTokenUsage.copyWith.fieldName(...)`
class _$TokenUsageCWProxyImpl implements _$TokenUsageCWProxy {
  const _$TokenUsageCWProxyImpl(this._value);

  final TokenUsage _value;

  @override
  TokenUsage promptTokens(int? promptTokens) =>
      this(promptTokens: promptTokens);

  @override
  TokenUsage completionTokens(int? completionTokens) =>
      this(completionTokens: completionTokens);

  @override
  TokenUsage totalTokens(int? totalTokens) => this(totalTokens: totalTokens);

  @override
  TokenUsage costUsd(num? costUsd) => this(costUsd: costUsd);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TokenUsage(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TokenUsage(...).copyWith(id: 12, name: "My name")
  /// ````
  TokenUsage call({
    Object? promptTokens = const $CopyWithPlaceholder(),
    Object? completionTokens = const $CopyWithPlaceholder(),
    Object? totalTokens = const $CopyWithPlaceholder(),
    Object? costUsd = const $CopyWithPlaceholder(),
  }) {
    return TokenUsage(
      promptTokens: promptTokens == const $CopyWithPlaceholder()
          ? _value.promptTokens
          // ignore: cast_nullable_to_non_nullable
          : promptTokens as int?,
      completionTokens: completionTokens == const $CopyWithPlaceholder()
          ? _value.completionTokens
          // ignore: cast_nullable_to_non_nullable
          : completionTokens as int?,
      totalTokens: totalTokens == const $CopyWithPlaceholder()
          ? _value.totalTokens
          // ignore: cast_nullable_to_non_nullable
          : totalTokens as int?,
      costUsd: costUsd == const $CopyWithPlaceholder()
          ? _value.costUsd
          // ignore: cast_nullable_to_non_nullable
          : costUsd as num?,
    );
  }
}

extension $TokenUsageCopyWith on TokenUsage {
  /// Returns a callable class that can be used as follows: `instanceOfTokenUsage.copyWith(...)` or like so:`instanceOfTokenUsage.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TokenUsageCWProxy get copyWith => _$TokenUsageCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TokenUsage _$TokenUsageFromJson(Map<String, dynamic> json) => $checkedCreate(
  'TokenUsage',
  json,
  ($checkedConvert) {
    final val = TokenUsage(
      promptTokens: $checkedConvert(
        'prompt_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      completionTokens: $checkedConvert(
        'completion_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      totalTokens: $checkedConvert(
        'total_tokens',
        (v) => (v as num?)?.toInt() ?? 0,
      ),
      costUsd: $checkedConvert('cost_usd', (v) => v as num? ?? 0.0),
    );
    return val;
  },
  fieldKeyMap: const {
    'promptTokens': 'prompt_tokens',
    'completionTokens': 'completion_tokens',
    'totalTokens': 'total_tokens',
    'costUsd': 'cost_usd',
  },
);

Map<String, dynamic> _$TokenUsageToJson(TokenUsage instance) =>
    <String, dynamic>{
      'prompt_tokens': ?instance.promptTokens,
      'completion_tokens': ?instance.completionTokens,
      'total_tokens': ?instance.totalTokens,
      'cost_usd': ?instance.costUsd,
    };
