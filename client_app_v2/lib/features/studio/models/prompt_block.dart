import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/safe_cast.dart';

/// Data types allowed for PromptBlock extracted values.
enum BlockDataType {
  floatType('float'),
  intType('int'),
  stringType('string'),
  instruction('instruction'),
  panel('panel'),
  compliance('compliance'),
  question('question'),
  criteria('criteria');

  final String backendValue;
  const BlockDataType(this.backendValue);

  static BlockDataType fromString(String val) {
    final lower = val.toLowerCase();
    return BlockDataType.values.firstWhere(
      (e) => e.backendValue == lower,
      orElse: () => BlockDataType.stringType,
    );
  }
}

class TheoryGrounding {
  final String sourceUrl;
  final String citationReference;

  const TheoryGrounding({
    required this.sourceUrl,
    required this.citationReference,
  });

  factory TheoryGrounding.fromJson(Map<String, dynamic> json) {
    return TheoryGrounding(
      sourceUrl: SafeCast.safeString(json['source_url']),
      citationReference: SafeCast.safeString(json['citation_reference']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'source_url': sourceUrl,
      'citation_reference': citationReference,
    };
  }

  TheoryGrounding copyWith({
    String? sourceUrl,
    String? citationReference,
  }) {
    return TheoryGrounding(
      sourceUrl: sourceUrl ?? this.sourceUrl,
      citationReference: citationReference ?? this.citationReference,
    );
  }
}

class MatrixClaim {
  final I18nText label;
  final String aiDescription;

  const MatrixClaim({
    required this.label,
    required this.aiDescription,
  });

  factory MatrixClaim.fromJson(Map<String, dynamic> json) {
    return MatrixClaim(
      label: I18nText.fromJson(SafeCast.safeMap(json['label'])),
      aiDescription: SafeCast.safeString(json['ai_description']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'label': label.toJson(),
      'ai_description': aiDescription,
    };
  }

  MatrixClaim copyWith({
    I18nText? label,
    String? aiDescription,
  }) {
    return MatrixClaim(
      label: label ?? this.label,
      aiDescription: aiDescription ?? this.aiDescription,
    );
  }
}

class MatrixRow {
  final I18nText label;
  final String aiDescription;

  const MatrixRow({
    required this.label,
    required this.aiDescription,
  });

  factory MatrixRow.fromJson(Map<String, dynamic> json) {
    return MatrixRow(
      label: I18nText.fromJson(SafeCast.safeMap(json['label'])),
      aiDescription: SafeCast.safeString(json['ai_description']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'label': label.toJson(),
      'ai_description': aiDescription,
    };
  }

  MatrixRow copyWith({
    I18nText? label,
    String? aiDescription,
  }) {
    return MatrixRow(
      label: label ?? this.label,
      aiDescription: aiDescription ?? this.aiDescription,
    );
  }
}

class MatrixScale {
  final int score;
  final I18nText? name;
  final String aiLabel;
  final List<MatrixClaim> claims;

  const MatrixScale({
    required this.score,
    this.name,
    required this.aiLabel,
    required this.claims,
  });

  factory MatrixScale.fromJson(Map<String, dynamic> json) {
    final claimsRaw = SafeCast.safeList(json['claims']);
    return MatrixScale(
      score: SafeCast.safeInt(json['score']),
      name: json['name'] != null ? I18nText.fromJson(SafeCast.safeMap(json['name'])) : null,
      aiLabel: SafeCast.safeString(json['ai_label']),
      claims: claimsRaw.map((e) => MatrixClaim.fromJson(SafeCast.safeMap(e))).toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      if (name != null) 'name': name!.toJson(),
      'ai_label': aiLabel,
      'claims': claims.map((e) => e.toJson()).toList(),
    };
  }

  MatrixScale copyWith({
    int? score,
    I18nText? name,
    String? aiLabel,
    List<MatrixClaim>? claims,
  }) {
    return MatrixScale(
      score: score ?? this.score,
      name: name ?? this.name,
      aiLabel: aiLabel ?? this.aiLabel,
      claims: claims ?? this.claims,
    );
  }
}

/// V2 PromptBlock representation.
/// Fuses legacy Components and Matrices into a unified directive model.
class PromptBlock {
  final String id;
  final String slug;
  final I18nText label;
  final I18nText description;
  final String? aiDescription;
  final String categoryId;
  final BlockDataType type;
  final bool allowDecimals;
  final List<String> outputExtensions;
  final TheoryGrounding? theoryGrounding;
  final int? scaleMin;
  final int? scaleMax;
  final List<MatrixScale>? scales;
  final List<MatrixRow>? rows;
  final List<I18nText>? columns;

  const PromptBlock({
    required this.id,
    required this.slug,
    required this.label,
    required this.description,
    this.aiDescription,
    this.categoryId = 'system',
    this.type = BlockDataType.stringType,
    this.allowDecimals = false,
    this.outputExtensions = const [],
    this.theoryGrounding,
    this.scaleMin,
    this.scaleMax,
    this.scales,
    this.rows,
    this.columns,
  });

  factory PromptBlock.fromJson(Map<String, dynamic> json) {
    final scalesRaw = json['scales'] as List?;
    final rowsRaw = json['rows'] as List?;
    final columnsRaw = json['columns'] as List?;
    final extensionsRaw = json['output_extensions'] as List?;

    return PromptBlock(
      id: SafeCast.safeString(json['id']),
      slug: SafeCast.safeString(json['slug']),
      label: I18nText.fromJson(SafeCast.safeMap(json['label'])),
      description: I18nText.fromJson(SafeCast.safeMap(json['description'])),
      aiDescription: json['ai_description'] != null ? SafeCast.safeString(json['ai_description']) : null,
      categoryId: SafeCast.safeString(json['category_id'], 'system'),
      type: BlockDataType.fromString(SafeCast.safeString(json['type'])),
      allowDecimals: SafeCast.safeBool(json['allow_decimals']),
      outputExtensions: extensionsRaw?.map((e) => SafeCast.safeString(e)).toList() ?? [],
      theoryGrounding: json['theory_grounding'] != null ? TheoryGrounding.fromJson(SafeCast.safeMap(json['theory_grounding'])) : null,
      scaleMin: json['scale_min'] != null ? SafeCast.safeInt(json['scale_min']) : null,
      scaleMax: json['scale_max'] != null ? SafeCast.safeInt(json['scale_max']) : null,
      scales: scalesRaw?.map((e) => MatrixScale.fromJson(SafeCast.safeMap(e))).toList(),
      rows: rowsRaw?.map((e) => MatrixRow.fromJson(SafeCast.safeMap(e))).toList(),
      columns: columnsRaw?.map((e) => I18nText.fromJson(SafeCast.safeMap(e))).toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'slug': slug,
      'label': label.toJson(),
      'description': description.toJson(),
      if (aiDescription != null) 'ai_description': aiDescription,
      'category_id': categoryId,
      'type': type.backendValue,
      'allow_decimals': allowDecimals,
      'output_extensions': outputExtensions,
      if (theoryGrounding != null) 'theory_grounding': theoryGrounding!.toJson(),
      if (scaleMin != null) 'scale_min': scaleMin,
      if (scaleMax != null) 'scale_max': scaleMax,
      if (scales != null) 'scales': scales!.map((e) => e.toJson()).toList(),
      if (rows != null) 'rows': rows!.map((e) => e.toJson()).toList(),
      if (columns != null) 'columns': columns!.map((e) => e.toJson()).toList(),
    };
  }

  PromptBlock copyWith({
    String? id,
    String? slug,
    I18nText? label,
    I18nText? description,
    String? aiDescription,
    String? categoryId,
    BlockDataType? type,
    bool? allowDecimals,
    List<String>? outputExtensions,
    TheoryGrounding? theoryGrounding,
    int? scaleMin,
    int? scaleMax,
    List<MatrixScale>? scales,
    List<MatrixRow>? rows,
    List<I18nText>? columns,
  }) {
    return PromptBlock(
      id: id ?? this.id,
      slug: slug ?? this.slug,
      label: label ?? this.label,
      description: description ?? this.description,
      aiDescription: aiDescription ?? this.aiDescription,
      categoryId: categoryId ?? this.categoryId,
      type: type ?? this.type,
      allowDecimals: allowDecimals ?? this.allowDecimals,
      outputExtensions: outputExtensions ?? this.outputExtensions,
      theoryGrounding: theoryGrounding ?? this.theoryGrounding,
      scaleMin: scaleMin ?? this.scaleMin,
      scaleMax: scaleMax ?? this.scaleMax,
      scales: scales ?? this.scales,
      rows: rows ?? this.rows,
      columns: columns ?? this.columns,
    );
  }

  /// Parses raw JSON string to PromptBlock in a background isolate
  static Future<PromptBlock> parseInBackground(String rawJson) async {
    return Isolate.run(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return PromptBlock.fromJson(decoded);
    });
  }

  static Future<List<PromptBlock>> parseListInBackground(List<dynamic> rawList) async {
    return Isolate.run(() {
      return rawList.map((e) => PromptBlock.fromJson(e as Map<String, dynamic>)).toList();
    });
  }
}
