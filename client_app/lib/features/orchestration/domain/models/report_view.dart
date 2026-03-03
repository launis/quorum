enum ReferenceIntent { search, grounding, internalKb, unknown }

ReferenceIntent _parseReferenceIntent(String? value) {
  switch (value) {
    case 'SEARCH':
      return ReferenceIntent.search;
    case 'GROUNDING':
      return ReferenceIntent.grounding;
    case 'INTERNAL_KB':
      return ReferenceIntent.internalKb;
    default:
      return ReferenceIntent.unknown;
  }
}

enum SemanticIntent { warning, success, neutral, danger, info, unknown }

SemanticIntent _parseSemanticIntent(String? value) {
  switch (value) {
    case 'WARNING':
      return SemanticIntent.warning;
    case 'SUCCESS':
      return SemanticIntent.success;
    case 'NEUTRAL':
      return SemanticIntent.neutral;
    case 'DANGER':
      return SemanticIntent.danger;
    case 'INFO':
      return SemanticIntent.info;
    default:
      return SemanticIntent.unknown;
  }
}

enum BlockType {
  paragraph,
  metric,
  list,
  dataGrid,
  citation,
  quotation,
  card,
  unknown,
}

BlockType _parseBlockType(String? value) {
  switch (value) {
    case 'PARAGRAPH':
      return BlockType.paragraph;
    case 'METRIC':
      return BlockType.metric;
    case 'LIST':
      return BlockType.list;
    case 'DATA_GRID':
      return BlockType.dataGrid;
    case 'CITATION':
      return BlockType.citation;
    case 'QUOTATION':
      return BlockType.quotation;
    case 'CARD':
      return BlockType.card;
    default:
      return BlockType.unknown;
  }
}

class ReferenceItem {
  final String id;
  final ReferenceIntent intent;
  final String? title;
  final String snippet;
  final String? url;

  ReferenceItem({
    required this.id,
    required this.intent,
    this.title,
    required this.snippet,
    this.url,
  });

  factory ReferenceItem.fromJson(Map<String, dynamic> json) {
    return ReferenceItem(
      id: json['id'] ?? '',
      intent: _parseReferenceIntent(json['intent']),
      title: json['title'],
      snippet: json['snippet'] ?? '',
      url: json['url'],
    );
  }
}

class SystemNotification {
  final String title;
  final String message;
  final String level;

  SystemNotification({
    required this.title,
    required this.message,
    required this.level,
  });

  factory SystemNotification.fromJson(Map<String, dynamic> json) {
    return SystemNotification(
      title: json['title'] ?? '',
      message: json['message'] ?? '',
      level: json['level'] ?? 'info',
    );
  }
}

class SemanticBlock {
  final String id;
  final BlockType type;
  final SemanticIntent intent;
  final String? label;
  final dynamic value;
  final Map<String, dynamic> metadata;

  SemanticBlock({
    required this.id,
    required this.type,
    required this.intent,
    this.label,
    this.value,
    this.metadata = const {},
  });

  factory SemanticBlock.fromJson(Map<String, dynamic> json) {
    return SemanticBlock(
      id: json['id'] ?? '',
      type: _parseBlockType(json['type']),
      intent: _parseSemanticIntent(json['intent']),
      label: json['label'],
      value: json['value'],
      metadata:
          json['metadata'] != null
              ? Map<String, dynamic>.from(json['metadata'])
              : {},
    );
  }
}

class SemanticReport {
  final String reportId;
  final String title;
  final SemanticIntent intent;
  final List<SemanticBlock> blocks;
  final List<ReferenceItem> references;
  final Map<String, dynamic>? metrics;
  final SystemNotification? systemNotification;

  SemanticReport({
    required this.reportId,
    required this.title,
    required this.intent,
    required this.blocks,
    required this.references,
    this.metrics,
    this.systemNotification,
  });

  factory SemanticReport.fromJson(Map<String, dynamic> json) {
    return SemanticReport(
      reportId:
          json['report_id'] ??
          json['view_id'] ??
          '', // Fallback to view_id just in case
      title: json['title'] ?? '',
      intent: _parseSemanticIntent(
        json['intent'] ?? json['status_theme'],
      ), // Fallback
      blocks:
          (json['blocks'] as List<dynamic>? ?? [])
              .map((e) => SemanticBlock.fromJson(e))
              .toList(),
      references:
          (json['references'] as List<dynamic>? ?? [])
              .map((e) => ReferenceItem.fromJson(e))
              .toList(),
      metrics: json['metrics'] as Map<String, dynamic>?,
      systemNotification:
          json['system_notification'] != null
              ? SystemNotification.fromJson(json['system_notification'])
              : null,
    );
  }
}
