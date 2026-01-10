import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/app_localizations.dart';

class AdminDashboardScreen extends ConsumerWidget {
  final Widget child;

  const AdminDashboardScreen({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    // Calculate selected index based on current location
    final String location = GoRouterState.of(context).uri.toString();
    int selectedIndex = 0;
    if (location.startsWith('/admin/users')) {
      selectedIndex = 1;
    } else if (location.startsWith('/admin/organizations')) {
      selectedIndex = 2;
    }

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: selectedIndex,
            onDestinationSelected: (int index) {
              switch (index) {
                case 0:
                  context.go('/admin');
                  break;
                case 1:
                  context.go('/admin/users');
                  break;
                case 2:
                  context.go('/admin/organizations');
                  break;
              }
            },
            labelType: NavigationRailLabelType.all,
            destinations: [
              NavigationRailDestination(
                icon: const Icon(Icons.dashboard_outlined),
                selectedIcon: const Icon(Icons.dashboard),
                label: Text(l10n.overview),
              ),
              NavigationRailDestination(
                icon: const Icon(Icons.people_outlined),
                selectedIcon: const Icon(Icons.people),
                label: Text(l10n.userManagementTitle),
              ),
              NavigationRailDestination(
                icon: const Icon(Icons.business_outlined),
                selectedIcon: const Icon(Icons.business),
                label: Text(l10n.organizationManagementTitle),
              ),
            ],
          ),
          const VerticalDivider(thickness: 1, width: 1),
          // Expanded content area
          Expanded(child: child),
        ],
      ),
    );
  }
}
