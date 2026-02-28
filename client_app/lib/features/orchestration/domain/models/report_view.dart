enum ReferenceIntent {
  search,
  grounding,
  internalKb,
  unknown
}

ReferenceIntent _parseIntent(String? value) {
  switch (value) {
    case 'SEARCH': return ReferenceIntent.search;
    case 'GROUNDING': return ReferenceIntent.grounding;
    case 'INTERNAL_KB': return ReferenceIntent.internalKb;
    default: return ReferenceIntent.unknown;
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
      intent: _parseIntent(json['intent']),
      title: json['title'],
      snippet: json['snippet'] ?? '',
      url: json['url'],
    );
  }
}

class ReportView {
  final String viewId;
  final String title;
  final String statusTheme;
  final List<UiSection> sections;
  final List<ReferenceItem> references;
  final Map<String, dynamic>? metrics;

  ReportView({
    required this.viewId,
    required this.title,
    required this.statusTheme,
    required this.sections,
    required this.references,
    this.metrics,
  });

  factory ReportView.fromJson(Map<String, dynamic> json) {
    return ReportView(
      viewId: json['view_id'] ?? '',
      title: json['title'] ?? '',
      statusTheme: json['status_theme'] ?? 'success',
      sections:
          (json['sections'] as List<dynamic>? ?? [])
              .map((e) => UiSection.fromJson(e))
              .toList(),
      references:
          (json['references'] as List<dynamic>? ?? [])
              .map((e) => ReferenceItem.fromJson(e))
              .toList(),
      metrics: json['metrics'] as Map<String, dynamic>?,
    );
  }
}

class UiSection {
  final String id;
  final String type;
  final String title;
  final Map<String, dynamic> data;

  UiSection({
    required this.id,
    required this.type,
    required this.title,
    required this.data,
  });

  factory UiSection.fromJson(Map<String, dynamic> json) {
    return UiSection(
      id: json['id'] ?? '',
      type: json['type'] ?? '',
      title: json['title'] ?? '',
      data: json['data'] as Map<String, dynamic>? ?? {},
    );
  }
}
