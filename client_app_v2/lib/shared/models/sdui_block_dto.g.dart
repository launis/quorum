// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sdui_block_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SduiParagraphBlock _$SduiParagraphBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiParagraphBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'text',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiParagraphBlock(
      id: $checkedConvert('id', (v) => v as String?),
      text: $checkedConvert('text', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiParagraphBlockToJson(SduiParagraphBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'text': instance.text,
      'citations': instance.citations,
      'exact_quotes': instance.exactQuotes,
      'block_type': instance.$type,
    };

SduiBulletListBlock _$SduiBulletListBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiBulletListBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'items', 'block_type']);
      final val = SduiBulletListBlock(
        id: $checkedConvert('id', (v) => v as String?),
        items: $checkedConvert(
          'items',
          (v) => (v as List<dynamic>)
              .map(
                (e) =>
                    SduiBulletListItemDTO.fromJson(e as Map<String, dynamic>),
              )
              .toList(),
        ),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiBulletListBlockToJson(
  SduiBulletListBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'items': instance.items.map((e) => e.toJson()).toList(),
  'block_type': instance.$type,
};

SduiAlertBoxBlock _$SduiAlertBoxBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiAlertBoxBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'text',
        'severity',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiAlertBoxBlock(
      id: $checkedConvert('id', (v) => v as String?),
      text: $checkedConvert('text', (v) => v as String),
      severity: $checkedConvert('severity', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiAlertBoxBlockToJson(SduiAlertBoxBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'text': instance.text,
      'severity': instance.severity,
      'citations': instance.citations,
      'exact_quotes': instance.exactQuotes,
      'block_type': instance.$type,
    };

SduiHeroInsightBlock _$SduiHeroInsightBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiHeroInsightBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'id',
        'text',
        'citations',
        'exact_quotes',
        'block_type',
      ],
    );
    final val = SduiHeroInsightBlock(
      id: $checkedConvert('id', (v) => v as String?),
      text: $checkedConvert('text', (v) => v as String),
      citations: $checkedConvert(
        'citations',
        (v) =>
            (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
            const [],
      ),
      exactQuotes: $checkedConvert(
        'exact_quotes',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'exactQuotes': 'exact_quotes', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiHeroInsightBlockToJson(
  SduiHeroInsightBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'text': instance.text,
  'citations': instance.citations,
  'exact_quotes': instance.exactQuotes,
  'block_type': instance.$type,
};

SduiMarkdownBlock _$SduiMarkdownBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiMarkdownBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'text', 'block_type']);
      final val = SduiMarkdownBlock(
        id: $checkedConvert('id', (v) => v as String?),
        text: $checkedConvert('text', (v) => v as String),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiMarkdownBlockToJson(SduiMarkdownBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'text': instance.text,
      'block_type': instance.$type,
    };

SduiQuoteCardBlock _$SduiQuoteCardBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SduiQuoteCardBlock',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'quote',
            'source_aliases',
            'citations',
            'block_type',
          ],
        );
        final val = SduiQuoteCardBlock(
          id: $checkedConvert('id', (v) => v as String?),
          quote: $checkedConvert('quote', (v) => v as String),
          sourceAliases: $checkedConvert(
            'source_aliases',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          citations: $checkedConvert('citations', (v) => v as List<dynamic>),
          $type: $checkedConvert('block_type', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'sourceAliases': 'source_aliases',
        r'$type': 'block_type',
      },
    );

Map<String, dynamic> _$SduiQuoteCardBlockToJson(SduiQuoteCardBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'quote': instance.quote,
      'source_aliases': instance.sourceAliases,
      'citations': instance.citations,
      'block_type': instance.$type,
    };

SduiWarningCardBlock _$SduiWarningCardBlockFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'SduiWarningCardBlock',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['id', 'message', 'quote_text', 'block_type'],
    );
    final val = SduiWarningCardBlock(
      id: $checkedConvert('id', (v) => v as String?),
      message: $checkedConvert('message', (v) => v as String),
      quoteText: $checkedConvert('quote_text', (v) => v as String?),
      $type: $checkedConvert('block_type', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {'quoteText': 'quote_text', r'$type': 'block_type'},
);

Map<String, dynamic> _$SduiWarningCardBlockToJson(
  SduiWarningCardBlock instance,
) => <String, dynamic>{
  'id': instance.id,
  'message': instance.message,
  'quote_text': instance.quoteText,
  'block_type': instance.$type,
};

SduiNACardBlock _$SduiNACardBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'SduiNACardBlock',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'short_circuit_reason_tda_ids',
            'message',
            'block_type',
          ],
        );
        final val = SduiNACardBlock(
          id: $checkedConvert('id', (v) => v as String?),
          shortCircuitReasonTdaIds: $checkedConvert(
            'short_circuit_reason_tda_ids',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          message: $checkedConvert('message', (v) => v as String),
          $type: $checkedConvert('block_type', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'shortCircuitReasonTdaIds': 'short_circuit_reason_tda_ids',
        r'$type': 'block_type',
      },
    );

Map<String, dynamic> _$SduiNACardBlockToJson(SduiNACardBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'short_circuit_reason_tda_ids': instance.shortCircuitReasonTdaIds,
      'message': instance.message,
      'block_type': instance.$type,
    };

SduiGridBlock _$SduiGridBlockFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SduiGridBlock', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['id', 'items', 'block_type']);
      final val = SduiGridBlock(
        id: $checkedConvert('id', (v) => v as String?),
        items: $checkedConvert('items', (v) => v as List<dynamic>),
        $type: $checkedConvert('block_type', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'block_type'});

Map<String, dynamic> _$SduiGridBlockToJson(SduiGridBlock instance) =>
    <String, dynamic>{
      'id': instance.id,
      'items': instance.items,
      'block_type': instance.$type,
    };

_SduiBulletListItemDTO _$SduiBulletListItemDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('_SduiBulletListItemDTO', json, ($checkedConvert) {
  $checkKeys(json, allowedKeys: const ['text', 'citations', 'exact_quotes']);
  final val = _SduiBulletListItemDTO(
    text: $checkedConvert('text', (v) => v as String),
    citations: $checkedConvert(
      'citations',
      (v) =>
          (v as List<dynamic>?)?.map((e) => (e as num).toInt()).toList() ??
          const [],
    ),
    exactQuotes: $checkedConvert(
      'exact_quotes',
      (v) =>
          (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
    ),
  );
  return val;
}, fieldKeyMap: const {'exactQuotes': 'exact_quotes'});

Map<String, dynamic> _$SduiBulletListItemDTOToJson(
  _SduiBulletListItemDTO instance,
) => <String, dynamic>{
  'text': instance.text,
  'citations': instance.citations,
  'exact_quotes': instance.exactQuotes,
};
