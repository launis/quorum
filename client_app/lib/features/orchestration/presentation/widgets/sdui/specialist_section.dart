import '../results/logic_matrix_chart.dart';
import 'unified_metric_gauge.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'dart:io';
import 'package:client_app/l10n/gen/app_localizations.dart';

class SpecialistSection extends StatefulWidget {
  final String title;
  final String type; // e.g. LOGIC_ANALYSIS, STRESS_TEST
  final Map<String, dynamic> data;
  final Map<String, dynamic>? metrics;

  const SpecialistSection({
    super.key,
    required this.title,
    required this.type,
    required this.data,
    this.metrics,
  });

  @override
  State<SpecialistSection> createState() => _SpecialistSectionState();
}

class _SpecialistSectionState extends State<SpecialistSection> {
  bool _showRaw = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Semantics(
        excludeSemantics: Platform.isWindows,
        child: ExpansionTile(
          leading: _buildIconForType(),
          title: Text(
            widget.title,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          subtitle: Text(
            _getSubtitleForType(),
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
          childrenPadding: const EdgeInsets.all(16),
          children: [
            // Toolbar
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: () {
                    setState(() {
                      _showRaw = !_showRaw;
                    });
                  },
                  icon: Icon(
                    _showRaw ? Icons.visibility_off : Icons.code,
                    size: 16,
                  ),
                  label: Text(
                    _showRaw ? 'Piilota Raaka-Data' : 'JSON',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.copy, size: 16),
                  onPressed: () {
                    final jsonStr = const JsonEncoder.withIndent(
                      '  ',
                    ).convert(widget.data);
                    Clipboard.setData(ClipboardData(text: jsonStr));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('JSON kopioitu leikepöydälle'),
                        duration: Duration(seconds: 1),
                      ),
                    );
                  },
                  tooltip: 'Kopioi JSON',
                ),
              ],
            ),
            const Divider(),

            AnimatedCrossFade(
              firstChild: _buildSummaryView(context),
              secondChild: _buildRawJsonView(),
              crossFadeState:
                  _showRaw
                      ? CrossFadeState.showSecond
                      : CrossFadeState.showFirst,
              duration: const Duration(milliseconds: 300),
            ),
          ],
        ),
      ),
    );
  }

  Icon _buildIconForType() {
    switch (widget.type) {
      case 'LOGIC_ANALYSIS':
        return const Icon(Icons.psychology, color: Colors.indigo);
      case 'STRESS_TEST':
        return const Icon(Icons.fitness_center, color: Colors.orange);
      case 'CAUSAL_ANALYSIS':
        return const Icon(Icons.compare_arrows, color: Colors.teal);
      case 'PERFORMATIVITY_CHECK':
        return const Icon(Icons.theater_comedy, color: Colors.purple);
      case 'FACT_CHECK':
        return const Icon(Icons.fact_check, color: Colors.blue);
      case 'PROFILER_ANALYSIS':
        return const Icon(Icons.face, color: Colors.pinkAccent);
      case 'ARCHIVIST_CHECK':
        return const Icon(Icons.gavel, color: Colors.brown);
      default:
        return const Icon(Icons.extension, color: Colors.grey);
    }
  }

  String _getSubtitleForType() {
    switch (widget.type) {
      case 'LOGIC_ANALYSIS':
        return "Toulmin & Kognitiivinen Taso";
      case 'STRESS_TEST':
        return "Walton Falsifiointi";
      case 'CAUSAL_ANALYSIS':
        return "Kausaalinen & Kontrafaktuaalinen";
      case 'PERFORMATIVITY_CHECK':
        return "Aitous & Pre-Mortem";
      case 'FACT_CHECK':
        return "Hallusinaatiot & Etiikka";
      case 'PROFILER_ANALYSIS':
        return "Vinoumat & Psyko-profiili";
      case 'ARCHIVIST_CHECK':
        return "Compliance & Ennakkotapaukset";
      default:
        return "";
    }
  }

  void _validateRequiredKeys(List<String> keys, String contextName) {
    final missing = keys.where((k) => widget.data[k] == null).toList();
    if (missing.isNotEmpty) {
      final msg =
          "Missing required keys in $contextName: ${missing.join(', ')}";
      debugPrint("🔴 STRUCTURAL DATA ERROR: $msg");
      throw FormatException(msg);
    }
  }

  Widget _buildDataErrorCard(String errorDetails) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.only(top: 8, bottom: 8),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        border: Border.all(color: Colors.red.shade200),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: Colors.red.shade700),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  "Data Integrity Error (Fail Fast)",
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.red.shade900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            errorDetails,
            style: TextStyle(
              fontFamily: 'monospace',
              fontSize: 12,
              color: Colors.red.shade900,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryView(BuildContext context) {
    if (widget.data.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(8.0),
        child: Text(
          "Ei dataa saatavilla.",
          style: TextStyle(fontStyle: FontStyle.italic),
        ),
      );
    }

    try {
      // Switch on type to provide RICH custom visualization
      switch (widget.type) {
        case 'LOGIC_ANALYSIS':
          return _buildLogicAnalysis(context);
        case 'STRESS_TEST':
          return _buildStressTest(context);
        case 'CAUSAL_ANALYSIS':
          return _buildCausalAnalysis(context);
        case 'PROFILER_ANALYSIS':
          return _buildProfilerAnalysis(context);
        case 'FACT_CHECK':
          return _buildFactCheck(context);
        case 'PERFORMATIVITY_CHECK':
          return _buildPerformativityCheck(context);
        case 'ARCHIVIST_CHECK':
          return _buildArchivistCheck(context);

        case 'DRIVER_PROFILE':
          return _buildDriverProfile(context);
        case 'SECURITY_CHECK':
          return _buildSecurityCheck(context);
        default:
          // Fallback to generic map renderer if type is barely supported
          return _buildGenericMap(widget.data);
      }
    } catch (e, stack) {
      debugPrint('🔴 UI GRACEFUL DEGRADATION [${widget.type}]: $e\n$stack');
      return _buildDataErrorCard(e.toString());
    }
  }

  // --- RESPONSIVE LAYOUT HELPER ---
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
        if (constraints.maxWidth > 800) {
          // Desktop / Horizontal layout
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(flex: leftFlex, child: leftContent),
              const SizedBox(width: 16),
              Expanded(flex: rightFlex, child: rightContent),
            ],
          );
        } else {
          // Mobile / Vertical Stack
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children:
                mobileReverse
                    ? [rightContent, const SizedBox(height: 16), leftContent]
                    : [leftContent, const SizedBox(height: 16), rightContent],
          );
        }
      },
    );
  }

  String _getLocalizedEnum(String? key) {
    if (key == null) return "N/A";
    final l10n = AppLocalizations.of(context)!;
    switch (key) {
      // Security
      case 'SEC_THREAT_DETECTED':
        return l10n.secThreatDetected;
      case 'SEC_THREAT_NONE':
        return l10n.secThreatNone;
      case 'SEC_ANONYMIZED':
        return l10n.secAnonymized;
      case 'SEC_NOT_ANONYMIZED':
        return l10n.secNotAnonymized;
      case 'RISK_HIGH':
        return l10n.riskHigh;
      case 'RISK_MEDIUM':
        return l10n.riskMedium;
      case 'RISK_LOW':
        return l10n.riskLow;
      case 'RISK_UNKNOWN':
        return l10n.riskUnknown;
      // Profiler
      case 'BIAS_DETECTED':
        return l10n.biasDetected;
      case 'BIAS_NONE':
        return l10n.biasNone;
      case 'GAP_DETECTED':
        return l10n.gapDetected;
      case 'GAP_NONE':
        return l10n.gapNone;
      // Roles
      case 'ROLE_PASSENGER':
        return l10n.rolePassenger;
      case 'ROLE_NAVIGATOR':
        return l10n.roleNavigator;
      case 'ROLE_DRIVER':
        return l10n.roleDriver;
      case 'ROLE_ARCHITECT':
        return l10n.roleArchitect;
      // Fact Check
      case 'VER_VERIFIED':
        return l10n.verVerified;
      case 'VER_DEBUNKED':
        return l10n.verDebunked;
      case 'VER_UNCERTAIN':
        return l10n.verUncertain;
      // Performativity
      case 'AUTH_ORGANIC':
        return l10n.authOrganic;
      case 'AUTH_PERFORMATIVE':
        return l10n.authPerformative;
      case 'AUTH_UNKNOWN':
        return l10n.authUnknown;
      // Bloom
      case 'BLOOM_REMEMBERING':
        return l10n.bloomRemembering;
      case 'BLOOM_UNDERSTANDING':
        return l10n.bloomUnderstanding;
      case 'BLOOM_APPLYING':
        return l10n.bloomApplying;
      case 'BLOOM_ANALYZING':
        return l10n.bloomAnalyzing;
      case 'BLOOM_EVALUATING':
        return l10n.bloomEvaluating;
      case 'BLOOM_CREATING':
        return l10n.bloomCreating;
      // Strategic Depth
      case 'STRAT_LOW':
        return l10n.stratLow;
      case 'STRAT_MEDIUM':
        return l10n.stratMedium;
      case 'STRAT_HIGH':
        return l10n.stratHigh;
      case 'STRAT_VISIONARY':
        return l10n.stratVisionary;

      // Profiler Enums
      case 'BIAS_DETECTED':
        return l10n.biasDetected;
      case 'BIAS_NONE':
        return l10n.biasNone;
      case 'GAP_DETECTED':
        return l10n.gapDetected;
      case 'GAP_NONE':
        return l10n.gapNone;

      default:
        return key;
    }
  }

  // --- 1. LOGIC ANALYSIS (Toulmin & Cognitive) ---
  Widget _buildLogicAnalysis(BuildContext context) {
    _validateRequiredKeys([
      'bloom_score',
      'strategic_score',
      'arguments',
    ], 'LOGIC_ANALYSIS');
    final l10n = AppLocalizations.of(context)!;

    // Strict V3 Flattened Keys
    final arguments =
        (widget.data['arguments'] as List?)?.cast<Map<String, dynamic>>() ?? [];

    final methodology =
        widget.data['methodological_log'] ??
        widget.data['metodologinen_loki'] as String?;

    final List<Widget> children = [];

    if (methodology != null) {
      children.add(
        _buildInfoCard(
          l10n.lblMethodologicalLog,
          methodology,
          Icons.history_edu,
          helpKey: "metodologia",
        ),
      );
      children.add(const SizedBox(height: 16));
    }

    // NEW: Compact Text Metrics (PDF Parity)
    if (widget.metrics != null && widget.metrics!.isNotEmpty) {
      children.add(_buildCompactTextMetrics(context, widget.metrics!));
      children.add(const SizedBox(height: 16));
    }

    children.add(
      LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth > 800;

          // Enhanced Bloom Widget (Report Style)
          final bloomWidget = Card(
            color: Colors.teal[50], // Distinct color for Cognitive
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.psychology, color: Colors.teal),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          "${l10n.lblCognitiveLevel}: ${widget.data['bloom_level_raw'] ?? 'Bloom Unknown'} (${widget.data['bloom_score'] ?? '?'})",
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: Colors.teal,
                          ),
                        ),
                      ),
                      _buildHelpButton(context, "bloom"),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    l10n.lblStrategicDepth,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  SelectableText(
                    (widget.data['strategic_depth_raw'] ?? 'Strategic Unknown')
                        .toString(),
                    style: const TextStyle(
                      fontSize: 14,
                      height: 1.5,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          );

          final List<Widget> toulminChildren = [];
          toulminChildren.add(
            Row(
              children: [
                Text(
                  l10n.lblArguments,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                _buildHelpButton(context, "toulmin"),
              ],
            ),
          );
          toulminChildren.add(const SizedBox(height: 8));

          toulminChildren.addAll(
            arguments.map<Widget>(
              (t) => Card(
                margin: const EdgeInsets.only(bottom: 8),
                color: Colors.indigo[50],
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildLabelValue("Väite (Claim)", t['claim']),
                      const SizedBox(height: 4),
                      const Divider(),
                      const SizedBox(height: 4),
                      _buildLabelValue("Perustelu (Warrant)", t['warrant']),
                      if (t['backing'] != null) ...[
                        const SizedBox(height: 4),
                        _buildLabelValue("Tuki (Backing)", t['backing']),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          );

          // Strategic Depth Gauge (New)
          final stratScore =
              (widget.data['strategic_score'] as num?)?.toDouble() ?? 2.0;
          final stratDisplay =
              widget.data['strategic_score_display'] ??
              "$stratScore/4.0"; // Use formatted if available
          final stratGauge = UnifiedMetricGauge(
            label: l10n.lblStrategicDepth,
            value: stratScore,
            max: 4.0,
            description:
                widget.data['strategic_help'] ?? "Strategic Depth Help",
            displayValue: stratDisplay,
            color: Colors.teal[700],
            // FULL LABELS as requested
            axisLabels: [
              l10n.stratLow,
              l10n.stratMedium,
              l10n.stratHigh,
              l10n.stratVisionary,
            ],
          );

          // New Visualization Widget (3D Bubble Chart)
          final matrixChart = LogicMatrixChart(
            bloomScore: (widget.data['bloom_score'] as num?)?.toDouble() ?? 0.0,
            toulminScore:
                (widget.data['toulmin_score'] as num?)?.toDouble() ?? 0.0,
            strategicScore: stratScore,
          );

          // Enhanced Bloom & Toulmin using UnifiedMetricGauge

          final bloomGauge = UnifiedMetricGauge(
            label: l10n.lblBloomScore,
            value: (widget.data['bloom_score'] as num?)?.toDouble() ?? 0.0,
            max: 6.0,
            description:
                widget.data['bloom_help'] ??
                "Bloom Help", // Use key if available

            displayValue:
                "${((widget.data['bloom_score'] as num?)?.toDouble() ?? 0.0).toStringAsFixed(1)}/6.0",
            color: Colors.teal,
            // FULL LABELS as requested
            axisLabels: [
              l10n.bloomRemembering,
              l10n.bloomUnderstanding,
              l10n.bloomApplying,
              l10n.bloomAnalyzing,
              l10n.bloomEvaluating,
              l10n.bloomCreating,
            ],
          );

          final toulminGauge = UnifiedMetricGauge(
            label: l10n.lblToulminScore,
            value: (widget.data['toulmin_score'] as num?)?.toDouble() ?? 0.0,
            max: 6.0,
            description: widget.data['toulmin_help'] ?? "Toulmin Help",
            displayValue:
                "${((widget.data['toulmin_score'] as num?)?.toDouble() ?? 0.0).toStringAsFixed(1)}/6.0",
            color: Colors.indigo,
            axisLabels: const ['Väite', '', 'Peruste', '', 'Tuki', 'Vahva'],
          );

          // Responsive Layout handling Matrix right, Text left (mobile: Matrix top)
          Widget leftContent = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              bloomWidget,
              const SizedBox(height: 8),
              bloomGauge,
              const SizedBox(height: 4),
              stratGauge,
              const SizedBox(height: 16),
              if (arguments.isNotEmpty) ...[
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: toulminChildren,
                ),
                const SizedBox(height: 8),
                toulminGauge,
              ],
            ],
          );

          Widget rightContent = Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey[200]!),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      l10n.lblLogicMatrix,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(width: 8),
                    _buildHelpButton(context, "matrix"),
                  ],
                ),
                Text(
                  l10n.lblMatrixSubtitle,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
                const SizedBox(height: 16),
                Center(child: matrixChart),
              ],
            ),
          );

          return _buildResponsiveLayout(
            context,
            leftContent: leftContent,
            rightContent: rightContent,
            leftFlex: 4,
            rightFlex: 6,
            mobileReverse: true, // Matrix goes top on mobile
          );
        },
      ),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: children,
    );
  }

  // --- 1.5 SECURITY CHECK (New Compact Visuals) ---
  Widget _buildSecurityCheck(BuildContext context) {
    // Keys: threat_detected, risk_level, anonymized, findings
    // STRICT: Use Backend Provided Label Keys

    // Threat
    final threatLabel = widget.data['threat_label'] ?? "Threat Unknown";
    final threat = widget.data['threat_detected'] == true; // Keep for color

    // Risk
    final riskLabel = widget.data['risk_label'] ?? "Risk Unknown";
    // Determine color from Key (Safe/Canonical) or just use level if simpler?
    // We still need logic for color. BFF sends risk_color?
    // BFF sent "risk_color".
    // Let's use it if available!
    // widget.data['risk_color'] -> "red", "orange", "green".
    // Map string to Color.

    Color riskColor;
    final rColorStr = widget.data['risk_color'];
    if (rColorStr == 'red')
      riskColor = Colors.red;
    else if (rColorStr == 'orange')
      riskColor = Colors.orange;
    else if (rColorStr == 'green')
      riskColor = Colors.green;
    else
      riskColor = Colors.grey;

    IconData riskIcon = Icons.help_outline;
    // We can infer icon from color or just use generic.
    if (riskColor == Colors.red)
      riskIcon = Icons.gpp_bad;
    else if (riskColor == Colors.orange)
      riskIcon = Icons.warning_amber;
    else if (riskColor == Colors.green)
      riskIcon = Icons.check_circle;

    // Anonymized
    final anonLabel = widget.data['anonymized_label'] ?? "Anonymity Unknown";
    final anonymized = widget.data['anonymized'] == true;

    final findings =
        (widget.data['findings'] ?? widget.data['loydokset'] as List?)
            ?.cast<String>() ??
        [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Status Row (Chips)
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            _buildStatusChip(
              context,
              label: threatLabel,
              color: threat ? Colors.red : Colors.green,
              icon: threat ? Icons.warning : Icons.check,
            ),
            _buildStatusChip(
              context,
              label:
                  "${AppLocalizations.of(context)!.lblRiskLevel}: $riskLabel",
              color: riskColor,
              icon: riskIcon,
            ),
            _buildStatusChip(
              context,
              label: anonLabel,
              color: anonymized ? Colors.blue : Colors.grey,
              icon: anonymized ? Icons.visibility_off : Icons.visibility,
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Findings List (Compact)
        if (findings.isNotEmpty) ...[
          const Text(
            "Löydökset:",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 4),
          ...findings.map(
            (f) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(top: 2),
                    child: Icon(
                      Icons.arrow_right,
                      size: 16,
                      color: Colors.grey,
                    ),
                  ),
                  Expanded(
                    child: Text(f, style: const TextStyle(fontSize: 13)),
                  ),
                ],
              ),
            ),
          ),
        ] else
          const Text(
            "Ei merkittäviä löydöksiä.",
            style: TextStyle(
              fontStyle: FontStyle.italic,
              fontSize: 13,
              color: Colors.grey,
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
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color.withValues(alpha: 0.3)),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  // --- 2. STRESS TEST (Falsifier) ---
  Widget _buildStressTest(BuildContext context) {
    _validateRequiredKeys(['findings', 'fidelity_audit'], 'STRESS_TEST');
    // V3 Flat Keys:
    final findings =
        (widget.data['findings'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    final fidelity =
        widget.data['fidelity_audit'] as Map<String, dynamic>? ?? {};

    final leftChildren = <Widget>[];
    if (fidelity.isNotEmpty) {
      double scoreVal =
          (fidelity['fidelity_score_display'] as String?) != null
              ? double.tryParse(
                    fidelity['fidelity_score_display']!.split('/')[0],
                  ) ??
                  0.0
              : 0.0;

      leftChildren.add(
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.orange[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              UnifiedMetricGauge(
                label: AppLocalizations.of(context)!.lblFidelity,
                value: scoreVal,
                max: 3.0,
                description: widget.data['fidelity_help'] ?? "Fidelity Help",
                displayValue: fidelity['fidelity_score_display'] ?? "0.0/3.0",
                color: Colors.orange,
                axisLabels: const ['Matala', 'Keski', 'Korkea'],
              ),
              const SizedBox(height: 12),
              Text(
                fidelity['post_hoc_rationalization_suspected'] == true
                    ? AppLocalizations.of(context)!.lblPostHocWarning
                    : AppLocalizations.of(context)!.lblNoRationalization,
                style: TextStyle(
                  color:
                      fidelity['post_hoc_rationalization_suspected'] == true
                          ? Colors.red[800]
                          : Colors.green[800],
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 12),
              _buildLabelValue(
                "Post-Hoc Rationalization",
                fidelity['post_hoc_rationalization_suspected'].toString(),
              ),
              const SizedBox(height: 4),
              _buildLabelValue("Perustelu", fidelity['reasoning'] ?? '-'),
            ],
          ),
        ),
      );
    }

    final rightChildren = <Widget>[];
    rightChildren.addAll(
      findings.map<Widget>((f) {
        final passed = f['is_held'] == true;
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          color: passed ? Colors.green[50] : Colors.red[50],
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildLabelValue(
                  AppLocalizations.of(context)!.lblQuestion,
                  f['question'],
                ),
                const SizedBox(height: 4),
                _buildLabelValue(
                  AppLocalizations.of(context)!.lblEvidenceHeld,
                  f['is_held'].toString(),
                ),
                const SizedBox(height: 4),
                _buildLabelValue(
                  AppLocalizations.of(context)!.lblObservation,
                  f['observation'],
                ),
              ],
            ),
          ),
        );
      }),
    );

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

  // --- 3. CAUSAL ANALYSIS ---
  Widget _buildCausalAnalysis(BuildContext context) {
    _validateRequiredKeys([
      'abductive_score',
      'observation',
      'counterfactual_actual',
      'counterfactual_simulated',
    ], 'CAUSAL_ANALYSIS');

    // English Keys: causal_audit, counterfactual_test, abductive_conclusion
    // V3 Flat Keys:
    final abductive = widget.data['abductive_conclusion'] as String?;
    final abductiveScore =
        (widget.data['abductive_score'] as num?)?.toDouble() ?? 0.0;

    // Causal Audit Flat
    final observation = widget.data['observation'] as String?;

    // Counterfactual Test Flat
    final actualScenario = widget.data['counterfactual_actual'] as String?;
    final simulatedScenario =
        widget.data['counterfactual_simulated'] as String?;
    final plausibilityScore =
        widget.data['plausibility_score'] != null
            ? (widget.data['plausibility_score'] as num?)?.toDouble() ?? 0.0
            : null;

    final leftChildren = <Widget>[];
    if (abductive != null) {
      leftChildren.add(
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.teal[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              UnifiedMetricGauge(
                label: AppLocalizations.of(context)!.lblAbductiveReasoning,
                value: abductiveScore,
                max: 3.0,
                description: widget.data['abductive_help'] ?? "Abductive Help",
                displayValue:
                    widget.data['abductive_score_display'] ??
                    "${abductiveScore}/3.0",
                color: Colors.teal,
                axisLabels: const ['Heikko', 'Kohtalainen', 'Vahva'],
              ),
              const SizedBox(height: 8),
              Text(abductive, style: const TextStyle(fontSize: 14)),
            ],
          ),
        ),
      );
      leftChildren.add(const SizedBox(height: 16));
    }

    if (observation != null) {
      leftChildren.add(
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.teal[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    AppLocalizations.of(context)!.lblCausalAudit,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  _buildHelpButton(context, "causal"),
                ],
              ),
              const SizedBox(height: 8),
              Text(observation),
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
              AppLocalizations.of(context)!.lblCounterfactualTest,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: _buildComparisonBlock(
                    AppLocalizations.of(context)!.lblScenarioActual,
                    actualScenario,
                    Colors.grey[200]!,
                  ),
                ),
                const SizedBox(width: 8),
                const Icon(Icons.arrow_forward),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildComparisonBlock(
                    AppLocalizations.of(context)!.lblScenarioSimulation,
                    simulatedScenario,
                    Colors.teal[100]!,
                  ),
                ),
              ],
            ),
            if (plausibilityScore != null)
              Padding(
                padding: const EdgeInsets.only(top: 16.0),
                child: UnifiedMetricGauge(
                  label: AppLocalizations.of(context)!.lblCredibility,
                  value: plausibilityScore,
                  max: 3.0,
                  description:
                      widget.data['plausibility_help'] ?? "Plausibility Help",
                  displayValue:
                      widget.data['plausibility_score_display'] ??
                      "${plausibilityScore}/3.0",
                  color: Colors.teal,
                  axisLabels: const ['Epäuskottava', '', 'Uskottava'],
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

  // --- 4. PROFILER ANALYSIS ---
  Widget _buildProfilerAnalysis(BuildContext context) {
    _validateRequiredKeys([
      'word_count',
      'avg_sentence_length',
      'lexical_diversity',
    ], 'PROFILER_ANALYSIS');

    // English Keys: detected_biases, psychological_profile, author_intent, text_metrics
    // New V3 Flat Keys:
    final profile = widget.data['psychological_profile'] as String?;
    final intent = widget.data['intent_analysis'] as String?;

    final leftChildren = <Widget>[];

    // Explicitly read flat metrics
    final wordCount =
        widget.data['word_count_display'] ??
        widget.data['word_count']?.toString() ??
        '0';
    final avgLength =
        widget.data['avg_sentence_length_display'] ??
        widget.data['avg_sentence_length']?.toString() ??
        '0.0';
    final lexicalDiv =
        widget.data['lexical_diversity_display'] ??
        widget.data['lexical_diversity']?.toString() ??
        '0.0';

    leftChildren.add(
      Row(
        children: [
          Text(
            "${AppLocalizations.of(context)!.lblTextMetrics}:",
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          _buildHelpButton(context, "profiler"),
        ],
      ),
    );
    leftChildren.add(const SizedBox(height: 8));

    // Build a simple grid for text metrics using flat properties
    leftChildren.add(
      Wrap(
        spacing: 16,
        runSpacing: 16,
        children: [
          _buildMetricBlock(
            AppLocalizations.of(context)!.lblWordCount,
            wordCount,
          ),
          _buildMetricBlock("Lauseen keskipituus", avgLength),
          _buildMetricBlock("Sanaston kirjavuus", lexicalDiv),
        ],
      ),
    );

    final rightChildren = <Widget>[];

    if (profile != null) {
      rightChildren.add(
        _buildInfoCard("Psykologinen Profiili", profile, Icons.psychology),
      );
      rightChildren.add(const SizedBox(height: 8));
    }
    if (intent != null) {
      rightChildren.add(
        _buildInfoCard("Tekijän Intentio", intent, Icons.track_changes),
      );
    }

    // New additions for Automation Bias & Say-Do gap (Flat properties)
    final autoBiasLabel = widget.data['automation_bias_label'];
    final autoBiasColor =
        widget.data['automation_bias_color'] == 'red'
            ? Colors.red
            : Colors.green;

    final sayDoLabel = widget.data['say_do_gap_label'];
    final sayDoColor =
        widget.data['say_do_gap_color'] == 'red' ? Colors.red : Colors.green;

    if (autoBiasLabel != null || sayDoLabel != null) {
      leftChildren.add(const SizedBox(height: 16));
      leftChildren.add(
        Text(
          "Behavioral Indicators:",
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      );
      leftChildren.add(const SizedBox(height: 8));
      leftChildren.add(
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            if (autoBiasLabel != null)
              _buildStatusChip(
                context,
                label: "Automation Bias: $autoBiasLabel",
                color: autoBiasColor,
                icon: autoBiasColor == Colors.red ? Icons.warning : Icons.check,
              ),
            if (sayDoLabel != null)
              _buildStatusChip(
                context,
                label: "Say-Do Gap: $sayDoLabel",
                color: sayDoColor,
                icon: sayDoColor == Colors.red ? Icons.warning : Icons.check,
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
  // --- 5. FACT CHECK ---

  Widget _buildFactCheck(BuildContext context) {
    _validateRequiredKeys(['fact_checks', 'ethical_issues'], 'FACT_CHECK');
    // English Keys: fact_checks, ethical_issues
    final facts =
        (widget.data['fact_checks'] as List?)?.cast<Map<String, dynamic>>() ??
        [];

    final ethics =
        (widget.data['ethical_issues'] as List?)
            ?.cast<Map<String, dynamic>>() ??
        [];

    final ethicsChildren = <Widget>[];
    if (ethics.isNotEmpty) {
      ethicsChildren.add(
        Row(
          children: [
            Text(
              AppLocalizations.of(context)!.lblEthicalObservation,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(width: 8),
            _buildHelpButton(context, "fact_check"),
          ],
        ),
      );
      ethicsChildren.add(const SizedBox(height: 8));

      ethicsChildren.addAll(
        ethics.map<Widget>((e) {
          return Card(
            color:
                (e['is_critical'] == true ||
                        e['severity'] == "Kriittinen" ||
                        e['severity'] == "Critical")
                    ? Colors.red[100]
                    : Colors.white,
            child: ListTile(
              leading: const Icon(Icons.security, color: Colors.red),
              title: Text(
                e['label'] ??
                    e['issue_type'] ??
                    e['tyyppi'] ??
                    AppLocalizations.of(context)!.lblEthicalObservation,
                style:
                    (e['is_critical'] == true)
                        ? TextStyle(
                          color: Colors.red[900],
                          fontWeight: FontWeight.bold,
                        )
                        : null,
              ),
              subtitle: Text(e['description'] ?? e['kuvaus'] ?? ''),
              trailing: Text(e['severity'] ?? e['vakavuus'] ?? 'N/A'),
            ),
          );
        }),
      );
    }

    final factsChildren = <Widget>[];
    factsChildren.add(
      Row(
        children: [
          Text(
            AppLocalizations.of(context)!.lblFactCheck,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          _buildHelpButton(context, "fact_check"),
        ],
      ),
    );

    if (facts.isEmpty) {
      factsChildren.add(
        Padding(
          padding: const EdgeInsets.all(8),
          child: Text(AppLocalizations.of(context)!.lblNoFindings),
        ),
      );
    } else {
      factsChildren.addAll(
        facts.map<Widget>((f) {
          final resultKey =
              f['verification_result'] as String? ?? 'VER_UNCERTAIN';
          final statusText =
              f['label'] as String? ?? f['label_key'] as String? ?? resultKey;
          IconData i = Icons.help_outline;
          Color c = Colors.orange;

          if (resultKey == 'VER_VERIFIED') {
            i = Icons.check_circle;
            c = Colors.green;
          } else if (resultKey == 'VER_DEBUNKED') {
            i = Icons.cancel;
            c = Colors.red;
          }

          return ListTile(
            leading: Icon(i, color: c),
            title: Text(f['vaite'] ?? f['claim'] ?? ''),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  statusText,
                  style: TextStyle(
                    color: c,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                Text(f['lahde_tai_paattely'] ?? f['source'] ?? ''),
              ],
            ),
          );
        }),
      );
    }

    if (ethics.isEmpty)
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: factsChildren,
      );
    if (facts.isEmpty && ethics.isNotEmpty)
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: ethicsChildren,
      );

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

  // --- 6. PERFORMATIVITY CHECK ---
  Widget _buildPerformativityCheck(BuildContext context) {
    _validateRequiredKeys([
      'heuristics',
      'authenticity_assessment',
      'authenticity_score',
    ], 'PERFORMATIVITY_CHECK');
    // Strict V3 Keys
    final heuristics =
        (widget.data['heuristics'] as List?)?.cast<Map<String, dynamic>>() ??
        [];

    final overall = widget.data['authenticity_assessment'] as String?;

    final leftChildren = <Widget>[];
    if (overall != null) {
      final l10n = AppLocalizations.of(context)!;
      String displayAuth = overall;
      if (displayAuth == overall) {
        if (overall.contains("AUTH_ORGANIC"))
          displayAuth = l10n.authOrganic;
        else if (overall.contains("AUTH_PERFORMATIVE"))
          displayAuth = l10n.authPerformative;
        else if (overall.contains("AUTH_UNKNOWN"))
          displayAuth = l10n.authUnknown;
      }

      leftChildren.add(
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.purple[50]!, Colors.blue[50]!],
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              UnifiedMetricGauge(
                label: AppLocalizations.of(context)!.lblAuthenticity,
                value:
                    (widget.data['authenticity_score'] as num?)?.toDouble() ??
                    (overall.contains("AUTH_ORGANIC")
                        ? 3.0
                        : (overall.contains("AUTH_PERFORMATIVE") ? 2.0 : 1.0)),
                max: 3.0,
                description:
                    widget.data['authenticity_help'] ?? "Authenticity Help",
                displayValue:
                    "${(widget.data['authenticity_score'] as num?)?.toDouble() ?? '?'}/3.0",
                color: Colors.purple,
                axisLabels: [
                  AppLocalizations.of(context)!.authPerformative,
                  '',
                  AppLocalizations.of(context)!.authOrganic,
                ],
              ),
              const SizedBox(height: 8),
              Text(
                displayAuth,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      );
    }

    final rightChildren = <Widget>[];
    rightChildren.add(
      Row(
        children: [
          Text(
            "${AppLocalizations.of(context)!.lblHeuristics}:",
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(width: 8),
          _buildHelpButton(context, "performativity"),
        ],
      ),
    );

    rightChildren.add(
      Wrap(
        spacing: 8,
        runSpacing: 4,
        children:
            heuristics.map<Widget>((b) {
              final raised = b['flag'] == true;
              return Chip(
                label: Text(b['name'] ?? ''),
                avatar: Icon(
                  raised ? Icons.flag : Icons.check,
                  size: 16,
                  color: raised ? Colors.red : Colors.green,
                ),
                backgroundColor: raised ? Colors.red[50] : Colors.green[50],
                labelStyle: TextStyle(
                  fontSize: 12,
                  color: raised ? Colors.red[900] : Colors.green[900],
                ),
              );
            }).toList(),
      ),
    );

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

  // --- 7. ARCHIVIST CHECK ---
  Widget _buildArchivistCheck(BuildContext context) {
    // English Keys: compliance_score, consistency_analysis, precedents
    final score = widget.data['compliance_score'];
    final recs =
        (widget.data['recommendations'] ??
            widget.data['suositukset'] as List?) ??
        [];

    final analysis =
        widget.data['consistency_analysis'] ??
        widget.data['analysis'] as String?;

    double normalizedScore = 0;
    if (score is num) normalizedScore = score / 100.0;

    final leftChildren = <Widget>[];
    leftChildren.add(
      Container(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            UnifiedMetricGauge(
              label: AppLocalizations.of(context)!.lblComplianceAnalysis,
              value:
                  (score is num ? score.toDouble() : null) ??
                  (normalizedScore * 5.0),
              max: 5.0,
              description:
                  widget.data['help_archivist'] ??
                  widget.data['help_compliance'] ??
                  "Compliance Help",
              displayValue:
                  "${(score as num?)?.toDouble() ?? (normalizedScore * 5.0).toStringAsFixed(1)}/5.0",
              color: Colors.brown,
              axisLabels: const ['Heikko', '', '', '', '', 'Vahva'],
            ),
            const SizedBox(height: 8),
            Text(
              analysis != null && analysis.isNotEmpty
                  ? analysis
                  : "Ei analyysiä.",
            ),
          ],
        ),
      ),
    );

    final rightChildren = <Widget>[];
    rightChildren.addAll(
      recs.map<Widget>(
        (r) => ListTile(
          leading: const Icon(Icons.task_alt, size: 16, color: Colors.brown),
          title: Text(r.toString()),
          dense: true,
        ),
      ),
    );

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

  Widget _buildGenericMap(Map<String, dynamic> map) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          map.entries.map<Widget>((e) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "${e.key}: ",
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Expanded(child: Text(e.value.toString())),
                ],
              ),
            );
          }).toList(),
    );
  }

  Widget _buildInfoCard(
    String title,
    String? value,
    IconData icon, {
    String? subtitle,
    Color? color,
    String? helpKey,
  }) {
    if (value == null || value.trim().isEmpty) {
      throw FormatException("Missing value for InfoCard: '$title'");
    }

    return Semantics(
      excludeSemantics: Platform.isWindows,
      child: ExpansionTile(
        tilePadding: EdgeInsets.zero,
        title: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color ?? Colors.grey[100],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            children: [
              Icon(icon, size: 32, color: Colors.black54),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            fontSize: 12,
                            color: Colors.black54,
                          ),
                        ),
                        if (helpKey != null) _buildHelpButton(context, helpKey),
                      ],
                    ),
                    Text(
                      value,
                      style: const TextStyle(
                        fontSize: 16,
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
              padding: const EdgeInsets.only(left: 12, right: 12, bottom: 12),
              child: Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 12,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildComparisonBlock(String label, dynamic content, Color color) {
    final strContent = content?.toString() ?? '';
    if (strContent.trim().isEmpty) {
      throw FormatException("Missing content for ComparisonBlock: '$label'");
    }

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 4),
          Text(
            strContent,
            style: const TextStyle(fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildLabelValue(String label, dynamic value) {
    final strValue = value?.toString() ?? '';
    if (strValue.trim().isEmpty) {
      throw FormatException("Missing value for LabelValue: '$label'");
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: Colors.grey,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(strValue, style: const TextStyle(fontSize: 14)),
      ],
    );
  }

  Widget _buildRawJsonView() {
    final jsonStr = const JsonEncoder.withIndent('  ').convert(widget.data);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF2d2d2d),
        borderRadius: BorderRadius.circular(4),
      ),
      child: SelectableText(jsonStr, style: const TextStyle()),
    );
  }

  Widget _buildHelpButton(BuildContext context, String key) {
    // Strict Mode: Help text must be provided by backend in the data payload.
    // Keys are typically "help_key" or just "key_help".
    // We try both common patterns.
    final text =
        widget.data[key] ??
        widget.data['help_$key'] ??
        widget.data['${key}_help'] ??
        "";
    if (text.isEmpty) return const SizedBox.shrink();

    return IconButton(
      icon: Icon(Icons.help_outline, size: 18, color: Colors.grey[400]),
      onPressed: () {
        showDialog(
          context: context,
          builder:
              (ctx) => AlertDialog(
                title: Row(
                  children: [
                    const Icon(Icons.info_outline, color: Colors.blue),
                    const SizedBox(width: 8),
                    const Text(
                      "Tietoa Mittarista",
                      style: TextStyle(fontSize: 16),
                    ),
                  ],
                ),
                content: Text(text, style: const TextStyle(height: 1.5)),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text("OK"),
                  ),
                ],
              ),
        );
      },
      tooltip: "Lisätietoa",
    );
  }

  // --- 8. DRIVER PROFILE (Interaction) ---
  Widget _buildDriverProfile(BuildContext context) {
    _validateRequiredKeys([
      'role_classification',
      'high_dependency',
      'imperative_command_count',
      'strategy',
    ], "Driver Profile");
    final roleRaw = widget.data['role_classification'] as String;
    final ratio = widget.data['input_control_ratio'];

    final cmdCount = widget.data['imperative_command_count'] as int;
    final isHighDependency = widget.data['high_dependency'] as bool;
    final strategyRaw = widget.data['strategy'] as String;
    final strategies = [strategyRaw];

    final l10n = AppLocalizations.of(context)!;

    // Strict Enum: Use ROLE_DRIVER etc.
    // If raw is "Driver", we map to "ROLE_DRIVER".
    // Backend creates "driver_display" with "classification" containing strict keys (lines 600+ BFF).
    // Let's rely on that if available, or map raw.

    String roleKey = roleRaw;
    if (!roleKey.startsWith("ROLE_")) {
      // Fallback for unexpected raw strings
      roleKey = "ROLE_${roleRaw.toUpperCase()}";
    }

    final role = roleKey;

    // Spectrum Definitions
    final roles = [
      l10n.rolePassenger,
      l10n.roleNavigator,
      l10n.roleDriver,
      l10n.roleArchitect,
    ];

    // If Ratio is 0 but role is Active, we still want to show it (e.g. 0% is valid data)
    final showRatio = ratio != null;

    final leftChildren = <Widget>[];
    leftChildren.add(
      Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.blue[50],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.blue[100]!),
        ),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  AppLocalizations.of(context)!.lblRoleAndPosition,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(width: 8),
                _buildHelpButton(context, "control_ratio"),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              showRatio ? "${(ratio! * 100).toStringAsFixed(0)}%" : "N/A",
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 32,
                color: Colors.blue,
              ),
            ),
            Text(
              showRatio
                  ? AppLocalizations.of(context)!.lblControlRatio
                  : "Osuus",
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 24),
            LayoutBuilder(
              builder: (context, constraints) {
                return Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children:
                      roles.map((r) {
                        final isActive = role.toLowerCase() == r.toLowerCase();
                        return Expanded(
                          child: Column(
                            children: [
                              AnimatedContainer(
                                duration: const Duration(milliseconds: 300),
                                height: isActive ? 12 : 8,
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 2,
                                ),
                                decoration: BoxDecoration(
                                  color:
                                      isActive ? Colors.blue : Colors.grey[300],
                                  borderRadius: BorderRadius.circular(4),
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                r,
                                style: TextStyle(
                                  fontSize: isActive ? 12 : 10,
                                  fontWeight:
                                      isActive
                                          ? FontWeight.bold
                                          : FontWeight.normal,
                                  color:
                                      isActive
                                          ? Colors.blue[800]
                                          : Colors.grey[500],
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                );
              },
            ),
          ],
        ),
      ),
    );

    final rightChildren = <Widget>[];
    if (strategies.isNotEmpty) {
      rightChildren.add(
        const Text(
          "Tunnistetut Strategiat:",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      );
      rightChildren.add(const SizedBox(height: 8));
      rightChildren.add(
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            for (final s in strategies)
              Chip(
                label: Text(s.toString()),
                backgroundColor: Colors.blue[50],
              )
          ],
        ),
      );
      rightChildren.add(const SizedBox(height: 16));
    }

    if (isHighDependency) {
      rightChildren.add(
        Chip(
          label: const Text(
            "High Dependency",
            style: TextStyle(color: Colors.white),
          ),
          backgroundColor: Colors.orange[600],
          avatar: const Icon(
            Icons.warning_amber_rounded,
            color: Colors.white,
            size: 16,
          ),
        ),
      );
      rightChildren.add(const SizedBox(height: 12));
    }

    rightChildren.add(
      Text(
        "Suoria käskyjä (Imperative): $cmdCount",
        style: TextStyle(color: Colors.grey[700], fontStyle: FontStyle.italic),
      ),
    );
    rightChildren.add(const SizedBox(height: 12));

    if (widget.data['compliance_analysis'] != null) {
      rightChildren.add(
        _buildComparisonBlock(
          "Linjakkuus",
          widget.data['compliance_analysis'] ?? 'N/A',
          Colors.blue[50]!,
        ),
      );
      rightChildren.add(const SizedBox(height: 8));
    }

    if (widget.data['poikkeamat_linjasta'] != null) {
      rightChildren.add(
        _buildInfoCard(
          "Poikkeamat Linjasta",
          widget.data['poikkeamat_linjasta'],
          Icons.call_split,
          color: Colors.white,
        ),
      );
      rightChildren.add(const SizedBox(height: 8));
    }

    if (widget.data['suositus_tuomarille'] != null) {
      rightChildren.add(
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.green[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.green[100]!),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: const [
                  Icon(Icons.recommend, color: Colors.green),
                  SizedBox(width: 8),
                  Text(
                    "Suositus Tuomarille",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.green,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                widget.data['suositus_tuomarille'],
                style: const TextStyle(fontSize: 14),
              ),
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

  // NEW: Compact Text Metrics for Logic Analysis (Teal Theme)
  Widget _buildCompactTextMetrics(
    BuildContext context,
    Map<String, dynamic> metrics,
  ) {
    final l10n = AppLocalizations.of(context)!;

    double _safeDouble(dynamic value) {
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
        _safeDouble(metrics['lexical_diversity']).toStringAsFixed(2);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.teal[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.teal[100]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.bar_chart, size: 16, color: Colors.teal),
              const SizedBox(width: 8),
              Text(
                "${l10n.lblTextMetrics}",
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                  color: Colors.teal,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildCompactMetricItem(l10n.lblWordCount, "$wordCount"),
              _buildCompactMetricItem(l10n.lblSentenceCount, "$sentCount"),
              _buildCompactMetricItem(l10n.lblLexicalDiversity, "$lexDiv"),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCompactMetricItem(String label, String value) {
    return Column(
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            fontSize: 9,
            color: Colors.teal,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: Colors.teal,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricBlock(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: Colors.indigo,
          ),
        ),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}
