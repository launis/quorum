import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/api/api_client.dart';
import 'package:client_app/features/admin/data/system_repository.dart';

part 'system_providers.g.dart';

@Riverpod(keepAlive: true)
SystemRepository systemRepository(Ref ref) {
  return SystemRepository(ref.watch(apiClientProvider));
}
