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
  final String title;

  // 1D Gauge
  final double value;
  final double scaleMax;
  final String scaleText;

  // 2D Matrix / 3D Scatter shared axis definitions
  final String xTitle;
  final String yTitle;
  final String zTitle;

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

  // Grid Row support
  final int columns;
  final List<SduiComponent> children;

  const SduiComponent({
    required this.type,
    required this.title,
    required this.value,
    required this.scaleMax,
    required this.scaleText,
    required this.xTitle,
    required this.yTitle,
    required this.zTitle,
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
    this.columns = 2,
    this.children = const [],
  });

  factory SduiComponent.fromJson(Map<String, dynamic> json) {
    return SduiComponent(
      type: SafeCast.safeString(json['type']),
      title: SafeCast.safeString(json['title']),
      value: SafeCast.safeDouble(json['value']),
      scaleMax: SafeCast.safeDouble(json['scale_max']),
      scaleText: SafeCast.safeString(json['scale_text']),
      xTitle: SafeCast.safeString(json['x_title']),
      yTitle: SafeCast.safeString(json['y_title']),
      zTitle: SafeCast.safeString(json['z_title']),
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
      columns: SafeCast.safeInt(json['columns'], 2),
      children:
          SafeCast.safeList(
            json['children'],
          ).map((c) => SduiComponent.fromJson(SafeCast.safeMap(c))).toList(),
    );
  }
}
