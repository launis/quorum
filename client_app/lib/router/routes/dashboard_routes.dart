import 'package:client_app/features/dashboard/presentation/screens/dashboard_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_monitor_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_result_screen.dart';
import 'package:client_app/features/orchestration/presentation/screens/execution_details_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

part 'dashboard_routes.g.dart';

@TypedGoRoute<DashboardHomeRoute>(
  path: '/dashboard',
  routes: [
    TypedGoRoute<ExecutionMonitorRoute>(path: 'executions/:executionId/monitor'),
    TypedGoRoute<ExecutionResultRoute>(path: 'executions/:executionId/report'),
    TypedGoRoute<ExecutionDetailsRoute>(path: 'executions/:executionId/details'),
  ]
)
class DashboardHomeRoute extends GoRouteData with $DashboardHomeRoute {
  const DashboardHomeRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const DashboardScreen();
  }
}

class ExecutionMonitorRoute extends GoRouteData with $ExecutionMonitorRoute {
  final String executionId;
  const ExecutionMonitorRoute(this.executionId);

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return ExecutionMonitorScreen(executionId: executionId);
  }
}

class ExecutionResultRoute extends GoRouteData with $ExecutionResultRoute {
  final String executionId;
  const ExecutionResultRoute(this.executionId);

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return ExecutionResultScreen(executionId: executionId);
  }
}

class ExecutionDetailsRoute extends GoRouteData with $ExecutionDetailsRoute {
  final String executionId;
  const ExecutionDetailsRoute(this.executionId);

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return ExecutionDetailsScreen(executionId: executionId);
  }
}
