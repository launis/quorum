import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/prompt_block_category.dart';

void main() {
  group('PromptBlockCategory', () {
    test('successfully parses execution_persona category without crashing', () {
      final category = PromptBlockCategory.fromId('execution_persona');
      expect(category, PromptBlockCategory.executionPersona);
    });
  });
}
