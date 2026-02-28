import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/usage/presentation/providers/usage_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/usage/domain/models/usage_report.dart';

enum UsageScopeSelection { system, organization, user }

class UsageScreen extends ConsumerStatefulWidget {
  const UsageScreen({super.key});

  @override
  ConsumerState<UsageScreen> createState() => _UsageScreenState();
}

class _UsageScreenState extends ConsumerState<UsageScreen> {
  UsageScopeSelection? _selectedScope;

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authControllerProvider).value;

    if (user == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final isRoot = user.role.name == 'root';

    // Initialize default scope if not set
    _selectedScope ??=
        isRoot ? UsageScopeSelection.system : UsageScopeSelection.organization;

    // Enforce role constraints if a non-root user somehow selects system
    if (!isRoot && _selectedScope == UsageScopeSelection.system) {
      _selectedScope = UsageScopeSelection.organization;
    }

    final AsyncValue<UsageReport> usageState;
    switch (_selectedScope!) {
      case UsageScopeSelection.system:
        usageState = ref.watch(systemUsageControllerProvider);
        break;
      case UsageScopeSelection.organization:
        usageState = ref.watch(
          organizationUsageControllerProvider(user.organizationId ?? ''),
        );
        break;
      case UsageScopeSelection.user:
        usageState = ref.watch(userUsageControllerProvider);
        break;
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics & Usage'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              switch (_selectedScope!) {
                case UsageScopeSelection.system:
                  ref.read(systemUsageControllerProvider.notifier).refresh();
                  break;
                case UsageScopeSelection.organization:
                  ref
                      .read(
                        organizationUsageControllerProvider(
                          user.organizationId ?? '',
                        ).notifier,
                      )
                      .refresh();
                  break;
                case UsageScopeSelection.user:
                  ref.read(userUsageControllerProvider.notifier).refresh();
                  break;
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: SegmentedButton<UsageScopeSelection>(
              segments: [
                if (isRoot)
                  const ButtonSegment(
                    value: UsageScopeSelection.system,
                    label: Text('System'),
                    icon: Icon(Icons.dns),
                  ),
                const ButtonSegment(
                  value: UsageScopeSelection.organization,
                  label: Text('Organization'),
                  icon: Icon(Icons.business),
                ),
                const ButtonSegment(
                  value: UsageScopeSelection.user,
                  label: Text('My Usage'),
                  icon: Icon(Icons.person),
                ),
              ],
              selected: {_selectedScope!},
              onSelectionChanged: (Set<UsageScopeSelection> newSelection) {
                setState(() {
                  _selectedScope = newSelection.first;
                });
              },
            ),
          ),
          Expanded(
            child: usageState.when(
              data: (usageReport) {
                // Determine missing data intuitively
                final hasData =
                    usageReport.usage.totalTokens > 0 ||
                    usageReport.usage.costUsd > 0;

                return Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Scope: \${usageReport.scope}',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Period: \${usageReport.period}',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 24),
                      if (!hasData)
                        Card(
                          color:
                              Theme.of(
                                context,
                              ).colorScheme.surfaceContainerHighest,
                          child: const Padding(
                            padding: EdgeInsets.all(24.0),
                            child: Center(
                              child: Text(
                                'No usage data recorded for this scope in the current period.',
                                style: TextStyle(fontStyle: FontStyle.italic),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                        )
                      else
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(16.0),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Tokens',
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                                const Divider(),
                                ListTile(
                                  title: const Text('Prompt Tokens'),
                                  trailing: Text(
                                    usageReport.usage.promptTokens.toString(),
                                  ),
                                ),
                                ListTile(
                                  title: const Text('Completion Tokens'),
                                  trailing: Text(
                                    usageReport.usage.completionTokens
                                        .toString(),
                                  ),
                                ),
                                ListTile(
                                  title: const Text('Total Tokens'),
                                  trailing: Text(
                                    usageReport.usage.totalTokens.toString(),
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const Divider(),
                                ListTile(
                                  title: const Text('Estimated Cost'),
                                  trailing: Text(
                                    '\$\${usageReport.usage.costUsd.toStringAsFixed(4)}',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      color:
                                          Theme.of(context).colorScheme.primary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error:
                  (err, st) => ErrorView(
                    error: err,
                    onRetry: () {
                      switch (_selectedScope!) {
                        case UsageScopeSelection.system:
                          ref
                              .read(systemUsageControllerProvider.notifier)
                              .refresh();
                          break;
                        case UsageScopeSelection.organization:
                          ref
                              .read(
                                organizationUsageControllerProvider(
                                  user.organizationId ?? '',
                                ).notifier,
                              )
                              .refresh();
                          break;
                        case UsageScopeSelection.user:
                          ref
                              .read(userUsageControllerProvider.notifier)
                              .refresh();
                          break;
                      }
                    },
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
