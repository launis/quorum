import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/features/studio/models/performative_lexicon.dart';
import 'package:client_app/core/logging/logger_service.dart';

part 'lexicon_controller.g.dart';

@riverpod
class LexiconController extends _$LexiconController {
  @override
  FutureOr<SystemConfigPerformativeLexicons> build() async {
    return _fetchLexicons();
  }

  Future<SystemConfigPerformativeLexicons> _fetchLexicons() async {
    final client = ref.read(studioClientProvider);
    final rawData = await client.getLexicons();
    return SystemConfigPerformativeLexicons.fromJson(rawData);
  }

  Future<void> fetchLexicons() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      return await _fetchLexicons();
    });
  }

  Future<void> saveLexicons(SystemConfigPerformativeLexicons config) async {
    final previousState = state;
    state = AsyncData(config);

    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.saveLexicons(config.toJson());
      state = AsyncData(SystemConfigPerformativeLexicons.fromJson(rawResponse));
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('LexiconController', 'Save failed', e, st);
      rethrow;
    }
  }

  Future<List<String>> discoverPhrases(String langCode) async {
    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.discoverLexiconPhrases(langCode);
      final dto = LexiconSuggestionListDTO.fromJson(rawResponse);
      return dto.suggestedPhrases;
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('LexiconController', 'Discover failed for $langCode', e, st);
      rethrow;
    }
  }

  Future<List<String>> translatePhrases(String langCode) async {
    try {
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.translateLexiconPhrases(langCode);
      final dto = LexiconSuggestionListDTO.fromJson(rawResponse);
      return dto.suggestedPhrases;
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('LexiconController', 'Translate failed for $langCode', e, st);
      rethrow;
    }
  }
}
