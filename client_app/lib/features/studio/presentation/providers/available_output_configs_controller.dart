import 'package:client_app/features/studio/data/studio_repository.dart';
import 'package:client_app/features/studio/domain/models/component_def.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'available_output_configs_controller.g.dart';

@riverpod
class AvailableOutputConfigsController extends _$AvailableOutputConfigsController {
  @override
  FutureOr<List<StudioComponentDef>> build() async {
    return ref.watch(studioRepositoryProvider).getOutputConfigs();
  }

  Future<void> saveOutputConfig(StudioComponentDef config) async {
    final previousState = state;
    final currentList = state.value ?? [];
    
    final isNew = !currentList.any((c) => c.id == config.id);
    final newList = isNew 
      ? [...currentList, config]
      : currentList.map((c) => c.id == config.id ? config : c).toList();
      
    state = AsyncData(newList);

    try {
      await ref.read(studioRepositoryProvider).saveOutputConfig(config);
      ref.invalidateSelf();
    } catch (e) {
      state = previousState;
      rethrow;
    }
  }
}
