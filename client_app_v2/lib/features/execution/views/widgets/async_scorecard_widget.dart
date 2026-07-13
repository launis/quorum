import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'package:client_app/features/execution/providers/scorecard_provider.dart';
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/error/app_exception.dart';

class AsyncScorecardWidget extends ConsumerWidget {
  final String executionId;

  const AsyncScorecardWidget({super.key, required this.executionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scorecardAsync = ref.watch(scorecardProvider(executionId));

    return scorecardAsync.when(
      data: (scorecardDto) {
        return DiagnosticScorecardWidget(
          executionId: executionId,
          evaluativeMatrices: scorecardDto.evaluativeMatrices,
          informationalMatrices: scorecardDto.informationalMatrices,
          visibleColumns: const [
            'label',
            'score',
            'distribution',
            'row_explanation',
            'quotes',
          ],
        );
      },
      loading: () => const Padding(
        padding: EdgeInsets.all(24.0),
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) {
        // AppErrorBoundary pattern dictates we catch gracefully
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: ErrorView(
            error: AppException.validation(error.toString()),
            stackTrace: stack,
            onRetry: () => ref.invalidate(scorecardProvider(executionId)),
          ),
        );
      },
    );
  }
}
