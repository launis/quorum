import 'package:flutter/material.dart';
import 'package:client_app/features/orchestration/presentation/widgets/results/deep_dive_expander.dart';

class EvidenceDashboard extends StatelessWidget {
  final Map<String, dynamic> report;

  const EvidenceDashboard({super.key, required this.report});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    // Extract sections
    final hypos = report['analyysi_hypoteesit'] as List? ?? [];
    final evidence = report['analyysi_todisteet'] as List? ?? []; // RAG results
    final toulmin = report['logiikka_toulmin'] as List? ?? [];
    final facts = report['faktatarkistus'] as List? ?? [];
    final ethics = report['etiikka'] as List? ?? [];

    if (hypos.isEmpty &&
        evidence.isEmpty &&
        toulmin.isEmpty &&
        facts.isEmpty &&
        ethics.isEmpty) {
      return const SizedBox.shrink();
    }

    return DeepDiveExpander(
      title: 'Evidence & Logic Dashboard',
      icon: Icons.science_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Hypotheses
          if (hypos.isNotEmpty) ...[
            _sectionHeader(context, 'Hypothesis Testing'),
            ...hypos.map((h) {
              final map = h as Map<String, dynamic>;
              final found = map['loytyyko_todisteita'] as bool? ?? false;
              return ListTile(
                leading: Icon(
                  found ? Icons.check_circle : Icons.cancel,
                  color: found ? Colors.green : Colors.red,
                ),
                title: Text(map['vaite_teksti'] as String? ?? 'Unknown'),
                subtitle:
                    found
                        ? const Text('Evidence found')
                        : const Text('No evidence'),
                dense: true,
              );
            }),
            const Divider(),
          ],

          // 2. RAG Evidence (New)
          if (evidence.isNotEmpty) ...[
            _sectionHeader(context, 'Found Evidence (RAG)'),
            ...evidence.map((e) {
              final map = e as Map<String, dynamic>;
              final score = map['relevanssi_score'] as num? ?? 0;
              final text = map['konteksti_segmentti'] as String? ?? '';
              return Card(
                color: Theme.of(context).colorScheme.surfaceContainer,
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.manage_search, size: 16),
                          const SizedBox(width: 8),
                          Text(
                            'Relevance: $score%',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: score > 70 ? Colors.green : Colors.orange,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '"$text"',
                        style: const TextStyle(fontStyle: FontStyle.italic),
                      ),
                    ],
                  ),
                ),
              );
            }),
            const Divider(),
          ],

          // 3. Logic (Toulmin)
          if (toulmin.isNotEmpty) ...[
            _sectionHeader(context, 'Logical Structure (Toulmin)'),
            ...toulmin.map((t) {
              final map = t as Map<String, dynamic>;
              return Card(
                color: Theme.of(context).colorScheme.surfaceContainer,
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _toulminRow('Claim', map['claim'] as String?),
                      _toulminRow('Data', map['data'] as String?),
                      _toulminRow('Warrant', map['warrant'] as String?),
                      if (map['backing'] != null)
                        _toulminRow('Backing', map['backing'] as String?),
                    ],
                  ),
                ),
              );
            }),
            const Divider(),
          ],

          // 4. Facts & Ethics
          if (facts.isNotEmpty || ethics.isNotEmpty) ...[
            _sectionHeader(context, 'Facts & Ethics'),
            if (facts.isNotEmpty)
              ...facts.map((f) {
                final map = f as Map<String, dynamic>;
                final res = map['verifiointi_tulos'] as String? ?? 'Unknown';
                final resLower = res.toLowerCase();
                final isVerified =
                    resLower.contains('vahvistettu') ||
                    resLower.contains('verified');

                String localizedRes = res;
                if (isVerified) {
                  localizedRes = l10n.verVerified;
                } else if (resLower.contains('kumottu') ||
                    resLower.contains('debunked')) {
                  localizedRes = l10n.verDebunked;
                } else if (resLower.contains('epävarma') ||
                    resLower.contains('uncertain')) {
                  localizedRes = l10n.verUncertain;
                }

                return ListTile(
                  leading: Icon(
                    isVerified ? Icons.verified : Icons.verified_user_outlined,
                    color: isVerified ? Colors.green : Colors.orange,
                  ),
                  title: Text(map['vaite'] as String? ?? ''),
                  subtitle: Text(
                    '$localizedRes (${map['lahde_tai_paattely']})',
                  ),
                  dense: true,
                );
              }),
            if (ethics.isNotEmpty)
              ...ethics.map((e) {
                final map = e as Map<String, dynamic>;
                final type = map['tyyppi'] as String? ?? 'Ei havaittu';
                if (type == 'Ei havaittu') return const SizedBox.shrink();

                return Card(
                  color: Colors.red.withValues(alpha: 0.1),
                  child: ListTile(
                    leading: const Icon(Icons.gavel, color: Colors.red),
                    title: Text(type),
                    subtitle: Text('${map['vakavuus']}: ${map['kuvaus']}'),
                  ),
                );
              }),
          ],
        ],
      ),
    );
  }

  Widget _sectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.bold,
          color: Theme.of(context).primaryColor,
        ),
      ),
    );
  }

  Widget _toulminRow(String label, String? value) {
    if (value == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 60,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
            ),
          ),
          Expanded(child: Text(value, style: const TextStyle(fontSize: 12))),
        ],
      ),
    );
  }
}
