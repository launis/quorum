import 'package:client_app/features/admin/data/organization_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/settings/usage_stats_provider.dart';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AdminLimitControls extends ConsumerStatefulWidget {
  const AdminLimitControls({super.key});

  @override
  ConsumerState<AdminLimitControls> createState() => _AdminLimitControlsState();
}

class _AdminLimitControlsState extends ConsumerState<AdminLimitControls> {
  final _formKey = GlobalKey<FormState>();

  // Form values (nullable until loaded)
  int? _tpmLimit;
  int? _rpmLimit;
  double? _quotaLimit;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    // Pre-fill fields once data is available is tricky in initState if it comes from a provider.
    // We'll handle initialization in build or via a listener if strictly needed,
    // but typically we can use initialValue from the async provider if we want.
    // However, to edit, we need state.
    // A better pattern: Listen to usageStatsProvider to fill initial values ONCE.
  }

  Future<void> _save(String orgId) async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    setState(() => _isLoading = true);

    try {
      final repo = ref.read(organizationRepositoryProvider);

      final updates = <String, dynamic>{
        'tpm_limit': _tpmLimit,
        'rpm_limit': _rpmLimit,
        'quota_limit': _quotaLimit,
      };

      final result = await repo.updateOrganization(orgId, updates);

      result.fold(
        (error) => ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: ${error.toString()}'))),
        (org) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Limits updated successfully')),
          );
          // Refresh stats
          return ref.refresh(usageStatsProvider(scope: 'org'));
        },
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final statsAsync = ref.watch(usageStatsProvider(scope: 'org'));
    final userAsync = ref.watch(authControllerProvider);
    final user = userAsync.asData?.value;

    // Only show for ROOT or ADMIN
    // Assuming UserRole enum or string check.
    // "role" in User model is String? for now based on previous context,
    // or maybe UserRole enum. Let's assume strict check if possible, or string.
    // Previous user.dart context showed String? role.
    if (user == null ||
        (user.role != UserRole.root && user.role != UserRole.admin)) {
      return const SizedBox.shrink();
    }

    // Also need orgID
    if (user.organizationId == null) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      color:
          Theme.of(context).colorScheme.surfaceContainer, // distinct background
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: statsAsync.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, s) => Text('Error loading limits: $e'),
          data: (stats) {
            // Initialize form fields *if they haven't been touched yet*
            // Actually, best to do this scheduling a microtask or rely on null checks
            // But setState inside build is bad.
            // Using a simple check:
            if (_tpmLimit == null) {
              _tpmLimit = stats.tpmLimit;
              _rpmLimit = stats.rpmLimit;
              _quotaLimit = stats.costLimit;
            }

            return Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.admin_panel_settings, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Admin Controls',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // TPM LIMIT
                  TextFormField(
                    initialValue: _tpmLimit?.toString(),
                    decoration: const InputDecoration(
                      labelText: 'TPM Limit (Tokens Per Minute)',
                      border: OutlineInputBorder(),
                      helperText: 'e.g. 100000 for Standard Tier',
                    ),
                    keyboardType: TextInputType.number,
                    validator:
                        (v) =>
                            (int.tryParse(v ?? '') ?? 0) < 1000
                                ? 'Minimum 1000'
                                : null,
                    onSaved: (v) => _tpmLimit = int.tryParse(v ?? ''),
                  ),
                  const SizedBox(height: 16),

                  // RPM LIMIT
                  TextFormField(
                    initialValue: _rpmLimit?.toString(),
                    decoration: const InputDecoration(
                      labelText: 'RPM Limit (Requests Per Minute)',
                      border: OutlineInputBorder(),
                      helperText: 'e.g. 60 for Standard Tier',
                    ),
                    keyboardType: TextInputType.number,
                    validator:
                        (v) =>
                            (int.tryParse(v ?? '') ?? 0) < 1
                                ? 'Minimum 1'
                                : null,
                    onSaved: (v) => _rpmLimit = int.tryParse(v ?? ''),
                  ),
                  const SizedBox(height: 16),

                  // QUOTA LIMIT ($)
                  TextFormField(
                    initialValue: _quotaLimit?.toString(),
                    decoration: const InputDecoration(
                      labelText: 'Monthly Quota (USD)',
                      border: OutlineInputBorder(),
                      prefixText: '\$ ',
                    ),
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    validator:
                        (v) =>
                            (double.tryParse(v ?? '') ?? 0) < 0
                                ? 'Must be positive'
                                : null,
                    onSaved: (v) => _quotaLimit = double.tryParse(v ?? ''),
                  ),
                  const SizedBox(height: 24),

                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed:
                          _isLoading ? null : () => _save(user.organizationId!),
                      icon:
                          _isLoading
                              ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                              : const Icon(Icons.save),
                      label: const Text('Update Limits'),
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}
