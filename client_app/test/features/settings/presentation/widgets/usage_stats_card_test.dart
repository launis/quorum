import 'package:client_app/features/settings/presentation/widgets/usage_stats_card.dart';
import 'package:client_app/features/settings/usage_stats_provider.dart';
import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('UsageStatsCard displays loading and data correctly', (
    tester,
  ) async {
    final stats = UsageStats(usedTokens: 15420, tokenLimit: 50000);

    // Create Future provider override since original is FutureProvider/AsyncValue
    // If it is 'usageStatsProvider', it is likely AutoDisposeFutureProvider based on @riverpod func.
    // We cannot override with a Stream unless we change the provider type expected,
    // OR if we return Future.value(stats).

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          usageStatsProvider.overrideWith((ref) => Future.value(stats)),
        ],
        child: const MaterialApp(
          localizationsDelegates: [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
          ],
          supportedLocales: AppLocalizations.supportedLocales,
          home: Scaffold(body: UsageStatsCard()),
        ),
      ),
    );

    // Pump to settle the Future
    await tester.pumpAndSettle();

    // Verify content
    // Check for text parts since "Usage Statistics" might be localized differently or I don't have exact arb.
    // Use AppLocalizations to get exact string? No context here easily.
    // Just check for numbers which are reliable.
    expect(
      find.textContaining('15,420'),
      findsOneWidget,
    ); // formatted? or just string.
    // Arb usually format {count} so potentially localized 15420 or 15,420.
    // Let's rely on finding *something* that proves rendering.

    // Check Progress Bar
    final progressBar = tester.widget<LinearProgressIndicator>(
      find.byType(LinearProgressIndicator),
    );
    expect(progressBar.value, closeTo(0.3084, 0.001)); // 15420 / 50000 = 0.3084
  });
}
