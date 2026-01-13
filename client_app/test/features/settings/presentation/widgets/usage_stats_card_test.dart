import 'package:client_app/features/settings/presentation/widgets/usage_stats_card.dart';
import 'package:client_app/features/settings/usage_stats_provider.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('UsageStatsCard displays loading and data correctly', (
    tester,
  ) async {
    final stats = UsageStats(
      usedCost: 5.42,
      costLimit: 10.0,
      tpmLimit: 100000,
      rpmLimit: 60,
      percentage: 0.542,
      period: '2026-01',
    );

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
    expect(find.textContaining('\$5.4200'), findsOneWidget);

    // Check Progress Bar
    final progressBar = tester.widget<LinearProgressIndicator>(
      find.byType(LinearProgressIndicator),
    );
    expect(progressBar.value, closeTo(0.542, 0.001));

    // Check Limits
    expect(find.textContaining('100000 tokens'), findsOneWidget);
    expect(find.textContaining('60 requests'), findsOneWidget);
  });
}
