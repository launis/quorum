import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class AdminDashboardScreen extends ConsumerWidget {
  final Widget child;

  const AdminDashboardScreen({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final user = ref.watch(authControllerProvider).value;

    // Destinations List
    final allDestinations = [
      (
        icon: Icons.dashboard_outlined,
        selectedIcon: Icons.dashboard,
        label: l10n.overview,
        path: '/admin',
      ),
      (
        icon: Icons.people_outlined,
        selectedIcon: Icons.people,
        label: l10n.userManagementTitle,
        path: '/admin/users',
      ),
      (
        icon: Icons.business_outlined,
        selectedIcon: Icons.business,
        label: l10n.organizationManagementTitle,
        path: '/admin/organizations',
      ),
      (
        icon: Icons.settings_outlined,
        selectedIcon: Icons.settings,
        label: l10n.systemSettingsTitle,
        path: '/admin/settings',
      ),
    ];

    // Filter destinations based on Role
    final visibleDestinations =
        allDestinations.where((d) {
          if (d.path == '/admin/organizations') {
            return user?.role == UserRole.root;
          }
          return true;
        }).toList();

    // Calculate selected index based on current location
    final String location = GoRouterState.of(context).uri.toString();

    int selectedIndex = visibleDestinations.indexWhere((d) {
      if (d.path == '/admin') {
        return location == '/admin';
      }
      return location.startsWith(d.path);
    });

    // Fallback if no match (e.g. sub-routes), specific handling logic
    // or just default to 0 if valid
    if (selectedIndex == -1) {
      // Manual fallback logic similar to before, but mapped to filtered list
      // Actually, generic logic above works well for /admin/users etc.
      // Only edge case is if we are at a route not in list ?
      // But we only have these routes in router.
      // Safe fallback:
      if (location.startsWith('/admin/users')) {
        selectedIndex = visibleDestinations.indexWhere(
          (d) => d.path == '/admin/users',
        );
      } else if (location.startsWith('/admin/organizations')) {
        selectedIndex = visibleDestinations.indexWhere(
          (d) => d.path == '/admin/organizations',
        );
      } else if (location.startsWith('/admin/settings')) {
        selectedIndex = visibleDestinations.indexWhere(
          (d) => d.path == '/admin/settings',
        );
      } else {
        selectedIndex = 0;
      }
    }
    // Ensure index is valid (e.g. if orgs removed but we are somehow at orgs url -> fallback 0)
    if (selectedIndex == -1) selectedIndex = 0;

    return LayoutBuilder(
      builder: (context, constraints) {
        // BREAKPOINT: 600dp
        final isWide = constraints.maxWidth >= 600;

        if (isWide) {
          // DESKTOP / TABLET: NavigationRail
          return Scaffold(
            body: Row(
              children: [
                NavigationRail(
                  selectedIndex: selectedIndex,
                  onDestinationSelected: (int index) {
                    context.go(visibleDestinations[index].path);
                  },
                  labelType: NavigationRailLabelType.all,
                  destinations:
                      visibleDestinations
                          .map(
                            (d) => NavigationRailDestination(
                              icon: Icon(d.icon),
                              selectedIcon: Icon(d.selectedIcon),
                              label: Text(d.label),
                            ),
                          )
                          .toList(),
                ),
                const VerticalDivider(thickness: 1, width: 1),
                Expanded(
                  child: Center(
                    child: SafeArea(
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 1200),
                        child: child,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          );
        } else {
          // MOBILE: NavigationBar
          return Scaffold(
            body: SafeArea(
              child: child,
            ), // Content is NOT constrained on mobile (full width)
            bottomNavigationBar: NavigationBar(
              selectedIndex: selectedIndex,
              onDestinationSelected: (int index) {
                context.go(visibleDestinations[index].path);
              },
              destinations:
                  visibleDestinations
                      .map(
                        (d) => NavigationDestination(
                          icon: Icon(d.icon),
                          selectedIcon: Icon(d.selectedIcon),
                          label: d.label,
                        ),
                      )
                      .toList(),
            ),
          );
        }
      },
    );
  }
}
