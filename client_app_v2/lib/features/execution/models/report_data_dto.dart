import 'dart:convert';
import 'dart:isolate';

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
  /// Enforces Fail-Fast parsing preventing dynamic type errors.
  factory ReportAxisDTO.fromJson(Map<String, dynamic> json) {
    Map<String, String> parsedLabels = {};
    if (json['scale_labels'] is Map) {
      json['scale_labels'].forEach(
        (k, v) => parsedLabels[k.toString()] = v.toString(),
      );
    }

    return ReportAxisDTO(
      name: json['name']?.toString() ?? '',
      description: json['description']?.toString(),
      score: (json['score'] as num?)?.toDouble(),
      justification: json['justification']?.toString() ?? '',
      citedSourceId: json['cited_source_id']?.toString(),
      citedTextQuote: json['cited_text_quote']?.toString(),
      citedWebCitation: json['cited_web_citation']?.toString(),
      coaching: json['coaching']?.toString(),
      confidence: (json['confidence'] as num?)?.toDouble(),
      falsification: json['falsification']?.toString(),
      missingContext: json['missing_context']?.toString(),
      riskFlag: json['risk_flag'] is bool
          ? json['risk_flag'] as bool
          : (json['risk_flag']?.toString() == 'true'),
      remediationSteps: json['remediation_steps'] is List
          ? (json['remediation_steps'] as List)
                .map((e) => e.toString())
                .toList()
          : null,
      emotionalSentiment: json['emotional_sentiment']?.toString(),
      theoryLink: json['theory_link']?.toString(),
      scaleMin: (json['scale_min'] as num?)?.toDouble() ?? 0.0,
      scaleMax: (json['scale_max'] as num?)?.toDouble() ?? 6.0,
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
    final presetRaw = json['preset_view']?.toString() ?? '';
    final preset = presetRaw.isEmpty ? '1d_metrics' : presetRaw;
    if (json['axes'] == null || json['axes'] is! List) {
      throw const FormatException(
        'CRITICAL: axes field is missing or invalid in ReportLayoutDTO payload. Fail-Fast enforced.',
      );
    }
    final titleRaw = json['title'];
    final descRaw = json['description'];
    final showTextRaw = json['show_text'];

    return ReportLayoutDTO(
      presetView: preset,
      matrixType: json['matrix_type']?.toString(),
      title: Map<String, String>.from(
        (titleRaw is Map ? titleRaw : {}).map(
          (k, v) => MapEntry(k.toString(), v.toString()),
        ),
      ),
      description: Map<String, String>.from(
        (descRaw is Map ? descRaw : {}).map(
          (k, v) => MapEntry(k.toString(), v.toString()),
        ),
      ),
      axes: (json['axes'] as List)
          .map(
            (e) => ReportAxisDTO.fromJson(
              e is Map ? e as Map<String, dynamic> : <String, dynamic>{},
            ),
          )
          .toList(),
      showText: showTextRaw is bool
          ? showTextRaw
          : (showTextRaw?.toString() != 'false'),
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

  /// Explicit parsing — Graceful Degradation (§6.3).
  factory MCPToolAuditDTO.fromJson(Map<String, dynamic> json) {
    final urlsRaw = json['source_urls'];
    return MCPToolAuditDTO(
      toolId: json['tool_id'] as String,
      stepName: json['step_name'] as String,
      query: json['query'] as String,
      responseSummary: json['response_summary']?.toString() ?? '',
      sourceUrls: (urlsRaw is List ? urlsRaw : [])
          .map((e) => e.toString())
          .toList(),
      timestamp: json['timestamp']?.toString(),
      durationMs: (json['duration_ms'] as num?)?.toInt() ?? 0,
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
      throw const FormatException(
        'CRITICAL: layouts field is missing or invalid in ReportDataDTO payload. Fail-Fast enforced.',
      );
    }

    final availRaw = json['available_profiles'];
    final mcpAuditRaw = json['mcp_tool_audit'];

    return ReportDataDTO(
      workflowId: json['workflow_id'] as String,
      profileId: json['profile_id'] as String,
      profileName: json['profile_name'] as Map<String, dynamic>,
      availableProfiles: Map<String, String>.from(
        (availRaw is Map ? availRaw : {}).map(
          (k, v) => MapEntry(k.toString(), v.toString()),
        ),
      ),
      globalScore: (json['global_score'] as num?)?.toDouble(),
      layouts: (json['layouts'] as List)
          .map(
            (e) => ReportLayoutDTO.fromJson(
              e is Map ? e as Map<String, dynamic> : <String, dynamic>{},
            ),
          )
          .toList(),
      createdAt: json['created_at']?.toString(),
      orgName: json['org_name']?.toString(),
      costEstimate: (json['cost_estimate'] as num?)?.toDouble(),
      totalTokens: (json['total_tokens'] as num?)?.toInt(),
      promptTokens: (json['prompt_tokens'] as num?)?.toInt(),
      completionTokens: (json['completion_tokens'] as num?)?.toInt(),
      reasoningTokens: (json['reasoning_tokens'] as num?)?.toInt(),
      mcpToolAudit: mcpAuditRaw is List
          ? mcpAuditRaw
                .map(
                  (e) => MCPToolAuditDTO.fromJson(
                    e is Map ? e as Map<String, dynamic> : <String, dynamic>{},
                  ),
                )
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
