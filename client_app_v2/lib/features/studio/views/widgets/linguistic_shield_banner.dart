import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Two-phase synchronous detector for non-English linguistic anomalies in AI evaluation assertions.
class LinguisticShieldDetector {
  static const Set<String> _targetStopwords = {
    'on',
    'ei',
    'ja',
    'se',
    'että',
    'mutta',
    'kuin',
    'jos',
    'niin',
    'kun',
    'tai',
    'ovat',
    'myös',
    'vain',
    'joka',
    'jotka',
    'tämä',
    'nämä',
  };

  /// Typographical whitelist: smart quotes (\u2018-\u201D), dashes (\u2013-\u2014), ellipsis (\u2026), bullets (\u2022).
  static final RegExp _typographicalWhitelist = RegExp(
    r'[\u2018-\u201D\u2013-\u2014\u2026\u2022]',
  );

  /// Evaluates whether the provided text triggers the linguistic shield.
  static bool hasLinguisticAnomaly(String text) {
    if (text.trim().isEmpty) return false;

    // Phase 1: Unicode check outside Basic Latin [^\x00-\x7F], ignoring typographical whitelist
    final cleanedText = text.replaceAll(_typographicalWhitelist, '');
    final hasNonAscii = RegExp(r'[^\x00-\x7F]').hasMatch(cleanedText);
    if (hasNonAscii) return true;

    // Phase 2: Target-language structural stopword gate (>= 2 matches)
    final tokens = text.toLowerCase().split(RegExp(r'[\s,.;:!?()\[\]"\\/]+'));
    var stopwordCount = 0;
    for (final token in tokens) {
      if (_targetStopwords.contains(token)) {
        stopwordCount++;
        if (stopwordCount >= 2) return true;
      }
    }
    return false;
  }
}

/// Inline informational banner rendered when non-English linguistic anomalies are detected.
class LinguisticShieldBanner extends StatelessWidget {
  final String text;

  const LinguisticShieldBanner({super.key, required this.text});

  @override
  Widget build(BuildContext context) {
    if (!LinguisticShieldDetector.hasLinguisticAnomaly(text)) {
      return const SizedBox.shrink();
    }

    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context);

    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: theme.colorScheme.tertiaryContainer,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: theme.colorScheme.tertiary.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.info_outline,
            color: theme.colorScheme.onTertiaryContainer,
            size: 20,
          ),
          AppSpacing.w8,
          Expanded(
            child: Text(
              l10n?.scaleLinguisticShieldWarning ??
                  'Non-English characters or words detected. Ensure the evaluation assertion is written in English.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onTertiaryContainer,
                height: 1.3,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
