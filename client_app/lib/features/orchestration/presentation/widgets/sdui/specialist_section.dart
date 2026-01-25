import 'package:client_app/features/orchestration/domain/models/report_view.dart';
import 'package:client_app/features/orchestration/presentation/widgets/sdui/generic_table.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/score_card_radar.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/logic_matrix_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:fl_chart/fl_chart.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class SpecialistSection extends StatefulWidget {
  final String title;
  final String type; // e.g. LOGIC_ANALYSIS, STRESS_TEST
  final Map<String, dynamic> data;

  const SpecialistSection({
    super.key,
    required this.title,
    required this.type,
    required this.data,
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
                _showRaw ? CrossFadeState.showSecond : CrossFadeState.showFirst,
            duration: const Duration(milliseconds: 300),
          ),
        ],
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
      default:
        // Fallback to generic map renderer if type is barely supported
        return _buildGenericMap(widget.data);
    }
  }

  // --- 1. LOGIC ANALYSIS (Toulmin & Cognitive) ---
  Widget _buildLogicAnalysis(BuildContext context) {
    // Keys match LogicianAgent output schema (v2.0)
    // "kognitiivinen_taso" is the canonical key. "kognitiivinen_analyysi" is legacy.
    final cog =
        (widget.data['kognitiivinen_taso'] ??
                widget.data['kognitiivinen_analyysi'])
            as Map<String, dynamic>? ??
        {};
    final toulmin =
        (widget.data['toulmin_analyysi'] as List?)
            ?.cast<Map<String, dynamic>>() ??
        [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.data['metodologinen_loki'] != null) ...[
          _buildInfoCard(
            AppLocalizations.of(context)!.lblMethodologicalLog,
            widget.data['metodologinen_loki'],
            Icons.history_edu,
            helpKey: "metodologia",
          ),
          const SizedBox(height: 16),
        ],

        // Responsive Layout for Bloom & Toulmin
        LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth > 800;

            // Enhanced Bloom Widget (Report Style)
            final bloomWidget =
                cog.isNotEmpty
                    ? Card(
                      color: Colors.teal[50], // Distinct color for Cognitive
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(
                                  Icons.psychology,
                                  color: Colors.teal,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    "${AppLocalizations.of(context)!.lblCognitiveLevel}: ${cog['bloom_taso'] ?? 'N/A'}",
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
                              AppLocalizations.of(context)!.lblStrategicDepth,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                                color: Colors.grey,
                              ),
                            ),
                            const SizedBox(height: 4),
                            SelectableText(
                              cog['strateginen_syvyys'] ?? "Ei analyysiä.",
                              style: const TextStyle(fontSize: 14, height: 1.5),
                            ),
                          ],
                        ),
                      ),
                    )
                    : const SizedBox.shrink();

            final toulminWidget =
                toulmin.isNotEmpty
                    ? Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              AppLocalizations.of(context)!.lblArguments,
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            _buildHelpButton(context, "toulmin"),
                          ],
                        ),
                        const SizedBox(height: 8),
                        ...toulmin
                            .map(
                              (t) => Card(
                                margin: const EdgeInsets.only(bottom: 8),
                                color: Colors.indigo[50],
                                child: Padding(
                                  padding: const EdgeInsets.all(12),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      _buildLabelValue(
                                        "Väite (Claim)",
                                        t['claim'],
                                      ),
                                      const SizedBox(height: 4),
                                      const Divider(),
                                      const SizedBox(height: 4),
                                      _buildLabelValue(
                                        "Perustelu (Warrant)",
                                        t['warrant'],
                                      ),
                                      if (t['backing'] != null) ...[
                                        const SizedBox(height: 4),
                                        _buildLabelValue(
                                          "Tuki (Backing)",
                                          t['backing'],
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                              ),
                            )
                            .toList(),
                      ],
                    )
                    : const SizedBox.shrink();

            // New Visualization Widget
            final matrixChart = LogicMatrixChart(
              bloomLevel: cog['bloom_taso'] as String? ?? 'N/A',
              toulminArguments: toulmin,
            );

            if (isWide) {
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Left Column: Text Analysis
                  Expanded(
                    flex: 1,
                    child: Column(
                      children: [
                        bloomWidget,
                        if (cog.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          _buildValidationScoreCard(
                            AppLocalizations.of(context)!.lblBloomScore,
                            _calculateBloomScore(cog['bloom_taso'] ?? 'N/A'),
                            6.0,
                          ),
                        ],
                        const SizedBox(height: 16),
                        toulminWidget,
                        if (toulmin.isNotEmpty) ...[
                          const SizedBox(height: 8),
                          _buildValidationScoreCard(
                            AppLocalizations.of(context)!.lblToulminScore,
                            _calculateToulminScore(toulmin),
                            6.0,
                          ),
                        ],
                        // WALTON SECTION
                        if (widget.data['walton_skeema'] != null) ...[
                          const SizedBox(height: 16),
                          _buildWaltonSection(widget.data['walton_skeema']),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),

                  // Right Column: Matrix Visualization
                  Expanded(
                    flex: 1,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: Colors.grey.withValues(alpha: 0.2),
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            AppLocalizations.of(context)!.lblLogicMatrix ??
                                "Logiikkamatriisi",
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          Text(
                            AppLocalizations.of(context)!.lblMatrixSubtitle ??
                                "Visuaalinen analyysi päättelyn laadusta.",
                            style: const TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                          const SizedBox(height: 16),
                          matrixChart,
                        ],
                      ),
                    ),
                  ),
                ],
              );
            } else {
              // Mobile / Narrow: Stacked
              return Column(
                children: [
                  matrixChart,
                  const SizedBox(height: 16),
                  bloomWidget,
                  const SizedBox(height: 16),
                  toulminWidget,
                ],
              );
            }
          },
        ),
      ],
    );
  }

  // --- 2. STRESS TEST (Falsifier) ---
  Widget _buildStressTest(BuildContext context) {
    final findings =
        widget.data['walton_stressitesti_loydokset'] as List<dynamic>? ?? [];
    final fidelity =
        widget.data['paattelyketjun_uskollisuus_auditointi']
            as Map<String, dynamic>? ??
        {};

    return Column(
      children: [
        if (fidelity.isNotEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.orange[50],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Text(
                          AppLocalizations.of(context)!.lblFidelity,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        _buildHelpButton(context, "stress_test"),
                      ],
                    ),
                    _buildSignalMeter(fidelity['uskollisuus_score']),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  fidelity['onko_post_hoc_rationalisointia'] == true
                      ? AppLocalizations.of(context)!.lblPostHocWarning
                      : AppLocalizations.of(context)!.lblNoRationalization,
                  style: TextStyle(
                    color:
                        fidelity['onko_post_hoc_rationalisointia'] == true
                            ? Colors.red[800]
                            : Colors.green[800],
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        const SizedBox(height: 16),
        ...findings.map((f) {
          final passed = f['kestiko_todistusaineisto'] == true;
          return ListTile(
            leading: CircleAvatar(
              backgroundColor: passed ? Colors.green : Colors.red,
              child: Icon(
                passed ? Icons.check : Icons.close,
                color: Colors.white,
                size: 16,
              ),
            ),
            title: Text(f['kysymys'] ?? ''),
            subtitle: Text(f['havainto'] ?? ''),
            dense: true,
          );
        }).toList(),
      ],
    );
  }

  // --- 3. CAUSAL ANALYSIS ---
  Widget _buildCausalAnalysis(BuildContext context) {
    // ... (Keep existing implementation or minimal tweaks)
    final simul =
        widget.data['kontrafaktuaalinen_testi'] as Map<String, dynamic>? ?? {};
    final abd = widget.data['abduktiivinen_paatelma'] as String?;

    return Column(
      children: [
        if (abd != null)
          _buildInfoCard(
            AppLocalizations.of(context)!.lblAbductiveReasoning,
            abd,
            Icons.lightbulb_outline,
            color: Colors.teal[50],
            helpKey: "causal",
          ),
        const SizedBox(height: 16),

        if (simul.isNotEmpty)
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: _buildComparisonBlock(
                  AppLocalizations.of(context)!.lblScenarioActual,
                  simul['skenaario_A_toteutunut'],
                  Colors.grey[200]!,
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.arrow_forward),
              const SizedBox(width: 8),
              Expanded(
                child: _buildComparisonBlock(
                  AppLocalizations.of(context)!.lblScenarioSimulation,
                  simul['skenaario_B_simulaatio'],
                  Colors.teal[100]!,
                ),
              ),
            ],
          ),
        if (simul['uskottavuus_arvio'] != null)
          Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Text(
              "${AppLocalizations.of(context)!.lblCredibility}: ${simul['uskottavuus_arvio']}",
              style: const TextStyle(fontStyle: FontStyle.italic),
            ),
          ),
      ],
    );
  }

  // --- 4. PROFILER ANALYSIS ---
  Widget _buildProfilerAnalysis(BuildContext context) {
    final biases = widget.data['tunnistetut_vinoumat'] as List<dynamic>? ?? [];
    final profile = widget.data['psykologinen_profiili'] as String?;
    final intent = widget.data['intentio_analyysi'] as String?;
    final metrics =
        widget.data['teksti_metriikka'] as Map<String, dynamic>? ?? {};

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (metrics.isNotEmpty) ...[
          Row(
            children: [
              Text(
                "${AppLocalizations.of(context)!.lblTextMetrics}:",
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              _buildHelpButton(context, "profiler"),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _buildMetricMeter(
                  "Sanaston monipuolisuus",
                  metrics['lexical_diversity'],
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildMetricMeter(
                  "Huuto/Kapitalisaatio",
                  metrics['capitalization_ratio'],
                  inverseBad: true,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
        ],

        if (biases.isNotEmpty) ...[
          Text(
            "${AppLocalizations.of(context)!.lblBias}:",
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children:
                biases
                    .map(
                      (b) => Chip(
                        label: Text(b['nimi'] ?? 'Vinouma'),
                        avatar: const Icon(
                          Icons.warning_amber_rounded,
                          size: 16,
                        ),
                        backgroundColor: Colors.pink[50],
                        labelStyle: const TextStyle(fontSize: 12),
                      ),
                    )
                    .toList(),
          ),
          const SizedBox(height: 16),
        ],
        if (intent != null)
          _buildInfoCard(
            AppLocalizations.of(context)!.lblIntent,
            intent,
            Icons.ads_click,
            color: Colors.blue[50],
          ),
        const SizedBox(height: 8),
        if (profile != null)
          _buildInfoCard(
            AppLocalizations.of(context)!.lblPsychProfile,
            profile,
            Icons.person_outline,
          ),
      ],
    );
  }

  // --- 5. FACT CHECK ---
  Widget _buildFactCheck(BuildContext context) {
    final facts = widget.data['faktantarkistus_rfi'] as List<dynamic>? ?? [];
    final ethics = widget.data['eettiset_havainnot'] as List<dynamic>? ?? [];

    return Column(
      children: [
        if (ethics.isNotEmpty) ...[
          ...ethics.map((e) {
            // Defensive Check: If LLM returns strings instead of objects
            if (e is! Map) {
              return Card(
                color: Colors.red[50],
                child: ListTile(
                  leading: const Icon(
                    Icons.warning_amber,
                    color: Colors.orange,
                  ),
                  title: const Text('Eettinen Huomio (Muu muoto)'),
                  subtitle: Text(e.toString()),
                ),
              );
            }

            return Card(
              color: Colors.red[50],
              child: ListTile(
                leading: const Icon(Icons.security, color: Colors.red),
                title: Text(
                  e['tyyppi'] ??
                      AppLocalizations.of(context)!.lblEthicalObservation,
                ),
                subtitle: Text(e['kuvaus'] ?? ''),
                trailing: Chip(
                  label: Text(e['vakavuus'] ?? 'N/A'),
                  backgroundColor: Colors.white,
                ),
              ),
            );
          }).toList(),
          const SizedBox(height: 16),
        ],
        Row(
          children: [
            Text(
              AppLocalizations.of(context)!.lblFactCheck,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            _buildHelpButton(context, "fact_check"),
          ],
        ),
        if (facts.isEmpty)
          const Padding(
            padding: EdgeInsets.all(8),
            child: Text("Ei faktantarkistuspyyntöjä."),
          ),
        ...facts.map((f) {
          // Defensive Check
          if (f is! Map) {
            return ListTile(
              leading: const Icon(Icons.error_outline, color: Colors.grey),
              title: Text(f.toString()),
            );
          }

          final status = f['verifiointi_tulos'];
          Color c = Colors.grey;
          IconData i = Icons.help_outline;
          if (status == 'Vahvistettu') {
            c = Colors.green;
            i = Icons.check_circle;
          }
          if (status == 'Kumottu') {
            c = Colors.red;
            i = Icons.cancel;
          }

          return ListTile(
            leading: Icon(i, color: c),
            title: Text(f['vaite'] ?? ''),
            subtitle: Text(f['lahde_tai_paattely'] ?? ''),
          );
        }).toList(),
      ],
    );
  }

  // --- 6. PERFORMATIVITY CHECK ---
  Widget _buildPerformativityCheck(BuildContext context) {
    final heuristics =
        widget.data['performatiivisuus_heuristiikat'] as List<dynamic>? ?? [];
    final overall = widget.data['yleisarvio_aitoudesta'] as String?;

    return Column(
      children: [
        if (overall != null)
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      AppLocalizations.of(context)!.lblAuthenticity,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildHelpButton(context, "performativity"),
                  ],
                ),
                const SizedBox(height: 8),
                _buildAuthenticityMeter(overall),
              ],
            ),
          ),
        const SizedBox(height: 16),
        Text(
          "${AppLocalizations.of(context)!.lblHeuristics}:",
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children:
              heuristics.map((b) {
                final raised = b['lippu_nostettu'] == true;
                return Chip(
                  label: Text(b['heuristiikka'] ?? ''),
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
      ],
    );
  }

  // --- 7. ARCHIVIST CHECK ---
  Widget _buildArchivistCheck(BuildContext context) {
    final score = widget.data['compliance_score'];
    final recs = widget.data['recommendations'] as List<dynamic>? ?? [];
    final analysis = widget.data['analysis'] as String?;

    double normalizedScore = 0;
    if (score is num) normalizedScore = score / 100.0;

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              SizedBox(
                height: 100,
                width: 100,
                child: Stack(
                  children: [
                    Center(
                      child: SizedBox(
                        height: 80,
                        width: 80,
                        child: CircularProgressIndicator(
                          value: normalizedScore,
                          color: _getColorForScore(normalizedScore),
                          backgroundColor: Colors.grey[200],
                          strokeWidth: 10,
                          strokeCap: StrokeCap.round,
                        ),
                      ),
                    ),
                    Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            "${score ?? '?'}",
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 24,
                            ),
                          ),
                          const Text(
                            "Score",
                            style: TextStyle(fontSize: 10, color: Colors.grey),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          AppLocalizations.of(context)!.lblComplianceAnalysis,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        _buildHelpButton(context, "archivist"),
                      ],
                    ),
                    const SizedBox(height: 4),
                    // Handle "ei analyysiä" case if null or empty, or explicitly suppressed
                    Text(
                      analysis != null && analysis.isNotEmpty
                          ? analysis
                          : "Ei analyysiä.",
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        ...recs
            .map(
              (r) => ListTile(
                leading: const Icon(
                  Icons.task_alt,
                  size: 16,
                  color: Colors.brown,
                ),
                title: Text(r.toString()),
                dense: true,
              ),
            )
            .toList(),
      ],
    );
  }

  // --- HELPERS & METERS ---

  Widget _buildSignalMeter(dynamic score) {
    // Score expected: KORKEA, EPÄVARMA, HEIKKO
    int level = 0;
    Color color = Colors.grey;
    if (score == 'KORKEA') {
      level = 3;
      color = Colors.green;
    } else if (score == 'EPÄVARMA') {
      level = 2;
      color = Colors.orange;
    } else if (score == 'HEIKKO') {
      level = 1;
      color = Colors.red;
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildSignalBar(1, level, color),
        const SizedBox(width: 2),
        _buildSignalBar(2, level, color),
        const SizedBox(width: 2),
        _buildSignalBar(3, level, color),
        const SizedBox(width: 8),
        Text(
          score.toString(),
          style: TextStyle(fontWeight: FontWeight.bold, color: color),
        ),
      ],
    );
  }

  Widget _buildSignalBar(int barIndex, int currentLevel, Color color) {
    final active = barIndex <= currentLevel;
    return Container(
      width: 8,
      height: 8.0 + (barIndex * 6), // Ascending height
      decoration: BoxDecoration(
        color: active ? color : Colors.grey[300],
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }

  Widget _buildAuthenticityMeter(String riskLevel) {
    // Orgaaninen, Performatiivinen, Epäilyttävä
    double value = 0.5;
    Color color = Colors.grey;
    String label = riskLevel;

    if (riskLevel == 'Orgaaninen') {
      value = 1.0;
      color = Colors.green;
    }
    if (riskLevel == 'Performatiivinen') {
      value = 0.5;
      color = Colors.purple;
    }
    if (riskLevel == 'Epäilyttävä') {
      value = 0.1;
      color = Colors.red;
    }

    return Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: LinearProgressIndicator(
            value: value,
            minHeight: 12,
            backgroundColor: Colors.grey[300],
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(color: color, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Color _getColorForScore(double value) {
    if (value >= 0.8) return Colors.green;
    if (value >= 0.5) return Colors.orange;
    return Colors.red;
  }

  Widget _buildMetricMeter(
    String label,
    dynamic value, {
    bool inverseBad = false,
  }) {
    double v = 0.0;
    if (value is num) v = value.toDouble();
    if (v > 1.0) v = 1.0; // clamp
    if (v < 0) v = 0;

    Color color = Colors.blue;
    if (inverseBad) {
      if (v > 0.3) color = Colors.orange;
      if (v > 0.7) color = Colors.red;
    } else {
      if (v < 0.3) color = Colors.orange;
      if (v < 0.1) color = Colors.red;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 10,
                color: Colors.grey,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              (v * 100).toStringAsFixed(0) + "%",
              style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: v,
            minHeight: 6,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }

  Widget _buildGenericMap(Map<String, dynamic> map) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          map.entries
              .map(
                (e) => Padding(
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
                ),
              )
              .toList(),
    );
  }

  Widget _buildInfoCard(
    String title,
    String value,
    IconData icon, {
    String? subtitle,
    Color? color,
    String? helpKey,
  }) {
    return Container(
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
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonBlock(String label, dynamic content, Color color) {
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
            content.toString(),
            style: const TextStyle(fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildLabelValue(String label, dynamic value) {
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
        Text(value.toString(), style: const TextStyle(fontSize: 14)),
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

  String _getHelpText(BuildContext context, String key) {
    final l10n = AppLocalizations.of(context)!;
    switch (key) {
      case "bloom":
        return l10n.helpBloom;
      case "toulmin":
        return l10n.helpToulmin;
      case "walton":
        return l10n.helpWalton;
      case "control_ratio":
        return l10n.helpControlRatio;
      case "metodologia":
        return l10n.helpMethodology;
      case "stress_test":
        return l10n.helpStressTest;
      case "causal":
        return l10n.helpCausal;
      case "profiler":
        return l10n.helpProfiler;
      case "fact_check":
        return l10n.helpFactCheck;
      case "performativity":
        return l10n.helpPerformativity;
      case "archivist":
        return l10n.helpArchivist;
      default:
        return "";
    }
  }

  Widget _buildHelpButton(BuildContext context, String key) {
    final text = _getHelpText(context, key);
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
    final roleRaw = widget.data['driver_classification'] as String? ?? 'N/A';
    final ratio = widget.data['input_control_ratio'];
    final strategies =
        widget.data['tunnistetut_strategiat'] as List<dynamic>? ?? [];
    final l10n = AppLocalizations.of(context)!;
    final role = _getLocalizedRole(roleRaw, l10n);

    // Spectrum Definitions
    final roles = [
      l10n.rolePassenger,
      l10n.roleNavigator,
      l10n.roleDriver,
      l10n.roleArchitect,
    ];

    // Clean up role string for check
    final rLower = roleRaw.toLowerCase();
    final isPassive =
        rLower.contains('matkustaja') || rLower.contains('passenger');

    // If Ratio is 0 but role is Active, we still want to show it (e.g. 0% is valid data)
    final showRatio = ratio != null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue.withOpacity(0.2)),
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
                (showRatio ? "${(ratio! * 100).toStringAsFixed(0)}%" : "N/A"),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 32,
                  color: Colors.blue,
                ),
              ),
              Text(
                AppLocalizations.of(context)!.lblControlRatio,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),

              const SizedBox(height: 24),

              // SPECTRUM VISUALIZATION
              LayoutBuilder(
                builder: (context, constraints) {
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children:
                        roles.map((r) {
                          final isActive =
                              role.toLowerCase() == r.toLowerCase();
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
                                        isActive
                                            ? Colors.blue
                                            : Colors.grey[300],
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

        const SizedBox(height: 16),

        // Strategies
        if (strategies.isNotEmpty) ...[
          const Text(
            "Tunnistetut Strategiat:",
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children:
                strategies.map((s) {
                  final label =
                      s is String ? s : (s['nimi'] ?? s['name'] ?? 'Strategia');
                  return Chip(
                    label: Text(label.toString()),
                    backgroundColor: Colors.blue[50],
                  );
                }).toList(),
          ),
          const SizedBox(height: 16),
        ],

        // Coherence Analysis (Linjakkuus)
        if (widget.data['linjakkuus_analyysi'] != null) ...[
          _buildInfoCard(
            "Linjakkuus (Coherence)",
            widget.data['linjakkuus_analyysi'],
            Icons.linear_scale,
            color: Colors.white,
          ),
          const SizedBox(height: 8),
        ],

        // Deviations (Poikkeamat)
        if (widget.data['poikkeamat_linjasta'] != null) ...[
          _buildInfoCard(
            "Poikkeamat Linjasta",
            widget.data['poikkeamat_linjasta'],
            Icons.call_split,
            color: Colors.white, // Use white to align with above card
          ),
          const SizedBox(height: 8),
        ],

        // Recommendation (Suositus)
        if (widget.data['suositus_tuomarille'] != null) ...[
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.green[50], // Highlight recommendation
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.green.withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
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
        ],
      ],
    );
  }

  Widget _buildProfileIcon(String role) {
    IconData icon = Icons.person;
    if (role.toLowerCase().contains("driver") ||
        role.toLowerCase().contains("ohjaaja"))
      icon = Icons.directions_car;
    if (role.toLowerCase().contains("passenger") ||
        role.toLowerCase().contains("matkustaja"))
      icon = Icons.airline_seat_recline_normal;

    return Column(
      children: [
        Icon(icon, size: 48, color: Colors.blue),
        const SizedBox(height: 8),
        Text(role, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }

  // LOGIC HELPERS
  double _calculateBloomScore(String level) {
    final lower = level.toLowerCase();
    if (lower.contains("luominen") || lower.contains("creating")) return 5.5;
    if (lower.contains("arviointi") || lower.contains("evaluating")) return 4.5;
    if (lower.contains("analysointi") || lower.contains("analyzing"))
      return 3.5;
    if (lower.contains("soveltaminen") || lower.contains("applying"))
      return 2.5;
    if (lower.contains("ymmärtäminen") || lower.contains("understanding"))
      return 1.5;
    if (lower.contains("muistaminen") || lower.contains("remembering"))
      return 0.5;
    return 3.0; // Default
  }

  double _calculateToulminScore(List<dynamic> args) {
    if (args.isEmpty) return 0.0;
    double totalScore = 0;
    for (final arg in args) {
      double score = 1.0; // Base: Claim
      if (arg['warrant'] != null && arg['warrant'].toString().length > 5)
        score += 2.0;
      if (arg['backing'] != null && arg['backing'].toString().length > 5)
        score += 2.0;
      totalScore += score;
    }
    final avg = totalScore / args.length;
    return avg > 6.0 ? 6.0 : avg; // Cap at 6
  }

  Widget _buildValidationScoreCard(String title, double score, double max) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.green[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: Colors.green,
            ),
          ),
          Text(
            "${score.toStringAsFixed(1)} / ${max.toStringAsFixed(1)}",
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _buildWaltonSection(Map<String, dynamic> walton) {
    final scheme = walton['tunnistettu_skeema'] ?? 'N/A';
    final questions = (walton['kriittiset_kysymykset'] as List?) ?? [];

    return Card(
      color: Colors.purple[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.balance, color: Colors.purple),
                const SizedBox(width: 8),
                Text(
                  AppLocalizations.of(context)!.lblWaltonScheme,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: Colors.purple,
                  ),
                ),
                if (walton.isNotEmpty) const Spacer(),
                _buildHelpButton(context, "walton"),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              scheme,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
            if (questions.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Text(
                "${AppLocalizations.of(context)!.lblCriticalQuestions}:",
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
              ...questions.map(
                (q) => Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "• ",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.purple,
                        ),
                      ),
                      Expanded(
                        child: Text(
                          q.toString(),
                          style: const TextStyle(fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _getLocalizedRole(String raw, AppLocalizations l10n) {
    final r = raw.toLowerCase();
    if (r.contains("matkustaja") || r.contains("passenger"))
      return l10n.rolePassenger;
    if (r.contains("kartanlukija") || r.contains("navigator"))
      return l10n.roleNavigator;
    if (r.contains("kuski") || r.contains("driver")) return l10n.roleDriver;
    if (r.contains("arkkitehti") || r.contains("architect"))
      return l10n.roleArchitect;
    return raw;
  }
}
