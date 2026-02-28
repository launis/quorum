import 'dart:async';
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../models/knowledge_base.dart';
import '../../../repositories/knowledge_repository.dart';
import 'package:client_app/features/knowledge/presentation/providers/knowledge_status_provider.dart';

part 'ingestion_controller.g.dart';

@riverpod
class IngestionController extends _$IngestionController {
  Timer? _timer;

  /// Builds the initial state of the ingestion process.
  ///
  /// Returns an [AsyncValue<IngestionStatus?>] which is initially `null` (no active upload).
  /// Automatically cancels the polling timer when the provider is disposed.
  @override
  AsyncValue<IngestionStatus?> build() {
    // Cancel timer on dispose
    ref.onDispose(() {
      _timer?.cancel();
    });
    return const AsyncValue.data(null);
  }

  /// Initiates the ingestion workflow for the selected [file].
  ///
  /// 1. Uploads the file to the backend via [KnowledgeRepository].
  /// 2. Sets state to `AsyncValue.loading()`.
  /// 3. Upon successful upload, starts periodic polling for job status.
  /// 4. Handles errors by setting state to `AsyncValue.error`.
  Future<void> startIngestion(File file, {String? modelStrategy}) async {
    state = const AsyncValue.loading();
    try {
      final repo = ref.read(knowledgeRepositoryProvider.notifier);

      // 1. Upload & Get Job ID
      final jobId = await repo.uploadKnowledgeBase(
        file,
        modelStrategy: modelStrategy,
      );

      // 2. Start Polling
      _startPolling(jobId);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Resets the knowledge base content.
  Future<void> resetKnowledgeBase() async {
    state = const AsyncValue.loading();
    try {
      final repo = ref.read(knowledgeRepositoryProvider.notifier);
      await repo.resetKnowledgeBase();
      state = const AsyncValue.data(null);
      // Ensure UI updates the document count back to 0
      ref.invalidate(knowledgeStatusProvider);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Internal: Starts a periodic timer to poll ingestion status every second.
  ///
  /// Stops polling when the status is 'completed' or 'failed'.
  void _startPolling(String jobId) {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(milliseconds: 1000), (timer) async {
      try {
        final repo = ref.read(knowledgeRepositoryProvider.notifier);
        final status = await repo.getIngestionStatus(jobId);

        state = AsyncValue.data(status);

        if (status.status == 'completed') {
          ref.invalidate(knowledgeStatusProvider); // Refresh the status banner
          timer.cancel();
        } else if (status.status == 'failed') {
          timer.cancel();
        }
      } catch (e) {
        // If polling fails, we set error state to stop the spinner and notify UI.
        state = AsyncValue.error(e, StackTrace.current);
        timer.cancel();
      }
    });
  }

  /// Resets the state to initial (null), clearing any errors or progress.
  void resetState() {
    _timer?.cancel();
    state = const AsyncValue.data(null);
  }
}

@riverpod
Future<List<KnowledgeModelStrategy>> knowledgeStrategies(Ref ref) async {
  final repo = ref.watch(knowledgeRepositoryProvider.notifier);
  return repo.getModels();
}
