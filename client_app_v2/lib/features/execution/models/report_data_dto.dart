import 'dart:convert';
import 'dart:isolate';
import 'package:client_app/utils/safe_cast.dart';

/// Strictly typed DTO for a single reporting axis (e.g., metric, category).
class ReportAxisDTO {
  final String name;
  final String? description;
  final double? score;
  final String justification;
  final String? citedSourceId;
  final String? citedTextQuote;
  final String? citedWebCitation;

  // Epic 6: XAI Output Extensions
  final String? coaching;
  final double? confidence;
  final String? falsification;
  final String? missingContext;
  final bool? riskFlag;
  final List<String>? remediationSteps;
  final String? emotionalSentiment;
  final String? theoryLink;

  final double scaleMin;
  final double scaleMax;
  final Map<String, String> scaleLabels;

  const ReportAxisDTO({
    required this.name,
    this.description,
    this.score,
    required this.justification,
    this.citedSourceId,
    this.citedTextQuote,
    this.citedWebCitation,
    this.coaching,
    this.confidence,
    this.falsification,
    this.missingContext,
    this.riskFlag,
    this.remediationSteps,
    this.emotionalSentiment,
    this.theoryLink,
    required this.scaleMin,
    required this.scaleMax,
    required this.scaleLabels,
  });

  /// Instantiates a strictly typed [ReportAxisDTO] from raw JSON.
  /// Enforces Fail-Fast via SafeCast parsing preventing dynamic type errors.
  factory ReportAxisDTO.fromJson(Map<String, dynamic> json) {
    Map<String, String> parsedLabels = {};
    if (json['scale_labels'] is Map) {
      json['scale_labels'].forEach(
        (k, v) => parsedLabels[k.toString()] = v.toString(),
      );
    }

    return ReportAxisDTO(
      name: SafeCast.safeString(json['name']),
      description: json['description']?.toString(),
      score: json['score'] != null ? SafeCast.safeDouble(json['score']) : null,
      justification: SafeCast.safeString(json['justification']),
      citedSourceId: json['cited_source_id']?.toString(),
      citedTextQuote: json['cited_text_quote']?.toString(),
      citedWebCitation: json['cited_web_citation']?.toString(),
      coaching: json['coaching']?.toString(),
      confidence:
          json['confidence'] != null
              ? SafeCast.safeDouble(json['confidence'])
              : null,
      falsification: json['falsification']?.toString(),
      missingContext: json['missing_context']?.toString(),
      riskFlag:
          json['risk_flag'] != null
              ? SafeCast.safeBool(json['risk_flag'])
              : null,
      remediationSteps:
          json['remediation_steps'] != null
              ? SafeCast.safeList(
                json['remediation_steps'],
              ).map((e) => e.toString()).toList()
              : null,
      emotionalSentiment: json['emotional_sentiment']?.toString(),
      theoryLink: json['theory_link']?.toString(),
      scaleMin: SafeCast.safeDouble(json['scale_min'], 0.0),
      scaleMax: SafeCast.safeDouble(json['scale_max'], 6.0),
      scaleLabels: parsedLabels,
    );
  }
}

/// Strictly typed DTO representing a single layout block dynamically defining how to render axes.
class ReportLayoutDTO {
  final String presetView;
  final String? matrixType;
  final Map<String, String> title;
  final Map<String, String> description;
  final List<ReportAxisDTO> axes;
  final bool showText;

  const ReportLayoutDTO({
    required this.presetView,
    this.matrixType,
    required this.title,
    required this.description,
    required this.axes,
    required this.showText,
  });

  factory ReportLayoutDTO.fromJson(Map<String, dynamic> json) {
    final preset = SafeCast.safeString(json['preset_view'], '1d_metrics');
    if (json['axes'] == null || json['axes'] is! List) {
      throw ArgumentError(
        'CRITICAL: axes field is missing or invalid in ReportLayoutDTO payload. Fail-Fast enforced.',
      );
    }
    return ReportLayoutDTO(
      presetView: preset.isEmpty ? '1d_metrics' : preset,
      matrixType: json['matrix_type']?.toString(),
      title: Map<String, String>.from(
        SafeCast.safeMap(
          json['title'],
        ).map((k, v) => MapEntry(k.toString(), v.toString())),
      ),
      description: Map<String, String>.from(
        SafeCast.safeMap(
          json['description'],
        ).map((k, v) => MapEntry(k.toString(), v.toString())),
      ),
      axes:
          SafeCast.safeList(
            json['axes'],
          ).map((e) => ReportAxisDTO.fromJson(SafeCast.safeMap(e))).toList(),
      showText: SafeCast.safeBool(json['show_text'], true),
    );
  }
}

/// Strictly typed DTO for a single MCP Tool Loop audit trace entry.
/// Used by XAIEvidenceBox to display AI fact-check sources.
class MCPToolAuditDTO {
  final String toolId;
  final String stepName;
  final String query;
  final String responseSummary;
  final List<String> sourceUrls;
  final String? timestamp;
  final int durationMs;

  const MCPToolAuditDTO({
    required this.toolId,
    required this.stepName,
    required this.query,
    required this.responseSummary,
    required this.sourceUrls,
    this.timestamp,
    required this.durationMs,
  });

  /// SafeCast parsing — Graceful Degradation (§6.3).
  factory MCPToolAuditDTO.fromJson(Map<String, dynamic> json) {
    return MCPToolAuditDTO(
      toolId: SafeCast.safeString(json['tool_id']),
      stepName: SafeCast.safeString(json['step_name']),
      query: SafeCast.safeString(json['query']),
      responseSummary: SafeCast.safeString(json['response_summary']),
      sourceUrls:
          SafeCast.safeList(
            json['source_urls'],
          ).map((e) => e.toString()).toList(),
      timestamp: json['timestamp']?.toString(),
      durationMs: SafeCast.safeInt(json['duration_ms']),
    );
  }
}

/// Strictly typed DTO representing the universal V3 Render Payload.
class ReportDataDTO {
  final String workflowId;
  final String profileId;
  final Map<String, dynamic> profileName;
  final Map<String, String> availableProfiles;
  final double? globalScore;
  final List<ReportLayoutDTO> layouts;

  final String? createdAt;
  final String? orgName;
  final double? costEstimate;
  final int? totalTokens;
  final int? promptTokens;
  final int? completionTokens;
  final int? reasoningTokens;

  // MCP Tool Loop Audit Trail (XAI Evidence for Frontend)
  final List<MCPToolAuditDTO> mcpToolAudit;

  const ReportDataDTO({
    required this.workflowId,
    required this.profileId,
    required this.profileName,
    required this.availableProfiles,
    this.globalScore,
    required this.layouts,
    this.createdAt,
    this.orgName,
    this.costEstimate,
    this.totalTokens,
    this.promptTokens,
    this.completionTokens,
    this.reasoningTokens,
    this.mcpToolAudit = const [],
  });

  /// Instantiates a strictly typed [ReportDataDTO] from raw JSON.
  /// Fail-Fast: Any missing or corrupted keys will yield to strict defaults.
  factory ReportDataDTO.fromJson(Map<String, dynamic> json) {
    if (json['layouts'] == null || json['layouts'] is! List) {
      throw ArgumentError(
        'CRITICAL: layouts field is missing or invalid in ReportDataDTO payload. Fail-Fast enforced.',
      );
    }

    return ReportDataDTO(
      workflowId: SafeCast.safeString(json['workflow_id']),
      profileId: SafeCast.safeString(json['profile_id']),
      profileName: SafeCast.safeMap(json['profile_name']),
      availableProfiles: Map<String, String>.from(
        SafeCast.safeMap(
          json['available_profiles'],
        ).map((k, v) => MapEntry(k.toString(), v.toString())),
      ),
      globalScore:
          json['global_score'] != null
              ? SafeCast.safeDouble(json['global_score'])
              : null,
      layouts:
          SafeCast.safeList(
            json['layouts'],
          ).map((e) => ReportLayoutDTO.fromJson(SafeCast.safeMap(e))).toList(),
      createdAt: json['created_at']?.toString(),
      orgName: json['org_name']?.toString(),
      costEstimate:
          json['cost_estimate'] != null
              ? SafeCast.safeDouble(json['cost_estimate'])
              : null,
      totalTokens:
          json['total_tokens'] != null
              ? SafeCast.safeInt(json['total_tokens'])
              : null,
      promptTokens:
          json['prompt_tokens'] != null
              ? SafeCast.safeInt(json['prompt_tokens'])
              : null,
      completionTokens:
          json['completion_tokens'] != null
              ? SafeCast.safeInt(json['completion_tokens'])
              : null,
      reasoningTokens:
          json['reasoning_tokens'] != null
              ? SafeCast.safeInt(json['reasoning_tokens'])
              : null,
      mcpToolAudit:
          json['mcp_tool_audit'] != null
              ? SafeCast.safeList(json['mcp_tool_audit'])
                  .map((e) => MCPToolAuditDTO.fromJson(SafeCast.safeMap(e)))
                  .toList()
              : const [],
    );
  }

  /// Parses a heavy raw JSON string into a ReportDataDTO entirely off the Main Thread.
  /// This is mandatory for large RAG synthesis payloads to prevent Main Thread Jank.
  static Future<ReportDataDTO> parseInBackground(String rawJson) async {
    return Isolate.run(() {
      final decoded = jsonDecode(rawJson) as Map<String, dynamic>;
      return ReportDataDTO.fromJson(decoded);
    });
  }
}
