import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';

/// Renders the XAI Evidence Box — clickable source URLs from MCP Tool Loop searches.
/// Follows Flat MVC (§5): Zero logic, pure data mapping from McpAuditTraceDto.
/// Only renders if audit traces are non-empty (zero visual clutter for non-MCP workflows).
class XAIEvidenceBox extends ConsumerWidget {
  final List<McpAuditTraceDto> traces;

  const XAIEvidenceBox({super.key, required this.traces});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (traces.isEmpty) return const SizedBox();

    final l10n = AppLocalizations.of(context)!;

    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ExpansionTile(
        initiallyExpanded: true,
        leading: Icon(Icons.fact_check, color: Colors.teal.shade700),
        title: Text(
          l10n.xaiEvidenceTitle,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Colors.teal.shade800,
          ),
        ),
        children: [
          const Divider(height: 1),
          ...traces.asMap().entries.map((entry) {
            final index = entry.key;
            final audit = entry.value;
            return _buildAuditEntry(context, ref, audit, index);
          }),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildAuditEntry(
    BuildContext context,
    WidgetRef ref,
    McpAuditTraceDto audit,
    int index,
  ) {
    final l10n = AppLocalizations.of(context)!;

    try {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (audit.claimText != null && audit.claimText!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Text.rich(
                  TextSpan(
                    children: [
                      TextSpan(
                        text: '${l10n.xaiEvidenceClaim}: ',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.teal.shade800,
                        ),
                      ),
                      TextSpan(
                        text: '"${audit.claimText}"',
                        style: TextStyle(
                          fontSize: 14,
                          fontStyle: FontStyle.italic,
                          color: Colors.grey.shade900,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            // Query row with duration badge
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.search, size: 18, color: Colors.grey.shade600),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        margin: const EdgeInsets.only(bottom: 4),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: Colors.blue.shade200),
                        ),
                        child: Text(
                          audit.toolId,
                          style: TextStyle(
                            fontSize: 10,
                            color: Colors.blue.shade800,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                      Text(
                        '${l10n.xaiEvidenceQuery}: "${audit.query}"',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '${l10n.xaiEvidenceDuration}: ${audit.durationMs}ms',
                    style: TextStyle(fontSize: 11, color: Colors.grey.shade700),
                  ),
                ),
              ],
            ),

            // Reasoning (Language specific LLM explanation)
            if (audit.reasoning.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8, left: 26),
                child: Text.rich(
                  TextSpan(
                    children: [
                      TextSpan(
                        text: '${l10n.xaiEvidenceReasoning}: ',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: Colors.teal.shade800,
                        ),
                      ),
                      TextSpan(
                        text: audit.reasoning,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey.shade900,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // Summary (if present) - Raw tool response
            if (audit.responseSummary.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8, left: 26),
                child: Text(
                  audit.responseSummary,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade700,
                    fontStyle: FontStyle.italic,
                    height: 1.4,
                  ),
                ),
              ),

            // Impacted Axes (if present)
            if (audit.impactedAxisNames.isNotEmpty) ...[
              Padding(
                padding: const EdgeInsets.only(top: 8, left: 26),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(
                        Icons.auto_awesome,
                        size: 14,
                        color: Colors.green.shade700,
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text.rich(
                          TextSpan(
                            children: [
                              TextSpan(
                                text: '${l10n.xaiEvidenceImpactedAxes} ',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.green.shade800,
                                ),
                              ),
                              TextSpan(
                                text: audit.impactedAxisNames.join(', '),
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.green.shade900,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],

            // Source URLs as clickable chips
            if (audit.sourceUrls.isNotEmpty) ...[
              Padding(
                padding: const EdgeInsets.only(top: 8, left: 26),
                child: Text(
                  l10n.xaiEvidenceSources,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.teal.shade600,
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.only(top: 4, left: 26),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: audit.sourceUrls.map((url) {
                    return ActionChip(
                      avatar: const Icon(
                        Icons.link,
                        size: 14,
                        color: Colors.blue,
                      ),
                      label: Text(
                        _truncateUrl(url),
                        style: const TextStyle(
                          fontSize: 11,
                          color: Colors.blue,
                        ),
                      ),
                      onPressed: () => _launchUrl(url, ref),
                      backgroundColor: Colors.blue.withValues(alpha: 0.08),
                      side: BorderSide(
                        color: Colors.blue.withValues(alpha: 0.2),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],

            if (index < traces.length - 1) const Divider(height: 24),
          ],
        ),
      );
    } catch (e, st) {
      // Diagnostic Node (§6.3): Fail loudly instead of hiding corruption
      ref
          .read(loggerServiceProvider)
          .error(
            'XAIEvidenceBox',
            'VALIDATION_FAILED: Failed to render audit entry',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  /// Truncate URL for chip display (domain + first path segment).
  String _truncateUrl(String url) {
    try {
      final uri = Uri.parse(url);
      final pathSegments = uri.pathSegments;
      if (pathSegments.isEmpty) return uri.host;
      return '${uri.host}/${pathSegments.first}...';
    } catch (_) {
      return url.length > 40 ? '${url.substring(0, 40)}...' : url;
    }
  }

  Future<void> _launchUrl(String url, WidgetRef ref) async {
    try {
      final uri = Uri.parse(url);
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        ref
            .read(loggerServiceProvider)
            .error('XAIEvidenceBox', 'Could not launch URL: $url', null, null);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('XAIEvidenceBox', 'URL launch error: $e', e, st);
      throw AppException.network(
        'URL launch error: $e',
      ).copyWith(extensions: {'url': url});
    }
  }
}
