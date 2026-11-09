import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

// Adaptive Navigation Shell with Profiili / Profile, Role-Gated Organization & IAM, and Trailing Sign-Out Button.

/// **Adaptive Navigation Scaffold**
///
/// Wraps the main application content with a responsive navigation structure.
class ScaffoldWithNav extends ConsumerWidget {
  final StatefulNavigationShell navigationShell;

  const ScaffoldWithNav({super.key, required this.navigationShell});

  static const double _wideScreenBreakpoint = 800.0;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    // Evaluate Roles via Dart 3 pattern matching
    final authState = ref.watch(authControllerProvider);
    final userRole = switch (authState) {
      AsyncData(:final value) => value?.role,
      AsyncLoading() || AsyncError() => null,
    };

    final isAdmin = userRole == UserRole.root || userRole == UserRole.admin;
    final canManageOrganization = isAdmin || userRole == UserRole.manager;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWideScreen = constraints.maxWidth >= _wideScreenBreakpoint;

        return Scaffold(
          body: isWideScreen
              ? _WideScreenLayout(
                  navigationShell: navigationShell,
                  canManageOrganization: canManageOrganization,
                  isAdmin: isAdmin,
                  onDestinationSelected: (index) => _onItemTapped(
                    index,
                    context,
                    canManageOrganization: canManageOrganization,
                    isAdmin: isAdmin,
                  ),
                )
              : navigationShell,
          bottomNavigationBar: isWideScreen
              ? null
              : NavigationBar(
                  selectedIndex: navigationShell.currentIndex,
                  onDestinationSelected: (index) => _onItemTapped(
                    index,
                    context,
                    canManageOrganization: canManageOrganization,
                    isAdmin: isAdmin,
                  ),
                  destinations: [
                    NavigationDestination(
                      icon: const Icon(Icons.dashboard_outlined),
                      selectedIcon: const Icon(Icons.dashboard),
                      label: l10n.navDashboard,
                    ),
                    NavigationDestination(
                      icon: const Icon(Icons.add_circle_outline),
                      selectedIcon: const Icon(Icons.add_circle),
                      label: l10n.newAnalysis,
                    ),
                    NavigationDestination(
                      icon: const Icon(Icons.person_outline),
                      selectedIcon: const Icon(Icons.person),
                      label: l10n.navProfile,
                    ),
                    if (canManageOrganization)
                      NavigationDestination(
                        icon: const Icon(Icons.corporate_fare_outlined),
                        selectedIcon: const Icon(Icons.corporate_fare),
                        label: l10n.navOrganization,
                      ),
                    if (isAdmin)
                      NavigationDestination(
                        icon: const Icon(Icons.admin_panel_settings_outlined),
                        selectedIcon: const Icon(Icons.admin_panel_settings),
                        label: l10n.navAdmin,
                      ),
                  ],
                ),
        );
      },
    );
  }

  void _onItemTapped(
    int index,
    BuildContext context, {
    required bool canManageOrganization,
    required bool isAdmin,
  }) {
    final adminIndex = canManageOrganization ? 4 : 3;
    if (isAdmin && index == adminIndex) {
      context.go('/admin');
      return;
    }

    if (canManageOrganization && index == 3) {
      if (navigationShell.route.branches.length > 3) {
        navigationShell.goBranch(
          3,
          initialLocation: 3 == navigationShell.currentIndex,
        );
      } else {
        context.go('/organization');
      }
      return;
    }

    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }
}

class _WideScreenLayout extends HookConsumerWidget {
  final StatefulNavigationShell navigationShell;
  final bool canManageOrganization;
  final bool isAdmin;
  final ValueChanged<int> onDestinationSelected;

  const _WideScreenLayout({
    required this.navigationShell,
    required this.canManageOrganization,
    required this.isAdmin,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final signOutFocusNode = useFocusNode();

    return Row(
      children: [
        NavigationRail(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: onDestinationSelected,
          labelType: NavigationRailLabelType.all,
          groupAlignment: -1.0,
          trailing: Expanded(
            child: Align(
              alignment: Alignment.bottomCenter,
              child: Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: IconButton(
                    key: const Key('nav_rail_sign_out_btn'),
                    focusNode: signOutFocusNode,
                    tooltip: l10n.signOutBtn,
                    icon: const Icon(Icons.logout),
                    onPressed: () {
                      ref.read(authControllerProvider.notifier).signOut();
                    },
                  ),
                ),
              ),
            ),
          ),
          destinations: [
            NavigationRailDestination(
              icon: const Icon(Icons.dashboard_outlined),
              selectedIcon: const Icon(Icons.dashboard),
              label: Text(l10n.navDashboard, overflow: TextOverflow.ellipsis),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.add_circle_outline),
              selectedIcon: const Icon(Icons.add_circle),
              label: Text(l10n.newAnalysis, overflow: TextOverflow.ellipsis),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.person_outline),
              selectedIcon: const Icon(Icons.person),
              label: Text(l10n.navProfile, overflow: TextOverflow.ellipsis),
            ),
            if (canManageOrganization)
              NavigationRailDestination(
                icon: const Icon(Icons.corporate_fare_outlined),
                selectedIcon: const Icon(Icons.corporate_fare),
                label: Text(
                  l10n.navOrganization,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            if (isAdmin)
              NavigationRailDestination(
                icon: const Icon(Icons.admin_panel_settings_outlined),
                selectedIcon: const Icon(Icons.admin_panel_settings),
                label: Text(l10n.navAdmin, overflow: TextOverflow.ellipsis),
              ),
          ],
        ),
        const VerticalDivider(thickness: 1, width: 1),
        Expanded(child: navigationShell),
      ],
    );
  }
}
