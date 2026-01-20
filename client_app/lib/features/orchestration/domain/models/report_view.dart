
class ReportView {
  final String viewId;
  final String title;
  final String statusTheme;
  final List<UiSection> sections;

  ReportView({
    required this.viewId,
    required this.title,
    required this.statusTheme,
    required this.sections,
  });

  factory ReportView.fromJson(Map<String, dynamic> json) {
    return ReportView(
      viewId: json['view_id'] ?? '',
      title: json['title'] ?? '',
      statusTheme: json['status_theme'] ?? 'success',
      sections: (json['sections'] as List<dynamic>? ?? [])
          .map((e) => UiSection.fromJson(e))
          .toList(),
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
