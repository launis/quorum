import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

import 'package:client_app/features/studio/models/prompt_block.dart';

void main() {
  group('Domain Parity (Isolate.run) strict tests', () {
    late String seedJsonString;
    late Map<String, dynamic> seedData;

    setUpAll(() {
      // Look for backend_v2/seed/seed_data.json
      // Since tests can be run from client_app_v2 or root, try both paths
      var currentDir = Directory.current.path;
      var seedFile = File('$currentDir/../../backend_v2/seed/seed_data.json');
      
      if (!seedFile.existsSync()) {
        seedFile = File('$currentDir/../backend_v2/seed/seed_data.json');
      }
      
      if (!seedFile.existsSync()) {
        fail('Epic 12 Fatal: seed_data.json not found. PWD=$currentDir');
      }
      
      seedJsonString = seedFile.readAsStringSync();
      seedData = jsonDecode(seedJsonString) as Map<String, dynamic>;
    });

    test('Isolate parsing extracts PromptBlocks perfectly from SSoT', () async {
      final rawBlocks = seedData['prompt_blocks'] as List<dynamic>;
      expect(rawBlocks.isNotEmpty, true, reason: 'Seed should have prompt blocks');

      // Send the large list into Isolate via our V2 static method
      final List<PromptBlock> parsedBlocks = 
          await PromptBlock.parseListInBackground(rawBlocks);

      // Verify that parsed block count matches raw count
      expect(parsedBlocks.length, rawBlocks.length);
      
      // Verify the list has items
      final bool hasBlocks = parsedBlocks.isNotEmpty;
      expect(hasBlocks, true, reason: 'Parsed blocks list must not be empty');
    });

    test('Strict mode intercepts maliciously modified payloads without crashing main thread', () async {
      // Pick the first valid prompt block as base
      final rawBlocks = seedData['prompt_blocks'] as List<dynamic>;
      final validMap = Map<String, dynamic>.from(rawBlocks.first as Map<String, dynamic>);
      
      // Inject an illegal field
      validMap['malicious_dart_key'] = 'injection_attempt';

      // Send to background parser and expect FREEZED CheckedFromJsonException 
      // (which confirms `disallow_unrecognized_keys: true` works inside Isolate)
      final rawList = [validMap];
      
      // We wrap the await in expect to check the thrown Exception
      expect(
        () async => await PromptBlock.parseListInBackground(rawList),
        throwsA(isA<CheckedFromJsonException>()),
        reason: 'Freezed must strictly reject unrecognized keys, adhering to Pydantic V2 Fail-Fast parity.',
      );
    });
  });
}
