import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/api/api_client.dart';

class KnowledgeStatus {
  final bool hasDocuments;
  final int documentCount;
  final int precedentCount;

  const KnowledgeStatus({
    required this.hasDocuments,
    required this.documentCount,
    required this.precedentCount,
  });

  factory KnowledgeStatus.fromJson(Map<String, dynamic> json) {
    return KnowledgeStatus(
      hasDocuments: json['has_documents'] as bool,
      documentCount: json['document_count'] as int,
      precedentCount: json['precedent_count'] as int,
    );
  }
}

final knowledgeStatusProvider = FutureProvider.autoDispose<KnowledgeStatus>((ref) async {
  final apiClient = ref.watch(apiClientProvider);
  final response = await apiClient.get('/v1/config/knowledge/status');
  return KnowledgeStatus.fromJson(response.data);
});
