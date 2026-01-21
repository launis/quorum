
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:fl_chart/fl_chart.dart';

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
                icon: Icon(_showRaw ? Icons.visibility_off : Icons.code, size: 16),
                label: Text(_showRaw ? 'Piilota Raaka-Data' : 'JSON', style: const TextStyle(fontSize: 12)),
              ),
              IconButton(
                icon: const Icon(Icons.copy, size: 16),
                onPressed: () {
                   final jsonStr = const JsonEncoder.withIndent('  ').convert(widget.data);
                   Clipboard.setData(ClipboardData(text: jsonStr));
                   ScaffoldMessenger.of(context).showSnackBar(
                     const SnackBar(content: Text('JSON kopioitu leikepöydälle'), duration: Duration(seconds: 1)),
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
             crossFadeState: _showRaw ? CrossFadeState.showSecond : CrossFadeState.showFirst,
             duration: const Duration(milliseconds: 300),
          )
        ],
      ),
    );
  }

  Icon _buildIconForType() {
    switch (widget.type) {
      case 'LOGIC_ANALYSIS': return const Icon(Icons.psychology, color: Colors.indigo);
      case 'STRESS_TEST': return const Icon(Icons.fitness_center, color: Colors.orange);
      case 'CAUSAL_ANALYSIS': return const Icon(Icons.compare_arrows, color: Colors.teal);
      case 'PERFORMATIVITY_CHECK': return const Icon(Icons.theater_comedy, color: Colors.purple);
      case 'FACT_CHECK': return const Icon(Icons.fact_check, color: Colors.blue);
      case 'PROFILER_ANALYSIS': return const Icon(Icons.face, color: Colors.pinkAccent);
      case 'ARCHIVIST_CHECK': return const Icon(Icons.gavel, color: Colors.brown);
      default: return const Icon(Icons.extension, color: Colors.grey);
    }
  }

  String _getSubtitleForType() {
     switch (widget.type) {
      case 'LOGIC_ANALYSIS': return "Toulmin & Kognitiivinen Taso";
      case 'STRESS_TEST': return "Walton Falsifiointi";
      case 'CAUSAL_ANALYSIS': return "Kausaalinen & Kontrafaktuaalinen";
      case 'PERFORMATIVITY_CHECK': return "Aitous & Pre-Mortem";
      case 'FACT_CHECK': return "Hallusinaatiot & Etiikka";
      case 'PROFILER_ANALYSIS': return "Vinoumat & Psyko-profiili";
      case 'ARCHIVIST_CHECK': return "Compliance & Ennakkotapaukset";
      default: return "";
    }
  }

  Widget _buildSummaryView(BuildContext context) {
    if (widget.data.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(8.0),
        child: Text("Ei dataa saatavilla.", style: TextStyle(fontStyle: FontStyle.italic)),
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
      default:
        // Fallback to generic map renderer if type is barely supported
        return _buildGenericMap(widget.data);
    }
  }
  
  // --- 1. LOGIC ANALYSIS (Toulmin) ---
  Widget _buildLogicAnalysis(BuildContext context) {
    final toulmin = widget.data['toulmin_analyysi'] as List<dynamic>? ?? [];
    final cog = widget.data['kognitiivinen_taso'] as Map<String, dynamic>? ?? {};
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (cog.isNotEmpty) ...[
           _buildInfoCard(
             "Kognitiivinen Taso (Bloom)", 
             cog['bloom_taso'] ?? 'N/A', 
             Icons.school,
             subtitle: cog['strateginen_syvyys']
           ),
           const SizedBox(height: 16),
        ],
        
        const Text("Argumentaatio (Toulmin)", style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        ...toulmin.map((t) => Card(
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
                   ]
                 ],
             ),
           ),
        )).toList()
      ],
    );
  }

  // --- 2. STRESS TEST (Falsifier) ---
  Widget _buildStressTest(BuildContext context) {
     final findings = widget.data['walton_stressitesti_loydokset'] as List<dynamic>? ?? [];
     final fidelity = widget.data['paattelyketjun_uskollisuus_auditointi'] as Map<String, dynamic>? ?? {};
     
     return Column(
       children: [
          if (fidelity.isNotEmpty)
             Container(
               padding: const EdgeInsets.all(16),
               decoration: BoxDecoration(color: Colors.orange[50], borderRadius: BorderRadius.circular(8)),
               child: Column(
                 children: [
                   Row(
                     mainAxisAlignment: MainAxisAlignment.spaceBetween,
                     children: [
                       const Text("Päättelyketjun Uskollisuus", style: TextStyle(fontWeight: FontWeight.bold)),
                       _buildSignalMeter(fidelity['uskollisuus_score']),
                     ],
                   ),
                   const SizedBox(height: 8),
                   Text(
                     fidelity['onko_post_hoc_rationalisointia'] == true 
                       ? "⚠️ Post-Hoc Rationalisointia havaittu!" 
                       : "✅ Ei rationalisointia.",
                     style: TextStyle(
                       color: fidelity['onko_post_hoc_rationalisointia'] == true ? Colors.red[800] : Colors.green[800],
                       fontWeight: FontWeight.w600
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
                 child: Icon(passed ? Icons.check : Icons.close, color: Colors.white, size: 16),
               ),
               title: Text(f['kysymys'] ?? ''),
               subtitle: Text(f['havainto'] ?? ''),
               dense: true,
             );
          }).toList()
       ],
     );
  }

  // --- 3. CAUSAL ANALYSIS ---
  Widget _buildCausalAnalysis(BuildContext context) {
    // ... (Keep existing implementation or minimal tweaks)
    final simul = widget.data['kontrafaktuaalinen_testi'] as Map<String, dynamic>? ?? {};
    final abd = widget.data['abduktiivinen_paatelma'] as String?;
    
    return Column(
      children: [
         if (abd != null)
           _buildInfoCard("Abduktiivinen Päätelmä", abd, Icons.lightbulb_outline, color: Colors.teal[50]),
         const SizedBox(height: 16),
         
         if (simul.isNotEmpty) 
           Row(
             crossAxisAlignment: CrossAxisAlignment.start,
             children: [
               Expanded(child: _buildComparisonBlock("Toteutunut", simul['skenaario_A_toteutunut'], Colors.grey[200]!)),
               const SizedBox(width: 8),
               const Icon(Icons.arrow_forward),
               const SizedBox(width: 8),
               Expanded(child: _buildComparisonBlock("Simulaatio", simul['skenaario_B_simulaatio'], Colors.teal[100]!)),
             ],
           ),
          if (simul['uskottavuus_arvio'] != null)
             Padding(
               padding: const EdgeInsets.only(top: 8.0),
               child: Text("Uskottavuus: ${simul['uskottavuus_arvio']}", style: const TextStyle(fontStyle: FontStyle.italic)),
             )
      ],
    );
  }

    // --- 4. PROFILER ANALYSIS ---
  Widget _buildProfilerAnalysis(BuildContext context) {
      final biases = widget.data['tunnistetut_vinoumat'] as List<dynamic>? ?? [];
      final profile = widget.data['psykologinen_profiili'] as String?;
      final intent = widget.data['intentio_analyysi'] as String?;
      final metrics = widget.data['teksti_metriikka'] as Map<String, dynamic>? ?? {};
      
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
            if (metrics.isNotEmpty) ...[
              const Text("Tekstimetriikka:", style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Row(
                children: [
                   Expanded(child: _buildMetricMeter("Sanaston monipuolisuus", metrics['lexical_diversity'])),
                   const SizedBox(width: 16),
                   Expanded(child: _buildMetricMeter("Huuto/Kapitalisaatio", metrics['capitalization_ratio'], inverseBad: true)),
                ],
              ),
              const SizedBox(height: 16),
            ],

           if (biases.isNotEmpty) ...[
             const Text("Tunnistetut Vinoumat:", style: TextStyle(fontWeight: FontWeight.bold)),
             const SizedBox(height: 8),
             Wrap(
               spacing: 8,
               runSpacing: 4,
               children: biases.map((b) => Chip(
                 label: Text(b['nimi'] ?? 'Vinouma'),
                 avatar: const Icon(Icons.warning_amber_rounded, size: 16),
                 backgroundColor: Colors.pink[50],
                 labelStyle: const TextStyle(fontSize: 12),
               )).toList(),
             ),
             const SizedBox(height: 16),
           ],
           if (intent != null) _buildInfoCard("Intentio", intent, Icons.ads_click, color: Colors.blue[50]),
           const SizedBox(height: 8),
           if (profile != null) _buildInfoCard("Psykologinen Profiili", profile, Icons.person_outline),
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
            ...ethics.map((e) => Card(
              color: Colors.red[50], 
              child: ListTile(
                leading: const Icon(Icons.security, color: Colors.red),
                title: Text(e['tyyppi'] ?? 'Eettinen Huomio'),
                subtitle: Text(e['kuvaus'] ?? ''),
                trailing: Chip(label: Text(e['vakavuus'] ?? 'N/A'), backgroundColor: Colors.white),
              )
            )).toList(),
            const SizedBox(height: 16),
          ],
          const Text("Faktantarkistus", style: TextStyle(fontWeight: FontWeight.bold)),
          if (facts.isEmpty) const Padding(padding:EdgeInsets.all(8), child:Text("Ei faktantarkistuspyyntöjä.")),
          ...facts.map((f) {
             final status = f['verifiointi_tulos'];
             Color c = Colors.grey;
             IconData i = Icons.help_outline;
             if (status == 'Vahvistettu') { c = Colors.green; i = Icons.check_circle; }
             if (status == 'Kumottu') { c = Colors.red; i = Icons.cancel; }
             
             return ListTile(
               leading: Icon(i, color: c),
               title: Text(f['vaite'] ?? ''),
               subtitle: Text(f['lahde_tai_paattely'] ?? ''),
             );
          }).toList()
       ],
     );
  }
  
  // --- 6. PERFORMATIVITY CHECK ---
  Widget _buildPerformativityCheck(BuildContext context) {
     final heuristics = widget.data['performatiivisuus_heuristiikat'] as List<dynamic>? ?? [];
     final overall = widget.data['yleisarvio_aitoudesta'] as String?;
     
     return Column(
       children: [
          if (overall != null)
             Container(
               padding: const EdgeInsets.all(16),
               decoration: BoxDecoration(
                 gradient: LinearGradient(colors: [Colors.purple[50]!, Colors.blue[50]!]),
                 borderRadius: BorderRadius.circular(12)
               ),
               child: Column(
                 children: [
                   const Text("Aitousarvio", style: TextStyle(fontWeight: FontWeight.bold)),
                   const SizedBox(height: 8),
                   _buildAuthenticityMeter(overall),
                 ],
               ),
             ),
          const SizedBox(height: 16),
          const Text("Heuristiikat:", style: TextStyle(fontWeight: FontWeight.bold)),
           Wrap(
               spacing: 8,
               runSpacing: 4,
               children: heuristics.map((b) {
                 final raised = b['lippu_nostettu'] == true;
                 return Chip(
                 label: Text(b['heuristiikka'] ?? ''),
                 avatar: Icon(raised ? Icons.flag : Icons.check, size: 16, color: raised ? Colors.red : Colors.green),
                 backgroundColor: raised ? Colors.red[50] : Colors.green[50],
                 labelStyle: TextStyle(fontSize: 12, color: raised ? Colors.red[900] : Colors.green[900]),
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
                    height: 100, width: 100,
                    child: Stack(
                       children: [
                          Center(
                            child: SizedBox(
                              height: 80, width: 80,
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
                                Text("${score ?? '?'}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 24)),
                                const Text("Score", style: TextStyle(fontSize: 10, color: Colors.grey)),
                              ],
                            )
                          ),
                       ],
                    ),
                  ),
                  const SizedBox(width: 24),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("Compliance-analyysi", style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text(analysis ?? "Ei analyysiä."),
                      ],
                    )
                  )
               ],
             ),
           ),
           const SizedBox(height: 16),
           ...recs.map((r) => ListTile(
              leading: const Icon(Icons.task_alt, size: 16, color: Colors.brown),
              title: Text(r.toString()),
              dense: true,
           )).toList()
        ],
      );
  }


  // --- HELPERS & METERS ---
  
  Widget _buildSignalMeter(dynamic score) {
    // Score expected: KORKEA, EPÄVARMA, HEIKKO
    int level = 0;
    Color color = Colors.grey;
    if (score == 'KORKEA') { level = 3; color = Colors.green; }
    else if (score == 'EPÄVARMA') { level = 2; color = Colors.orange; }
    else if (score == 'HEIKKO') { level = 1; color = Colors.red; }
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildSignalBar(1, level, color),
        const SizedBox(width: 2),
        _buildSignalBar(2, level, color),
        const SizedBox(width: 2),
        _buildSignalBar(3, level, color),
        const SizedBox(width: 8),
        Text(score.toString(), style: TextStyle(fontWeight: FontWeight.bold, color: color))
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
        borderRadius: BorderRadius.circular(2)
      ),
    );
  }
  
  Widget _buildAuthenticityMeter(String riskLevel) {
    // Orgaaninen, Performatiivinen, Epäilyttävä
    double value = 0.5;
    Color color = Colors.grey;
    String label = riskLevel;
    
    if (riskLevel == 'Orgaaninen') { value = 1.0; color = Colors.green; }
    if (riskLevel == 'Performatiivinen') { value = 0.5; color = Colors.purple; }
    if (riskLevel == 'Epäilyttävä') { value = 0.1; color = Colors.red; }
    
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
        Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold))
      ],
    );
  }
  
  Color _getColorForScore(double value) {
    if (value >= 0.8) return Colors.green;
    if (value >= 0.5) return Colors.orange;
    return Colors.red;
  }
  
  Widget _buildMetricMeter(String label, dynamic value, {bool inverseBad = false}) {
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
               Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey, fontWeight: FontWeight.bold)),
               Text((v * 100).toStringAsFixed(0) + "%", style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
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
          )
       ],
     );
  }


  Widget _buildGenericMap(Map<String, dynamic> map) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start, 
        children: map.entries.map((e) => Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
               Text("${e.key}: ", style: const TextStyle(fontWeight: FontWeight.bold)),
               Expanded(child: Text(e.value.toString()))
            ],
          ),
        )).toList()
     );
  }

  Widget _buildInfoCard(String title, String value, IconData icon, {String? subtitle, Color? color}) {
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
                 Text(title, style: const TextStyle(fontSize: 12, color: Colors.black54)),
                 Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                 if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(subtitle, style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic))
                 ]
               ],
             ),
           )
        ],
      ),
    );
  }
  
  Widget _buildComparisonBlock(String label, dynamic content, Color color) {
     return Container(
       padding: const EdgeInsets.all(8),
       decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(4)),
       child: Column(
         children: [
            Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(content.toString(), style: const TextStyle(fontSize: 12), textAlign: TextAlign.center),
         ],
       ),
     );
  }
  
  Widget _buildLabelValue(String label, dynamic value) {
     return Column(
       crossAxisAlignment: CrossAxisAlignment.start,
       children: [
          Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey, fontWeight: FontWeight.bold)),
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
      child: SelectableText(
        jsonStr,
        style: const TextStyle(
          fontFamily: 'monospace',
          fontSize: 12,
          color: Color(0xFFcccccc),
        ),
      ),
    );
  }
}
