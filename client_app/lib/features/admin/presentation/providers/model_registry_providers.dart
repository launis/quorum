import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../../api/api_client.dart';
import '../../data/model_registry_repository.dart';

part 'model_registry_providers.g.dart';

@riverpod
ModelRegistryRepository modelRegistryRepository(Ref ref) {
  final client = ref.watch(apiClientProvider);
  return ModelRegistryRepository(client);
}
