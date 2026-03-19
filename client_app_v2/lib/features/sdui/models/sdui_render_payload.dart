import 'package:client_app/utils/safe_cast.dart';

/// Represents the top-level V6.0 Universal Render Payload returned by the backend API.
class SduiRenderPayload {
  final SduiBlueprint blueprint;
  final String targetLocale;
  final Map<String, String> resolvedNotes;
  final List<String> bibliography;

  const SduiRenderPayload({
    required this.blueprint,
    required this.targetLocale,
    required this.resolvedNotes,
    required this.bibliography,
  });

  factory SduiRenderPayload.fromJson(Map<String, dynamic> json) {
    return SduiRenderPayload(
      blueprint: SduiBlueprint.fromJson(SafeCast.safeMap(json['blueprint'])),
      targetLocale:
          SafeCast.safeString(json['target_locale']).isNotEmpty
              ? SafeCast.safeString(json['target_locale'])
              : 'fi',
      resolvedNotes: SafeCast.safeMap(
        json['resolved_notes'],
      ).map((key, value) => MapEntry(key, SafeCast.safeString(value))),
      bibliography:
          SafeCast.safeList(
            json['bibliography'],
          ).map(SafeCast.safeString).toList(),
    );
  }
}

/// Represents the Blueprint definition inside the render payload.
class SduiBlueprint {
  final List<SduiComponent> components;

  const SduiBlueprint({required this.components});

  factory SduiBlueprint.fromJson(Map<String, dynamic> json) {
    return SduiBlueprint(
      components:
          SafeCast.safeList(
            json['components'],
          ).map((c) => SduiComponent.fromJson(SafeCast.safeMap(c))).toList(),
    );
  }
}

/// A parsed SDUI Component adhering to strictly bound attributes without assuming logic.
class SduiComponent {
  final String type;

  // Header / Common
  final dynamic title;

  // 1D Gauge
  final double value;
  final double scaleMax;
  final String scaleText;
  final String displayValue;
  final String displayValueOnly;
  final String displayMaxOnly;
  final double visualPct;

  // 2D Matrix / 3D Scatter shared axis definitions
  final dynamic xTitle;
  final dynamic yTitle;
  final dynamic zTitle;

  // Coordinates for Matrices & Scatters
  final double xValue;
  final double yValue;
  final double zValue;

  final double xScaleMax;
  final double yScaleMax;
  final double zScaleMax;

  // Extracted note text for nodes
  final String xNoteText;
  final String yNoteText;
  final String zNoteText;

  // Scale category text labels
  final String xScaleText;
  final String yScaleText;
  final String zScaleText;

  // Render Display Formatting
  final String xDisplay;
  final String xDisplayValueOnly;
  final String xDisplayMaxOnly;
  final double xVisualPct;
  final String yDisplay;
  final String yDisplayValueOnly;
  final String yDisplayMaxOnly;
  final double yVisualPct;
  final String zDisplay;
  final String zDisplayValueOnly;
  final String zDisplayMaxOnly;
  final double zVisualPct;
  final double zVisualSize;
  final double zVisualOffset;

  // Grid Row support
  final int columns;
  final List<SduiComponent> children;

  const SduiComponent({
    required this.type,
    this.title = '',
    required this.value,
    required this.scaleMax,
    required this.scaleText,
    this.displayValue = '',
    this.displayValueOnly = '',
    this.displayMaxOnly = '',
    this.visualPct = 0.0,
    this.xTitle = '',
    this.yTitle = '',
    this.zTitle = '',
    required this.xValue,
    required this.yValue,
    required this.zValue,
    required this.xScaleMax,
    required this.yScaleMax,
    required this.zScaleMax,
    required this.xNoteText,
    required this.yNoteText,
    required this.zNoteText,
    this.xScaleText = '',
    this.yScaleText = '',
    this.zScaleText = '',
    this.xDisplay = '',
    this.xDisplayValueOnly = '',
    this.xDisplayMaxOnly = '',
    this.xVisualPct = 0.0,
    this.yDisplay = '',
    this.yDisplayValueOnly = '',
    this.yDisplayMaxOnly = '',
    this.yVisualPct = 0.0,
    this.zDisplay = '',
    this.zDisplayValueOnly = '',
    this.zDisplayMaxOnly = '',
    this.zVisualPct = 0.0,
    this.zVisualSize = 0.0,
    this.zVisualOffset = 0.0,
    this.columns = 2,
    this.children = const [],
  });

  factory SduiComponent.fromJson(Map<String, dynamic> json) {
    return SduiComponent(
      type: SafeCast.safeString(json['type']),
      title: json['title'] ?? '',
      value: SafeCast.safeDouble(json['value']),
      scaleMax: SafeCast.safeDouble(json['scale_max']),
      scaleText: SafeCast.safeString(json['scale_text']),
      displayValue: SafeCast.safeString(json['display_value']),
      displayValueOnly: SafeCast.safeString(json['display_value_only']),
      displayMaxOnly: SafeCast.safeString(json['display_max_only']),
      visualPct: SafeCast.safeDouble(json['visual_pct']),
      xTitle: json['x_title'] ?? '',
      yTitle: json['y_title'] ?? '',
      zTitle: json['z_title'] ?? '',
      xValue: SafeCast.safeDouble(json['x_value']),
      yValue: SafeCast.safeDouble(json['y_value']),
      zValue: SafeCast.safeDouble(json['z_value']),
      xScaleMax: SafeCast.safeDouble(json['x_scale_max']),
      yScaleMax: SafeCast.safeDouble(json['y_scale_max']),
      zScaleMax: SafeCast.safeDouble(json['z_scale_max']),
      xNoteText: SafeCast.safeString(json['x_note_text']),
      yNoteText: SafeCast.safeString(json['y_note_text']),
      zNoteText: SafeCast.safeString(json['z_note_text']),
      xScaleText: SafeCast.safeString(json['x_scale_text']),
      yScaleText: SafeCast.safeString(json['y_scale_text']),
      zScaleText: SafeCast.safeString(json['z_scale_text']),
      xDisplay: SafeCast.safeString(json['x_display']),
      xDisplayValueOnly: SafeCast.safeString(json['x_display_value_only']),
      xDisplayMaxOnly: SafeCast.safeString(json['x_display_max_only']),
      xVisualPct: SafeCast.safeDouble(json['x_visual_pct']),
      yDisplay: SafeCast.safeString(json['y_display']),
      yDisplayValueOnly: SafeCast.safeString(json['y_display_value_only']),
      yDisplayMaxOnly: SafeCast.safeString(json['y_display_max_only']),
      yVisualPct: SafeCast.safeDouble(json['y_visual_pct']),
      zDisplay: SafeCast.safeString(json['z_display']),
      zDisplayValueOnly: SafeCast.safeString(json['z_display_value_only']),
      zDisplayMaxOnly: SafeCast.safeString(json['z_display_max_only']),
      zVisualPct: SafeCast.safeDouble(json['z_visual_pct']),
      zVisualSize: SafeCast.safeDouble(json['z_visual_size']),
      zVisualOffset: SafeCast.safeDouble(json['z_visual_offset']),
      columns: SafeCast.safeInt(json['columns'], 2),
      children:
          SafeCast.safeList(
            json['children'],
          ).map((c) => SduiComponent.fromJson(SafeCast.safeMap(c))).toList(),
    );
  }
}
