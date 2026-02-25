import 'package:client_app/features/orchestration/presentation/screens/analysis_wizard_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

part 'orchestration_routes.g.dart';

@TypedGoRoute<NewAnalysisRoute>(path: '/orchestration/new')
class NewAnalysisRoute extends GoRouteData with $NewAnalysisRoute {
  const NewAnalysisRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const AnalysisWizardScreen();
  }
}
