import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';


/// tests for PlaygroundApi
void main() {
  final instance = BackendApi().getPlaygroundApi();

  group(PlaygroundApi, () {
    // Run Prompt
    //
    // Executes a prompt template with variables against the LLM.
    //
    //Future<PlaygroundResponse> runPromptBuilderPlaygroundRunPost(PlaygroundRequest playgroundRequest) async
    test('test runPromptBuilderPlaygroundRunPost', () async {
      // TODO
    });

  });
}
