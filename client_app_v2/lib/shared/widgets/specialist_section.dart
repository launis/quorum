import 'dart:convert';
import 'dart:io';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/shared/widgets/unified_metric_gauge.dart';
import 'package:client_app/theme/app_colors.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class SpecialistSection extends ConsumerStatefulWidget {
  final String title;
  final String type;
  final Map<String, Object?> data;
  final Map<String, Object?>? metrics;

  const SpecialistSection({
    super.key,
    required this.title,
    required this.type,
    required this.data,
    this.metrics,
  });

  @override
  ConsumerState<SpecialistSection> createState() => _SpecialistSectionState();
}

class _SpecialistSectionState extends ConsumerState<SpecialistSection> {
  static const double _desktopBreakpoint = 800.0;
  static const double _logicThreshold = 3.0;
  static const double _strategicMaxScore = 4.0;
  static const double _bloomMaxScore = 6.0;
  static const double _toulminMaxScore = 6.0;
  static const double _fidelityMaxScore = 3.0;
  static const double _abductiveMaxScore = 3.0;
  static const double _authenticityMaxScore = 3.0;
  static const double _complianceMaxScore = 5.0;
  static const double _baseBubbleSize = 12.0;
  static const double _bubbleScaleMultiplier = 4.0;
  static const double _spectrumLineTop = 10.0;
  static const double _spectrumLineHorizontalInset = 30.0;
  static const double _spectrumTrackHeight = 4.0;
  static const double _spectrumNodeDimension = 24.0;
  static const double _spectrumBorderWidth = 3.0;
  static const double _infoIconSize = 32.0;
  static const double _helpIconSize = 18.0;
  static const double _chipIconSize = 14.0;
  static const double _defaultBorderWidth = 1.0;

  bool _showRaw = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    if (widget.title.trim().isEmpty) {
      final err = AppException.validation(
        'Fail-Fast: SpecialistSection title cannot be empty.',
      );
      ref
          .read(loggerServiceProvider)
          .error(
            'SpecialistSection',
            'VALIDATION_FAILED: SpecialistSection title cannot be empty',
            err,
          );
      return ErrorView(error: err, compact: true);
    }

    if (widget.type.trim().isEmpty) {
      final err = AppException.validation(
        'Fail-Fast: SpecialistSection type cannot be empty.',
      );
      ref
          .read(loggerServiceProvider)
          .error(
            'SpecialistSection',
            'VALIDATION_FAILED: SpecialistSection type cannot be empty',
            err,
          );
      return ErrorView(error: err, compact: true);
    }

    return Card(
      elevation: AppSpacing.s2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Semantics(
        excludeSemantics: Platform.isWindows,
        child: ExpansionTile(
          leading: _buildIconForType(context),
          title: Text(
            widget.title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          subtitle: Text(
            _getSubtitleForType(l10n),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: textTheme.bodySmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
          ),
          childrenPadding: AppSpacing.p16,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Flexible(
                  child: TextButton.icon(
                    onPressed: () {
                      setState(() {
                        _showRaw = !_showRaw;
                      });
                    },
                    icon: Icon(
                      _showRaw ? Icons.visibility_off : Icons.code,
                      size: AppSpacing.s16,
                    ),
                    label: Text(
                      _showRaw ? l10n.btnHideRawData : l10n.btnShowJson,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.bodySmall,
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.copy, size: AppSpacing.s16),
                  onPressed: () {
                    final jsonStr = const JsonEncoder.withIndent(
                      '  ',
                    ).convert(widget.data);
                    Clipboard.setData(ClipboardData(text: jsonStr));
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(l10n.msgJsonCopied),
                        duration: AppDurations.slow,
                      ),
                    );
                  },
                  tooltip: l10n.copyToClipboard,
                ),
              ],
            ),
            const Divider(),
            AnimatedCrossFade(
              firstChild: _buildSummaryView(context),
              secondChild: _buildRawJsonView(context),
              crossFadeState: _showRaw
                  ? CrossFadeState.showSecond
                  : CrossFadeState.showFirst,
              duration: AppDurations.standard,
            ),
          ],
        ),
      ),
    );
  }

  Icon _buildIconForType(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return switch (widget.type) {
      'logic-analysis' ||
      'LOGIC_ANALYSIS' => Icon(Icons.psychology, color: colorScheme.primary),
      'stress-test' ||
      'STRESS_TEST' => Icon(Icons.fitness_center, color: colorScheme.error),
      'causal-analysis' || 'CAUSAL_ANALYSIS' => Icon(
        Icons.compare_arrows,
        color: colorScheme.secondary,
      ),
      'performativity-check' || 'PERFORMATIVITY_CHECK' => Icon(
        Icons.theater_comedy,
        color: colorScheme.tertiary,
      ),
      'fact-check' ||
      'FACT_CHECK' ||
      'fact-check-grid' ||
      'FACT_CHECK_GRID' => Icon(Icons.fact_check, color: colorScheme.primary),
      'profiler-analysis' ||
      'PROFILER_ANALYSIS' => Icon(Icons.face, color: colorScheme.secondary),
      'archivist-check' || 'ARCHIVIST_CHECK' => Icon(
        Icons.gavel,
        color: colorScheme.onSurfaceVariant,
      ),
      _ => Icon(Icons.extension, color: colorScheme.onSurfaceVariant),
    };
  }

  String _getSubtitleForType(AppLocalizations l10n) {
    return switch (widget.type) {
      'logic-analysis' || 'LOGIC_ANALYSIS' => l10n.subLogicAnalysis,
      'stress-test' || 'STRESS_TEST' => l10n.subStressTest,
      'causal-analysis' || 'CAUSAL_ANALYSIS' => l10n.subCausalAnalysis,
      'performativity-check' ||
      'PERFORMATIVITY_CHECK' => l10n.subPerformativityCheck,
      'fact-check' ||
      'FACT_CHECK' ||
      'fact-check-grid' ||
      'FACT_CHECK_GRID' => l10n.subFactCheck,
      'profiler-analysis' || 'PROFILER_ANALYSIS' => l10n.subProfilerAnalysis,
      'archivist-check' || 'ARCHIVIST_CHECK' => l10n.subArchivistCheck,
      _ => '',
    };
  }

  void _validateRequiredKeys(List<String> keys, String contextName) {
    final missing = keys.where((k) => widget.data[k] == null).toList();
    if (missing.isNotEmpty) {
      final msg =
          'Fail-Fast: Missing required keys in $contextName: ${missing.join(', ')}';
      throw AppException.validation(msg);
    }
  }

  Widget _buildSummaryView(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    if (widget.data.isEmpty) {
      return Padding(
        padding: AppSpacing.p8,
        child: Text(
          l10n.dataUnavailable,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontStyle: FontStyle.italic,
          ),
        ),
      );
    }

    try {
      return switch (widget.type) {
        'logic-analysis' || 'LOGIC_ANALYSIS' => _buildLogicAnalysis(context),
        'stress-test' || 'STRESS_TEST' => _buildStressTest(context),
        'causal-analysis' || 'CAUSAL_ANALYSIS' => _buildCausalAnalysis(context),
        'profiler-analysis' ||
        'PROFILER_ANALYSIS' => _buildProfilerAnalysis(context),
        'fact-check' ||
        'FACT_CHECK' ||
        'fact-check-grid' ||
        'FACT_CHECK_GRID' => _buildFactCheck(context),
        'performativity-check' ||
        'PERFORMATIVITY_CHECK' => _buildPerformativityCheck(context),
        'archivist-check' || 'ARCHIVIST_CHECK' => _buildArchivistCheck(context),
        'driver-profile' ||
        'DRIVER_PROFILE' ||
        'interaction-grid' ||
        'INTERACTION_GRID' => _buildDriverProfile(context),
        'security-check' || 'SECURITY_CHECK' => _buildSecurityCheck(context),
        _ => _buildGenericMap(context, widget.data),
      };
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'SpecialistSection',
            'VALIDATION_FAILED: UI Graceful Degradation [${widget.type}]: $e',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  Widget _buildResponsiveLayout(
    BuildContext context, {
    required Widget leftContent,
    required Widget rightContent,
    int leftFlex = 5,
    int rightFlex = 5,
    bool mobileReverse = false,
  }) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > _desktopBreakpoint) {
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(flex: leftFlex, child: leftContent),
              AppSpacing.w16,
              Expanded(flex: rightFlex, child: rightContent),
            ],
          );
        } else {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: mobileReverse
                ? [rightContent, AppSpacing.h16, leftContent]
                : [leftContent, AppSpacing.h16, rightContent],
          );
        }
      },
    );
  }

  String _getLocalizedEnum(String? key, AppLocalizations l10n) {
    if (key == null) return l10n.dataUnavailable;
    return switch (key) {
      'SEC_THREAT_DETECTED' => l10n.secThreatDetected,
      'SEC_THREAT_NONE' => l10n.secThreatNone,
      'SEC_ANONYMIZED' => l10n.secAnonymized,
      'SEC_NOT_ANONYMIZED' => l10n.secNotAnonymized,
      'RISK_HIGH' => l10n.riskHigh,
      'RISK_MEDIUM' => l10n.riskMedium,
      'RISK_LOW' => l10n.riskLow,
      'RISK_UNKNOWN' => l10n.riskUnknown,
      'BIAS_DETECTED' => l10n.biasDetected,
      'BIAS_NONE' => l10n.biasNone,
      'GAP_DETECTED' => l10n.gapDetected,
      'GAP_NONE' => l10n.gapNone,
      'ROLE_PASSENGER' => l10n.rolePassenger,
      'ROLE_NAVIGATOR' => l10n.roleNavigator,
      'ROLE_DRIVER' => l10n.roleDriver,
      'ROLE_ARCHITECT' => l10n.roleArchitect,
      'VER_VERIFIED' => l10n.verVerified,
      'VER_DEBUNKED' => l10n.verDebunked,
      'VER_UNCERTAIN' => l10n.verUncertain,
      'AUTH_ORGANIC' => l10n.authOrganic,
      'AUTH_PERFORMATIVE' => l10n.authPerformative,
      'AUTH_UNKNOWN' => l10n.authUnknown,
      'BLOOM_REMEMBERING' => l10n.bloomRemembering,
      'BLOOM_UNDERSTANDING' => l10n.bloomUnderstanding,
      'BLOOM_APPLYING' => l10n.bloomApplying,
      'BLOOM_ANALYZING' => l10n.bloomAnalyzing,
      'BLOOM_EVALUATING' => l10n.bloomEvaluating,
      'BLOOM_CREATING' => l10n.bloomCreating,
      'STRAT_LOW' => l10n.stratLow,
      'STRAT_MEDIUM' => l10n.stratMedium,
      'STRAT_HIGH' => l10n.stratHigh,
      'STRAT_VISIONARY' => l10n.stratVisionary,
      _ => key,
    };
  }

  Widget _buildLogicMatrix(
    BuildContext context,
    double toulmin,
    double bloom,
    double strat,
    AppLocalizations l10n,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final bool isStrongToulmin = toulmin >= _logicThreshold;
    final bool isHighBloom = bloom >= _logicThreshold;
    final helpBtn = _buildHelpButton(context, 'logicMatrix');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Icon(Icons.grid_view, color: colorScheme.secondary),
            AppSpacing.w8,
            Expanded(
              child: Text(
                l10n.logicMatrixTitle,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            ?helpBtn,
          ],
        ),
        AppSpacing.h16,
        Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: _buildQuadrant(
                    context,
                    l10n.logicMatrixQ2Title,
                    l10n.logicMatrixQ2Desc,
                    !isStrongToulmin && isHighBloom,
                    strat,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: _buildQuadrant(
                    context,
                    l10n.logicMatrixQ1Title,
                    l10n.logicMatrixQ1Desc,
                    isStrongToulmin && isHighBloom,
                    strat,
                  ),
                ),
              ],
            ),
            AppSpacing.h8,
            Row(
              children: [
                Expanded(
                  child: _buildQuadrant(
                    context,
                    l10n.logicMatrixQ4Title,
                    l10n.logicMatrixQ4Desc,
                    !isStrongToulmin && !isHighBloom,
                    strat,
                  ),
                ),
                AppSpacing.w8,
                Expanded(
                  child: _buildQuadrant(
                    context,
                    l10n.logicMatrixQ3Title,
                    l10n.logicMatrixQ3Desc,
                    isStrongToulmin && !isHighBloom,
                    strat,
                  ),
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuadrant(
    BuildContext context,
    String title,
    String desc,
    bool isActive,
    double strat,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final double bubbleSize = isActive
        ? _baseBubbleSize + (strat * _bubbleScaleMultiplier)
        : 0.0;

    return Container(
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: isActive
            ? colorScheme.primaryContainer
            : colorScheme.surfaceContainerLowest,
        border: Border.all(
          color: isActive
              ? colorScheme.primary
              : colorScheme.surfaceContainerHighest,
          width: isActive ? AppSpacing.s2 : _defaultBorderWidth,
        ),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: textTheme.bodySmall?.copyWith(
                    fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                    color: isActive
                        ? colorScheme.onPrimaryContainer
                        : colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
              if (isActive) ...[
                AppSpacing.w4,
                Container(
                  width: bubbleSize,
                  height: bubbleSize,
                  decoration: BoxDecoration(
                    color: colorScheme.primary,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ],
          ),
          AppSpacing.h4,
          Text(
            desc,
            style: textTheme.labelSmall?.copyWith(
              color: isActive
                  ? colorScheme.onPrimaryContainer
                  : colorScheme.onSurfaceVariant,
              height: 1.3,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLogicAnalysis(BuildContext context) {
    _validateRequiredKeys([
      'bloom_score',
      'strategic_score',
      'arguments',
    ], 'LOGIC_ANALYSIS');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final rawArgs = widget.data['arguments'];
    if (rawArgs is! List) {
      throw AppException.validation(
        'Fail-Fast: LOGIC_ANALYSIS arguments must be a List.',
      );
    }
    final arguments = <Map<String, Object?>>[];
    for (var i = 0; i < rawArgs.length; i++) {
      final item = rawArgs[i];
      if (item is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: LOGIC_ANALYSIS argument[$i] must be a Map<String, Object?>.',
        );
      }
      arguments.add(item);
    }

    final methodology =
        widget.data['methodological_log']?.toString() ??
        widget.data['metodologinen_loki']?.toString();

    final List<Widget> children = [];

    if (methodology != null) {
      children.add(
        _buildInfoCard(
          context,
          l10n.lblMethodologicalLog,
          methodology,
          Icons.history_edu,
          helpKey: 'metodologia',
        ),
      );
      children.add(AppSpacing.h16);
    }

    final currentMetrics = widget.metrics;
    if (currentMetrics != null && currentMetrics.isNotEmpty) {
      children.add(_buildCompactTextMetrics(context, currentMetrics));
      children.add(AppSpacing.h16);
    }

    final stratScore = _parseNumericScore(
      widget.data['strategic_score'],
      'strategic_score',
      maxBound: _strategicMaxScore,
    );
    final stratDisplay =
        '${stratScore.toStringAsFixed(1)}/${_strategicMaxScore.toStringAsFixed(1)}';
    final stratGauge = UnifiedMetricGauge(
      label: l10n.lblStrategicDepth,
      value: stratScore,
      max: _strategicMaxScore,
      description:
          widget.data['strategic_help']?.toString() ?? l10n.helpStrategicDepth,
      displayValue: stratDisplay,
      color: colorScheme.secondary,
      axisLabels: [
        l10n.stratLow,
        l10n.stratMedium,
        l10n.stratHigh,
        l10n.stratVisionary,
      ],
      isOrdinal: true,
    );

    final bloomScore = _parseNumericScore(
      widget.data['bloom_score'],
      'bloom_score',
      maxBound: _bloomMaxScore,
    );
    final bloomDisplay =
        '${bloomScore.toStringAsFixed(1)}/${_bloomMaxScore.toStringAsFixed(1)}';

    final bloomGauge = UnifiedMetricGauge(
      label: l10n.lblBloomScore,
      value: bloomScore,
      max: _bloomMaxScore,
      description: widget.data['bloom_help']?.toString() ?? l10n.helpBloom,
      displayValue: bloomDisplay,
      color: colorScheme.secondary,
      axisLabels: [
        l10n.bloomRemembering,
        l10n.bloomUnderstanding,
        l10n.bloomApplying,
        l10n.bloomAnalyzing,
        l10n.bloomEvaluating,
        l10n.bloomCreating,
      ],
      isOrdinal: true,
    );

    final toulminScore = widget.data['toulmin_score'] != null
        ? _parseNumericScore(
            widget.data['toulmin_score'],
            'toulmin_score',
            maxBound: _toulminMaxScore,
          )
        : 0.0;
    final toulminGauge = UnifiedMetricGauge(
      label: l10n.lblToulminScore,
      value: toulminScore,
      max: _toulminMaxScore,
      description: widget.data['toulmin_help']?.toString() ?? l10n.helpToulmin,
      displayValue:
          '${toulminScore.toStringAsFixed(1)}/${_toulminMaxScore.toStringAsFixed(1)}',
      color: colorScheme.primary,
      axisLabels: [l10n.lblClaim, '', l10n.lblData, '', l10n.lblBacking, ''],
      isOrdinal: true,
    );

    children.add(
      _buildLogicMatrix(context, toulminScore, bloomScore, stratScore, l10n),
    );
    children.add(AppSpacing.h24);

    children.add(
      Card(
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s8),
          side: BorderSide(color: colorScheme.secondary.withValues(alpha: 0.3)),
        ),
        color: colorScheme.secondaryContainer.withValues(alpha: 0.3),
        child: Padding(
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              bloomGauge,
              const Padding(
                padding: EdgeInsets.symmetric(vertical: AppSpacing.s16),
                child: Divider(height: _defaultBorderWidth),
              ),
              stratGauge,
              const Padding(
                padding: EdgeInsets.symmetric(vertical: AppSpacing.s16),
                child: Divider(height: _defaultBorderWidth),
              ),
              toulminGauge,
            ],
          ),
        ),
      ),
    );

    children.add(AppSpacing.h24);

    if (arguments.isNotEmpty) {
      final toulminHelp = _buildHelpButton(context, 'toulmin');
      final List<Widget> toulminChildren = [
        Row(
          children: [
            Expanded(
              child: Text(
                l10n.lblArguments,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            ?toulminHelp,
          ],
        ),
        AppSpacing.h8,
      ];

      toulminChildren.addAll(
        arguments.map<Widget>(
          (t) => Card(
            margin: const EdgeInsets.only(bottom: AppSpacing.s8),
            color: colorScheme.surfaceContainerLow,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppSpacing.s4),
              side: BorderSide(
                color: colorScheme.primary.withValues(alpha: 0.2),
              ),
            ),
            child: Padding(
              padding: AppSpacing.p12,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildLabelValue(context, l10n.lblClaim, t['claim']),
                  AppSpacing.h4,
                  const Divider(),
                  AppSpacing.h4,
                  if (t['data'] != null) ...[
                    _buildLabelValue(context, l10n.lblData, t['data']),
                    AppSpacing.h4,
                  ],
                  _buildLabelValue(context, l10n.lblWarrant, t['warrant']),
                  if (t['backing'] != null) ...[
                    AppSpacing.h4,
                    _buildLabelValue(context, l10n.lblBacking, t['backing']),
                  ],
                  if (t['rebuttal'] != null) ...[
                    AppSpacing.h4,
                    _buildLabelValue(context, l10n.lblRebuttal, t['rebuttal']),
                  ],
                  if (t['qualifier'] != null) ...[
                    AppSpacing.h4,
                    _buildLabelValue(
                      context,
                      l10n.lblQualifier,
                      t['qualifier'],
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      );
      children.add(
        Container(
          padding: AppSpacing.p16,
          decoration: BoxDecoration(
            border: Border.all(color: colorScheme.surfaceContainerHighest),
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: toulminChildren,
          ),
        ),
      );
    } else {
      children.add(
        Padding(
          padding: AppSpacing.p16,
          child: Text(
            l10n.dataUnavailable,
            style: textTheme.bodyMedium?.copyWith(fontStyle: FontStyle.italic),
          ),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
  }

  Widget _buildSecurityCheck(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final semanticColors = context.semanticColors;
    final l10n = AppLocalizations.of(context)!;

    final threat = widget.data['threat_detected'] == true;
    final threatLabel =
        widget.data['threat_label']?.toString() ??
        (threat ? l10n.secThreatDetected : l10n.secThreatNone);

    final riskLabel = widget.data['risk_label']?.toString() ?? l10n.riskUnknown;

    final rColorStr = widget.data['risk_color']?.toString();
    final Color riskColor;
    final IconData riskIcon;
    if (rColorStr == 'red') {
      riskColor = colorScheme.error;
      riskIcon = Icons.gpp_bad;
    } else if (rColorStr == 'orange') {
      riskColor = semanticColors.warning;
      riskIcon = Icons.warning_amber;
    } else if (rColorStr == 'green') {
      riskColor = colorScheme.primary;
      riskIcon = Icons.check_circle;
    } else {
      riskColor = colorScheme.onSurfaceVariant;
      riskIcon = Icons.help_outline;
    }

    final anonymized = widget.data['anonymized'] == true;
    final anonLabel =
        widget.data['anonymized_label']?.toString() ??
        (anonymized ? l10n.secAnonymized : l10n.secNotAnonymized);

    final rawFindings = widget.data['findings'] ?? widget.data['loydokset'];
    final findings = rawFindings is List
        ? rawFindings.map((e) => e.toString()).toList()
        : <String>[];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: AppSpacing.s8,
          runSpacing: AppSpacing.s8,
          children: [
            _buildStatusChip(
              context,
              label: threatLabel,
              color: threat ? colorScheme.error : colorScheme.primary,
              icon: threat ? Icons.warning : Icons.check,
            ),
            _buildStatusChip(
              context,
              label: '${l10n.lblRiskLevel}: $riskLabel',
              color: riskColor,
              icon: riskIcon,
            ),
            _buildStatusChip(
              context,
              label: anonLabel,
              color: anonymized
                  ? colorScheme.primary
                  : colorScheme.onSurfaceVariant,
              icon: anonymized ? Icons.visibility_off : Icons.visibility,
            ),
          ],
        ),
        AppSpacing.h16,
        if (findings.isNotEmpty) ...[
          Text(
            '${l10n.lblFindings}:',
            style: textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: colorScheme.onSurfaceVariant,
            ),
          ),
          AppSpacing.h4,
          ...findings.map(
            (f) => Padding(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.s2),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: AppSpacing.s2),
                    child: Icon(
                      Icons.arrow_right,
                      size: AppSpacing.s16,
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                  Expanded(child: Text(f, style: textTheme.bodySmall)),
                ],
              ),
            ),
          ),
        ] else
          Text(
            l10n.lblNoSignificantFindings,
            style: textTheme.bodySmall?.copyWith(
              fontStyle: FontStyle.italic,
              color: colorScheme.onSurfaceVariant,
            ),
          ),
      ],
    );
  }

  Widget _buildStatusChip(
    BuildContext context, {
    required String label,
    required Color color,
    required IconData icon,
  }) {
    final textTheme = Theme.of(context).textTheme;
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s8,
        vertical: AppSpacing.s4,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(AppSpacing.s16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: _chipIconSize, color: color),
          AppSpacing.w4,
          Flexible(
            child: Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: textTheme.labelSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStressTest(BuildContext context) {
    _validateRequiredKeys(['findings', 'fidelity_audit'], 'STRESS_TEST');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final rawFindings = widget.data['findings'];
    if (rawFindings is! List) {
      throw AppException.validation(
        'Fail-Fast: STRESS_TEST findings must be a List.',
      );
    }
    final findings = <Map<String, Object?>>[];
    for (var i = 0; i < rawFindings.length; i++) {
      final item = rawFindings[i];
      if (item is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: STRESS_TEST finding[$i] must be a Map<String, Object?>.',
        );
      }
      findings.add(item);
    }

    final rawFidelity = widget.data['fidelity_audit'];
    if (rawFidelity is! Map<String, Object?>) {
      throw AppException.validation(
        'Fail-Fast: STRESS_TEST fidelity_audit must be a Map<String, Object?>.',
      );
    }
    final fidelity = rawFidelity;

    final leftChildren = <Widget>[];
    if (fidelity.isNotEmpty) {
      final fidelityDisplay = fidelity['fidelity_score_display']?.toString();
      final double scoreVal;
      if (fidelity['fidelity_score'] != null) {
        scoreVal = _parseNumericScore(
          fidelity['fidelity_score'],
          'fidelity_score',
          maxBound: _fidelityMaxScore,
        );
      } else if (fidelityDisplay != null && fidelityDisplay.isNotEmpty) {
        scoreVal = _parseNumericScore(
          fidelityDisplay.split('/').first,
          'fidelity_score_display',
          maxBound: _fidelityMaxScore,
        );
      } else {
        scoreVal = 0.0;
      }

      leftChildren.add(
        Container(
          padding: AppSpacing.p16,
          decoration: BoxDecoration(
            color: colorScheme.errorContainer.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              UnifiedMetricGauge(
                label: l10n.lblFidelity,
                value: scoreVal,
                max: _fidelityMaxScore,
                description:
                    widget.data['fidelity_help']?.toString() ??
                    l10n.helpFidelity,
                displayValue: fidelityDisplay != null
                    ? '$fidelityDisplay/${_fidelityMaxScore.toStringAsFixed(1)}'
                    : '${scoreVal.toStringAsFixed(1)}/${_fidelityMaxScore.toStringAsFixed(1)}',
                color: colorScheme.error,
                axisLabels: [l10n.lblWeak, l10n.lblModerate, l10n.lblStrong],
              ),
              AppSpacing.h12,
              Text(
                fidelity['post_hoc_rationalization_suspected'] == true
                    ? l10n.lblPostHocWarning
                    : l10n.lblNoRationalization,
                style: textTheme.bodyMedium?.copyWith(
                  color: fidelity['post_hoc_rationalization_suspected'] == true
                      ? colorScheme.error
                      : colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              AppSpacing.h12,
              _buildLabelValue(
                context,
                l10n.lblPostHocRationalization,
                fidelity['post_hoc_rationalization_suspected']?.toString(),
              ),
              AppSpacing.h4,
              _buildLabelValue(
                context,
                l10n.lblReasoning,
                fidelity['reasoning'] ?? '-',
              ),
            ],
          ),
        ),
      );
    }

    final rightChildren = <Widget>[
      for (final f in findings)
        Card(
          margin: const EdgeInsets.only(bottom: AppSpacing.s8),
          color: f['is_held'] == true
              ? colorScheme.primaryContainer
              : colorScheme.errorContainer,
          child: Padding(
            padding: AppSpacing.p12,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLabelValue(context, l10n.lblQuestion, f['question']),
                AppSpacing.h4,
                _buildLabelValue(
                  context,
                  l10n.lblEvidenceHeld,
                  f['is_held']?.toString(),
                ),
                AppSpacing.h4,
                _buildLabelValue(
                  context,
                  l10n.lblObservation,
                  f['observation'],
                ),
              ],
            ),
          ),
        ),
    ];

    return _buildResponsiveLayout(
      context,
      leftContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: leftChildren,
      ),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: rightChildren,
      ),
      leftFlex: 4,
      rightFlex: 6,
    );
  }

  Widget _buildCausalAnalysis(BuildContext context) {
    _validateRequiredKeys([
      'abductive_score',
      'observation',
      'counterfactual_actual',
      'counterfactual_simulated',
    ], 'CAUSAL_ANALYSIS');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final abductive = widget.data['abductive_conclusion']?.toString();
    final abductiveScore = _parseNumericScore(
      widget.data['abductive_score'],
      'abductive_score',
      maxBound: _abductiveMaxScore,
    );
    final observation = widget.data['observation']?.toString();
    final actualScenario = widget.data['counterfactual_actual']?.toString();
    final simulatedScenario = widget.data['counterfactual_simulated']
        ?.toString();
    final plausibilityScore = widget.data['plausibility_score'] != null
        ? _parseNumericScore(
            widget.data['plausibility_score'],
            'plausibility_score',
            maxBound: _abductiveMaxScore,
          )
        : null;

    final leftChildren = <Widget>[];
    if (abductive != null && abductive.trim().isNotEmpty) {
      leftChildren.add(
        Container(
          padding: AppSpacing.p12,
          decoration: BoxDecoration(
            color: colorScheme.secondaryContainer.withValues(alpha: 0.4),
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              UnifiedMetricGauge(
                label: l10n.lblAbductiveReasoning,
                value: abductiveScore,
                max: _abductiveMaxScore,
                description:
                    widget.data['abductive_help']?.toString() ??
                    l10n.helpAbductive,
                displayValue: widget.data['abductive_score_display'] != null
                    ? '${widget.data['abductive_score_display']}/${_abductiveMaxScore.toStringAsFixed(1)}'
                    : '${abductiveScore.toStringAsFixed(1)}/${_abductiveMaxScore.toStringAsFixed(1)}',
                color: colorScheme.secondary,
                axisLabels: [l10n.lblWeak, l10n.lblModerate, l10n.lblStrong],
              ),
              AppSpacing.h8,
              Text(abductive, style: textTheme.bodyMedium),
            ],
          ),
        ),
      );
      leftChildren.add(AppSpacing.h16);
    }

    if (observation != null) {
      if (observation.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: CAUSAL_ANALYSIS observation cannot be empty.',
        );
      }
      final causalHelp = _buildHelpButton(context, 'causal');
      leftChildren.add(
        Container(
          padding: AppSpacing.p16,
          decoration: BoxDecoration(
            color: colorScheme.secondaryContainer.withValues(alpha: 0.4),
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      l10n.lblCausalAudit,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  ?causalHelp,
                ],
              ),
              AppSpacing.h8,
              Text(observation, style: textTheme.bodyMedium),
            ],
          ),
        ),
      );
    }

    final rightChildren = <Widget>[];
    if (actualScenario != null && simulatedScenario != null) {
      rightChildren.add(
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.lblCounterfactualTest,
              style: textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            AppSpacing.h8,
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: _buildComparisonBlock(
                    context,
                    l10n.lblScenarioActual,
                    actualScenario,
                    colorScheme.surfaceContainerHighest,
                  ),
                ),
                AppSpacing.w8,
                const Icon(Icons.arrow_forward),
                AppSpacing.w8,
                Expanded(
                  child: _buildComparisonBlock(
                    context,
                    l10n.lblScenarioSimulation,
                    simulatedScenario,
                    colorScheme.secondaryContainer,
                  ),
                ),
              ],
            ),
            if (plausibilityScore != null)
              Padding(
                padding: const EdgeInsets.only(top: AppSpacing.s16),
                child: UnifiedMetricGauge(
                  label: l10n.lblCredibility,
                  value: plausibilityScore,
                  max: _abductiveMaxScore,
                  description:
                      widget.data['plausibility_help']?.toString() ??
                      l10n.plausibility_desc,
                  displayValue:
                      widget.data['plausibility_score_display']?.toString() ??
                      '${plausibilityScore.toStringAsFixed(1)}/${_abductiveMaxScore.toStringAsFixed(1)}',
                  color: colorScheme.secondary,
                  axisLabels: [l10n.lblWeak, '', l10n.lblStrong],
                ),
              ),
          ],
        ),
      );
    }

    return _buildResponsiveLayout(
      context,
      leftContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: leftChildren,
      ),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: rightChildren,
      ),
      leftFlex: 4,
      rightFlex: 6,
    );
  }

  Widget _buildProfilerAnalysis(BuildContext context) {
    _validateRequiredKeys([
      'word_count',
      'avg_sentence_length',
      'lexical_diversity',
    ], 'PROFILER_ANALYSIS');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final profile = widget.data['psychological_profile']?.toString();
    final intent = widget.data['intent_analysis']?.toString();

    final wordCount =
        widget.data['word_count_display']?.toString() ??
        widget.data['word_count']!.toString();
    final avgLength =
        widget.data['avg_sentence_length_display']?.toString() ??
        widget.data['avg_sentence_length']!.toString();
    final lexicalDiv =
        widget.data['lexical_diversity_display']?.toString() ??
        widget.data['lexical_diversity']!.toString();

    final profilerHelp = _buildHelpButton(context, 'profiler');
    final leftChildren = <Widget>[
      Row(
        children: [
          Expanded(
            child: Text(
              '${l10n.lblTextMetrics}:',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          ?profilerHelp,
        ],
      ),
      AppSpacing.h8,
      Wrap(
        spacing: AppSpacing.s16,
        runSpacing: AppSpacing.s16,
        children: [
          _buildMetricBlock(context, l10n.lblWordCount, wordCount),
          _buildMetricBlock(context, l10n.lblAvgSentenceLength, avgLength),
          _buildMetricBlock(context, l10n.lblLexicalDiversity, lexicalDiv),
        ],
      ),
    ];

    final rightChildren = <Widget>[];
    if (profile != null) {
      rightChildren.add(
        _buildInfoCard(
          context,
          l10n.lblPsychologicalProfile,
          profile,
          Icons.psychology,
        ),
      );
      rightChildren.add(AppSpacing.h8);
    }
    if (intent != null) {
      rightChildren.add(
        _buildInfoCard(
          context,
          l10n.lblAuthorIntent,
          intent,
          Icons.track_changes,
        ),
      );
    }

    final autoBiasLabel = widget.data['automation_bias_label']?.toString();
    final autoBiasColor = widget.data['automation_bias_color'] == 'red'
        ? colorScheme.error
        : colorScheme.primary;

    final sayDoLabel = widget.data['say_do_gap_label']?.toString();
    final sayDoColor = widget.data['say_do_gap_color'] == 'red'
        ? colorScheme.error
        : colorScheme.primary;

    if (autoBiasLabel != null || sayDoLabel != null) {
      leftChildren.add(AppSpacing.h16);
      leftChildren.add(
        Text(
          l10n.lblBehavioralIndicators,
          style: textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
      );
      leftChildren.add(AppSpacing.h8);
      leftChildren.add(
        Wrap(
          spacing: AppSpacing.s8,
          runSpacing: AppSpacing.s8,
          children: [
            if (autoBiasLabel != null)
              _buildStatusChip(
                context,
                label: l10n.lblAutomationBiasValue(
                  _getLocalizedEnum(autoBiasLabel, l10n),
                ),
                color: autoBiasColor,
                icon: autoBiasColor == colorScheme.error
                    ? Icons.warning
                    : Icons.check,
              ),
            if (sayDoLabel != null)
              _buildStatusChip(
                context,
                label: l10n.lblSayDoGapValue(
                  _getLocalizedEnum(sayDoLabel, l10n),
                ),
                color: sayDoColor,
                icon: sayDoColor == colorScheme.error
                    ? Icons.warning
                    : Icons.check,
              ),
          ],
        ),
      );
    }

    return _buildResponsiveLayout(
      context,
      leftContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: leftChildren,
      ),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: rightChildren,
      ),
      leftFlex: 4,
      rightFlex: 6,
    );
  }

  Widget _buildFactCheck(BuildContext context) {
    _validateRequiredKeys(['fact_checks', 'ethical_issues'], 'FACT_CHECK');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final rawFacts = widget.data['fact_checks'];
    if (rawFacts is! List) {
      throw AppException.validation(
        'Fail-Fast: FACT_CHECK fact_checks must be a List.',
      );
    }
    final facts = <Map<String, Object?>>[];
    for (var i = 0; i < rawFacts.length; i++) {
      final item = rawFacts[i];
      if (item is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: FACT_CHECK fact_checks[$i] must be a Map<String, Object?>.',
        );
      }
      facts.add(item);
    }

    final rawEthics = widget.data['ethical_issues'];
    if (rawEthics is! List) {
      throw AppException.validation(
        'Fail-Fast: FACT_CHECK ethical_issues must be a List.',
      );
    }
    final ethics = <Map<String, Object?>>[];
    for (var i = 0; i < rawEthics.length; i++) {
      final item = rawEthics[i];
      if (item is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: FACT_CHECK ethical_issues[$i] must be a Map<String, Object?>.',
        );
      }
      ethics.add(item);
    }

    final factHelp = _buildHelpButton(context, 'fact_check');
    final ethicsChildren = <Widget>[];
    if (ethics.isNotEmpty) {
      ethicsChildren.add(
        Row(
          children: [
            Expanded(
              child: Text(
                l10n.lblEthicalObservation,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            if (factHelp != null) ...[AppSpacing.w8, factHelp],
          ],
        ),
      );
      ethicsChildren.add(AppSpacing.h8);

      ethicsChildren.addAll(
        ethics.map<Widget>((e) {
          final isCrit =
              e['is_critical'] == true ||
              e['severity'] == 'Kriittinen' ||
              e['severity'] == 'Critical';
          return Card(
            color: isCrit ? colorScheme.errorContainer : colorScheme.surface,
            child: ListTile(
              leading: Icon(Icons.security, color: colorScheme.error),
              title: Text(
                e['label']?.toString() ??
                    e['issue_type']?.toString() ??
                    e['tyyppi']?.toString() ??
                    l10n.lblEthicalObservation,
                style: isCrit
                    ? textTheme.bodyMedium?.copyWith(
                        color: colorScheme.onErrorContainer,
                        fontWeight: FontWeight.bold,
                      )
                    : textTheme.bodyMedium,
              ),
              subtitle: Text(
                e['description']?.toString() ?? e['kuvaus']?.toString() ?? '',
                style: textTheme.bodySmall,
              ),
              trailing: Text(
                e['severity']?.toString() ??
                    e['vakavuus']?.toString() ??
                    l10n.dataUnavailable,
                style: textTheme.labelSmall,
              ),
            ),
          );
        }),
      );
    }

    final factsChildren = <Widget>[
      Row(
        children: [
          Expanded(
            child: Text(
              l10n.lblFactCheck,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          ?factHelp,
        ],
      ),
    ];

    if (facts.isEmpty) {
      factsChildren.add(
        Padding(
          padding: AppSpacing.p8,
          child: Text(l10n.lblNoFindings, style: textTheme.bodyMedium),
        ),
      );
    } else {
      factsChildren.addAll(
        facts.map<Widget>((f) {
          final resultKey =
              f['verification_result']?.toString() ?? 'VER_UNCERTAIN';
          final rawStatus =
              f['label']?.toString() ?? f['label_key']?.toString() ?? resultKey;
          final statusText = _getLocalizedEnum(rawStatus, l10n);
          IconData i = Icons.help_outline;
          Color c = colorScheme.error;

          if (resultKey == 'VER_VERIFIED') {
            i = Icons.check_circle;
            c = colorScheme.primary;
          } else if (resultKey == 'VER_DEBUNKED') {
            i = Icons.cancel;
            c = colorScheme.error;
          }

          return ListTile(
            leading: Icon(i, color: c),
            title: Text(
              f['vaite']?.toString() ?? f['claim']?.toString() ?? '',
              style: textTheme.bodyMedium,
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  statusText,
                  style: textTheme.labelSmall?.copyWith(
                    color: c,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  f['lahde_tai_paattely']?.toString() ??
                      f['source']?.toString() ??
                      '',
                  style: textTheme.bodySmall,
                ),
              ],
            ),
          );
        }),
      );
    }

    if (ethics.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: factsChildren,
      );
    }
    if (facts.isEmpty && ethics.isNotEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: ethicsChildren,
      );
    }

    return _buildResponsiveLayout(
      context,
      leftContent: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: ethicsChildren,
      ),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: factsChildren,
      ),
      leftFlex: 5,
      rightFlex: 5,
    );
  }

  Widget _buildPerformativityCheck(BuildContext context) {
    _validateRequiredKeys([
      'heuristics',
      'authenticity_assessment',
      'authenticity_score',
    ], 'PERFORMATIVITY_CHECK');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final rawHeuristics = widget.data['heuristics'];
    if (rawHeuristics is! List) {
      throw AppException.validation(
        'Fail-Fast: PERFORMATIVITY_CHECK heuristics must be a List.',
      );
    }
    final heuristics = <Map<String, Object?>>[];
    for (var i = 0; i < rawHeuristics.length; i++) {
      final item = rawHeuristics[i];
      if (item is! Map<String, Object?>) {
        throw AppException.validation(
          'Fail-Fast: PERFORMATIVITY_CHECK heuristics[$i] must be a Map<String, Object?>.',
        );
      }
      heuristics.add(item);
    }

    final overall = widget.data['authenticity_assessment']?.toString();
    final authScore = _parseNumericScore(
      widget.data['authenticity_score'],
      'authenticity_score',
      maxBound: _authenticityMaxScore,
    );

    final leftChildren = <Widget>[];
    if (overall != null) {
      String displayAuth = overall;
      if (overall.contains('AUTH_ORGANIC')) {
        displayAuth = l10n.authOrganic;
      } else if (overall.contains('AUTH_PERFORMATIVE')) {
        displayAuth = l10n.authPerformative;
      } else if (overall.contains('AUTH_UNKNOWN')) {
        displayAuth = l10n.authUnknown;
      }

      leftChildren.add(
        Container(
          padding: AppSpacing.p16,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                colorScheme.tertiaryContainer,
                colorScheme.primaryContainer,
              ],
            ),
            borderRadius: BorderRadius.circular(AppSpacing.s12),
          ),
          child: Column(
            children: [
              UnifiedMetricGauge(
                label: l10n.lblAuthenticity,
                value: authScore,
                max: _authenticityMaxScore,
                description:
                    widget.data['authenticity_help']?.toString() ??
                    l10n.helpAuthenticity,
                displayValue:
                    '${authScore.toStringAsFixed(1)}/${_authenticityMaxScore.toStringAsFixed(1)}',
                color: colorScheme.tertiary,
                axisLabels: [l10n.authPerformative, '', l10n.authOrganic],
              ),
              AppSpacing.h8,
              Text(
                displayAuth,
                style: textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      );
    }

    final perfHelp = _buildHelpButton(context, 'performativity');
    final rightChildren = <Widget>[
      Row(
        children: [
          Expanded(
            child: Text(
              '${l10n.lblHeuristics}:',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          if (perfHelp != null) ...[AppSpacing.w8, perfHelp],
        ],
      ),
      AppSpacing.h8,
      Wrap(
        spacing: AppSpacing.s8,
        runSpacing: AppSpacing.s4,
        children: heuristics.map<Widget>((b) {
          final raised = b['flag'] == true;
          return Chip(
            label: Text(b['name']?.toString() ?? ''),
            avatar: Icon(
              raised ? Icons.flag : Icons.check,
              size: AppSpacing.s16,
              color: raised ? colorScheme.error : colorScheme.primary,
            ),
            backgroundColor: raised
                ? colorScheme.errorContainer
                : colorScheme.primaryContainer,
            labelStyle: textTheme.labelSmall?.copyWith(
              color: raised
                  ? colorScheme.onErrorContainer
                  : colorScheme.onPrimaryContainer,
            ),
          );
        }).toList(),
      ),
    ];

    return _buildResponsiveLayout(
      context,
      leftContent: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: leftChildren,
      ),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: rightChildren,
      ),
      leftFlex: 4,
      rightFlex: 6,
    );
  }

  Widget _buildArchivistCheck(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final rawScore = widget.data['compliance_score'];
    final double scoreVal = rawScore != null
        ? _parseNumericScore(
            rawScore,
            'compliance_score',
            maxBound: _complianceMaxScore,
          )
        : 0.0;
    final rawRecs =
        widget.data['recommendations'] ?? widget.data['suositukset'];
    final recs = rawRecs is List ? rawRecs : const <Object?>[];

    final analysis =
        widget.data['consistency_analysis']?.toString() ??
        widget.data['analysis']?.toString();

    final leftChildren = <Widget>[
      Container(
        padding: AppSpacing.p12,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            UnifiedMetricGauge(
              label: l10n.lblComplianceAnalysis,
              value: scoreVal,
              max: _complianceMaxScore,
              description:
                  widget.data['help_archivist']?.toString() ??
                  widget.data['help_compliance']?.toString() ??
                  l10n.helpArchivist,
              displayValue:
                  '${scoreVal.toStringAsFixed(1)}/${_complianceMaxScore.toStringAsFixed(1)}',
              color: colorScheme.onSurfaceVariant,
              axisLabels: [l10n.lblWeak, '', '', '', '', l10n.lblStrong],
            ),
            AppSpacing.h8,
            Text(
              analysis != null && analysis.isNotEmpty
                  ? analysis
                  : l10n.lblNoAnalysis,
              style: textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    ];

    final rightChildren = <Widget>[
      for (final r in recs)
        ListTile(
          leading: Icon(
            Icons.task_alt,
            size: AppSpacing.s16,
            color: colorScheme.onSurfaceVariant,
          ),
          title: Text(r.toString(), style: textTheme.bodySmall),
          dense: true,
        ),
    ];

    return _buildResponsiveLayout(
      context,
      leftContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: leftChildren,
      ),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: rightChildren,
      ),
      leftFlex: 4,
      rightFlex: 6,
    );
  }

  Widget _buildGenericMap(BuildContext context, Map<String, Object?> map) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: map.entries.map<Widget>((e) {
        final parsedKey = e.key.replaceAll(RegExp(r'\*+'), '').trim();

        final String displayValue;
        if (e.value is Map || e.value is List) {
          displayValue = const JsonEncoder.withIndent('  ').convert(e.value);
        } else {
          displayValue = e.value?.toString() ?? '';
        }

        return Container(
          margin: const EdgeInsets.only(bottom: AppSpacing.s12),
          padding: AppSpacing.p12,
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(AppSpacing.s8),
            border: Border.all(color: colorScheme.surfaceContainerHighest),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                parsedKey.toUpperCase(),
                style: textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                  color: colorScheme.primary,
                ),
              ),
              AppSpacing.h8,
              if (displayValue.contains('```') || displayValue.contains('**'))
                OutputRenderer(markdownContent: displayValue)
              else
                SelectableText(
                  displayValue,
                  style: textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurface,
                    height: 1.5,
                  ),
                ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildInfoCard(
    BuildContext context,
    String title,
    String? value,
    IconData icon, {
    String? subtitle,
    Color? color,
    String? helpKey,
  }) {
    if (value == null || value.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Missing value for InfoCard: "$title"',
      );
    }

    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final helpBtn = helpKey != null ? _buildHelpButton(context, helpKey) : null;

    return Semantics(
      excludeSemantics: Platform.isWindows,
      child: ExpansionTile(
        tilePadding: EdgeInsets.zero,
        title: Container(
          padding: AppSpacing.p12,
          decoration: BoxDecoration(
            color: color ?? colorScheme.surfaceContainerLow,
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Row(
            children: [
              Icon(
                icon,
                size: _infoIconSize,
                color: colorScheme.onSurfaceVariant,
              ),
              AppSpacing.w16,
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: textTheme.bodySmall?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ),
                        ?helpBtn,
                      ],
                    ),
                    Text(
                      value,
                      style: textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        children: [
          if (subtitle != null)
            Padding(
              padding: const EdgeInsets.only(
                left: AppSpacing.s12,
                right: AppSpacing.s12,
                bottom: AppSpacing.s12,
              ),
              child: Text(
                subtitle,
                style: textTheme.bodySmall?.copyWith(
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildComparisonBlock(
    BuildContext context,
    String label,
    Object? content,
    Color color,
  ) {
    final strContent = content?.toString() ?? '';
    if (strContent.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Missing content for ComparisonBlock: "$label"',
      );
    }

    final textTheme = Theme.of(context).textTheme;

    return Container(
      padding: AppSpacing.p8,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(AppSpacing.s4),
      ),
      child: Column(
        children: [
          Text(
            label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: textTheme.labelSmall?.copyWith(fontWeight: FontWeight.bold),
          ),
          AppSpacing.h4,
          Text(
            strContent,
            style: textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildLabelValue(BuildContext context, String label, Object? value) {
    final strValue = value?.toString() ?? '';
    if (strValue.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Missing value for LabelValue: "$label"',
      );
    }

    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: textTheme.labelSmall?.copyWith(
            color: colorScheme.onSurfaceVariant,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(strValue, style: textTheme.bodyMedium),
      ],
    );
  }

  Widget _buildRawJsonView(BuildContext context) {
    final theme = Theme.of(context);
    final jsonStr = const JsonEncoder.withIndent('  ').convert(widget.data);
    return Container(
      width: double.infinity,
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(AppSpacing.s4),
      ),
      child: SelectableText(
        jsonStr,
        style: theme.textTheme.bodySmall?.copyWith(fontFamily: 'monospace'),
      ),
    );
  }

  Widget? _buildHelpButton(BuildContext context, String key) {
    final text =
        (widget.data[key] ??
                widget.data['help_$key'] ??
                widget.data['${key}_help'] ??
                '')
            .toString();
    if (text.trim().isEmpty) return null;

    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    return IconButton(
      icon: Icon(
        Icons.help_outline,
        size: _helpIconSize,
        color: colorScheme.onSurfaceVariant,
      ),
      onPressed: () {
        showDialog<void>(
          context: context,
          builder: (ctx) => AlertDialog(
            title: Row(
              children: [
                Icon(Icons.info_outline, color: colorScheme.primary),
                AppSpacing.w8,
                Expanded(
                  child: Text(
                    l10n.aboutMetricTitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.titleMedium,
                  ),
                ),
              ],
            ),
            content: Text(
              text,
              style: textTheme.bodyMedium?.copyWith(height: 1.5),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: Text(l10n.sharedOk),
              ),
            ],
          ),
        );
      },
      tooltip: l10n.sharedMoreInfoTooltip,
    );
  }

  Widget _buildDriverProfile(BuildContext context) {
    _validateRequiredKeys([
      'role_classification',
      'high_dependency',
      'imperative_command_count',
      'strategy',
    ], 'Driver Profile');
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    final roleRaw = widget.data['role_classification']?.toString().trim() ?? '';
    if (roleRaw.isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Driver Profile role_classification cannot be empty.',
      );
    }

    final rawRatio = widget.data['input_control_ratio'];
    final double? ratio = rawRatio != null
        ? _parseNumericScore(rawRatio, 'input_control_ratio')
        : null;

    final rawCmdCount = widget.data['imperative_command_count'];
    if (rawCmdCount is! int) {
      throw AppException.validation(
        'Fail-Fast: Driver Profile imperative_command_count must be an int.',
      );
    }
    final cmdCount = rawCmdCount;

    final rawHighDep = widget.data['high_dependency'];
    if (rawHighDep is! bool) {
      throw AppException.validation(
        'Fail-Fast: Driver Profile high_dependency must be a bool.',
      );
    }
    final isHighDependency = rawHighDep;

    final strategyRaw = widget.data['strategy']?.toString().trim() ?? '';
    if (strategyRaw.isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Driver Profile strategy cannot be empty.',
      );
    }
    final strategies = [strategyRaw];

    final String role = roleRaw.startsWith('ROLE_')
        ? roleRaw
        : 'ROLE_${roleRaw.toUpperCase()}';

    final roles = [
      l10n.rolePassenger,
      l10n.roleNavigator,
      l10n.roleDriver,
      l10n.roleArchitect,
    ];

    final controlRatioHelp = _buildHelpButton(context, 'control_ratio');

    final leftChildren = <Widget>[
      Container(
        padding: AppSpacing.p16,
        decoration: BoxDecoration(
          color: colorScheme.primaryContainer.withValues(alpha: 0.3),
          borderRadius: BorderRadius.circular(AppSpacing.s12),
          border: Border.all(color: colorScheme.primary),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Flexible(
                  child: Text(
                    l10n.lblRoleAndPosition,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                if (controlRatioHelp != null) ...[
                  AppSpacing.w8,
                  controlRatioHelp,
                ],
              ],
            ),
            AppSpacing.h8,
            Text(
              ratio != null
                  ? '${(ratio * 100).toStringAsFixed(0)}%'
                  : l10n.dataUnavailable,
              style: textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: colorScheme.primary,
              ),
            ),
            Text(
              l10n.lblControlRatio,
              style: textTheme.bodySmall?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            AppSpacing.h24,
            LayoutBuilder(
              builder: (context, constraints) {
                final translatedRole = _getLocalizedEnum(role, l10n);
                return Stack(
                  alignment: Alignment.center,
                  children: [
                    Positioned(
                      left: _spectrumLineHorizontalInset,
                      right: _spectrumLineHorizontalInset,
                      top: _spectrumLineTop,
                      child: Container(
                        height: _spectrumTrackHeight,
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: roles.map((r) {
                        final isActive =
                            translatedRole.toLowerCase() == r.toLowerCase();
                        return Expanded(
                          child: Column(
                            children: [
                              Container(
                                width: _spectrumNodeDimension,
                                height: _spectrumNodeDimension,
                                decoration: BoxDecoration(
                                  color: isActive
                                      ? colorScheme.primary
                                      : colorScheme.onSurfaceVariant,
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: colorScheme.surface,
                                    width: _spectrumBorderWidth,
                                  ),
                                  boxShadow: [
                                    if (isActive)
                                      BoxShadow(
                                        color: colorScheme.primary.withValues(
                                          alpha: 0.4,
                                        ),
                                        spreadRadius: AppSpacing.s2,
                                        blurRadius: AppSpacing.s4,
                                      )
                                    else
                                      BoxShadow(
                                        color: colorScheme.onSurfaceVariant,
                                        spreadRadius: _defaultBorderWidth,
                                      ),
                                  ],
                                ),
                              ),
                              AppSpacing.h8,
                              Text(
                                r,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: textTheme.labelSmall?.copyWith(
                                  fontWeight: isActive
                                      ? FontWeight.bold
                                      : FontWeight.normal,
                                  color: isActive
                                      ? colorScheme.primary
                                      : colorScheme.onSurfaceVariant,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    ];

    final rightChildren = <Widget>[];
    if (strategies.isNotEmpty) {
      rightChildren.add(
        Text(
          l10n.sharedIdentifiedStrategies,
          style: textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold),
        ),
      );
      rightChildren.add(AppSpacing.h8);
      rightChildren.add(
        Wrap(
          spacing: AppSpacing.s8,
          runSpacing: AppSpacing.s4,
          children: [
            for (final s in strategies)
              Chip(
                label: Text(s),
                backgroundColor: colorScheme.primaryContainer,
              ),
          ],
        ),
      );
      rightChildren.add(AppSpacing.h16);
    }

    if (isHighDependency) {
      rightChildren.add(
        Chip(
          label: Text(
            l10n.sharedHighDependency,
            style: textTheme.labelSmall?.copyWith(color: colorScheme.onError),
          ),
          backgroundColor: colorScheme.error,
          avatar: Icon(
            Icons.warning_amber_rounded,
            color: colorScheme.onError,
            size: AppSpacing.s16,
          ),
        ),
      );
      rightChildren.add(AppSpacing.h12);
    }

    rightChildren.add(
      Text(
        l10n.sharedImperativeCommandsCount(cmdCount),
        style: textTheme.bodyMedium?.copyWith(
          color: colorScheme.onSurfaceVariant,
          fontStyle: FontStyle.italic,
        ),
      ),
    );
    rightChildren.add(AppSpacing.h12);

    if (widget.data['compliance_analysis'] != null) {
      rightChildren.add(
        _buildComparisonBlock(
          context,
          l10n.lblComplianceAnalysis,
          widget.data['compliance_analysis'],
          colorScheme.primaryContainer,
        ),
      );
      rightChildren.add(AppSpacing.h8);
    }

    if (widget.data['poikkeamat_linjasta'] != null) {
      rightChildren.add(
        _buildInfoCard(
          context,
          l10n.sharedDeviationsFromAlignment,
          widget.data['poikkeamat_linjasta']?.toString(),
          Icons.call_split,
          color: colorScheme.surfaceContainerLow,
        ),
      );
      rightChildren.add(AppSpacing.h8);
    }

    if (widget.data['suositus_tuomarille'] != null) {
      final recText =
          widget.data['suositus_tuomarille']?.toString().trim() ?? '';
      if (recText.isEmpty) {
        throw AppException.validation(
          'Fail-Fast: Driver Profile suositus_tuomarille cannot be empty.',
        );
      }
      rightChildren.add(
        Container(
          padding: AppSpacing.p16,
          decoration: BoxDecoration(
            color: colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(AppSpacing.s8),
            border: Border.all(color: colorScheme.primary),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.recommend, color: colorScheme.primary),
                  AppSpacing.w8,
                  Expanded(
                    child: Text(
                      l10n.recommendationToJudgeTitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: colorScheme.primary,
                      ),
                    ),
                  ),
                ],
              ),
              AppSpacing.h8,
              Text(recText, style: textTheme.bodyMedium),
            ],
          ),
        ),
      );
    }

    return _buildResponsiveLayout(
      context,
      leftContent: Column(children: leftChildren),
      rightContent: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: rightChildren,
      ),
      leftFlex: 4,
      rightFlex: 6,
    );
  }

  Widget _buildCompactTextMetrics(
    BuildContext context,
    Map<String, Object?> metrics,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;
    final l10n = AppLocalizations.of(context)!;

    double parseMetricDouble(Object? value) {
      if (value == null) return 0.0;
      if (value is num) return value.toDouble();
      if (value is String) return double.tryParse(value) ?? 0.0;
      return 0.0;
    }

    final wordCount =
        metrics['word_count_display'] ?? metrics['word_count'] ?? 0;
    final sentCount = metrics['sentence_count'] ?? 0;
    final lexDiv =
        metrics['lexical_diversity_display'] ??
        parseMetricDouble(metrics['lexical_diversity']).toStringAsFixed(2);

    return Container(
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: colorScheme.secondaryContainer.withValues(alpha: 0.3),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
        border: Border.all(color: colorScheme.secondary),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.bar_chart,
                size: AppSpacing.s16,
                color: colorScheme.secondary,
              ),
              AppSpacing.w8,
              Expanded(
                child: Text(
                  l10n.lblTextMetrics,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: textTheme.labelMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: colorScheme.secondary,
                  ),
                ),
              ),
            ],
          ),
          AppSpacing.h8,
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Expanded(
                child: _buildCompactMetricItem(
                  context,
                  l10n.lblWordCount,
                  '$wordCount',
                ),
              ),
              Expanded(
                child: _buildCompactMetricItem(
                  context,
                  l10n.lblSentenceCount,
                  '$sentCount',
                ),
              ),
              Expanded(
                child: _buildCompactMetricItem(
                  context,
                  l10n.lblLexicalDiversity,
                  '$lexDiv',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCompactMetricItem(
    BuildContext context,
    String label,
    String value,
  ) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    return Column(
      children: [
        Text(
          label.toUpperCase(),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: textTheme.labelSmall?.copyWith(
            color: colorScheme.secondary,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          value,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: colorScheme.secondary,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricBlock(BuildContext context, String label, String value) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final textTheme = theme.textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
            color: colorScheme.primary,
          ),
        ),
        AppSpacing.h2,
        Text(
          label,
          style: textTheme.bodySmall?.copyWith(
            color: colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }

  double _parseNumericScore(
    Object? raw,
    String fieldName, {
    double minBound = 0.0,
    double? maxBound,
  }) {
    final double val;
    if (raw is num) {
      val = raw.toDouble();
    } else if (raw != null) {
      final parsed = double.tryParse(raw.toString().trim());
      if (parsed == null) {
        throw AppException.validation(
          'Fail-Fast: SpecialistSection $fieldName must be a valid number.',
        );
      }
      val = parsed;
    } else {
      throw AppException.validation(
        'Fail-Fast: SpecialistSection $fieldName is required.',
      );
    }

    if (val.isNaN || val.isInfinite) {
      throw AppException.validation(
        'Fail-Fast: SpecialistSection $fieldName must be finite.',
      );
    }

    if (val < minBound || (maxBound != null && val > maxBound)) {
      throw AppException.validation(
        'Fail-Fast: SpecialistSection $fieldName ($val) is out of bounds [$minBound, ${maxBound ?? 'inf'}].',
      );
    }
    return val;
  }
}
