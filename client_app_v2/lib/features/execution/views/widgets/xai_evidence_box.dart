import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:client_app/features/execution/models/report_data_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Renders the XAI Evidence Box — clickable source URLs from MCP Tool Loop searches.
/// Follows Flat MVC (§5): Zero logic, pure data mapping from MCPToolAuditDTO.
/// Only renders if audit traces are non-empty (zero visual clutter for non-MCP workflows).
class XAIEvidenceBox extends ConsumerWidget {
  final List<MCPToolAuditDTO> auditTraces;

  const XAIEvidenceBox({super.key, required this.auditTraces});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (auditTraces.isEmpty) return const SizedBox.shrink();

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
          ...auditTraces.asMap().entries.map((entry) {
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
    MCPToolAuditDTO audit,
    int index,
  ) {
    final l10n = AppLocalizations.of(context)!;

    try {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Query row with duration badge
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.search, size: 18, color: Colors.grey.shade600),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${l10n.xaiEvidenceQuery}: "${audit.query}"',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
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
                    style: TextStyle(
                      fontSize: 11,
                      color: Colors.grey.shade700,
                    ),
                  ),
                ),
              ],
            ),

            // Summary (if present)
            if (audit.responseSummary.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8, left: 26),
                child: Text(
                  audit.responseSummary,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade800,
                    height: 1.4,
                  ),
                ),
              ),

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
                  children:
                      audit.sourceUrls.map((url) {
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

            if (index < auditTraces.length - 1)
              const Divider(height: 24),
          ],
        ),
      );
    } catch (e, st) {
      // Graceful Degradation (§6.3): render failure does not crash the report
      ref
          .read(loggerServiceProvider)
          .error(
            'XAIEvidenceBox',
            'VALIDATION_FAILED: Failed to render audit entry',
            e,
            st,
          );
      return const SizedBox.shrink();
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
    }
  }
}
