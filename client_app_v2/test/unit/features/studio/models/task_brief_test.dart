import 'dart:convert';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/task_brief.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

void main() {
  group('TaskBrief Model Unit & ISTQB Boundary Tests', () {
    const validBriefId = 'tbr_0195f3a00000700d8a1b2c3d4e5f6001';
    const validOrgId = 'org_0195f3a0000070008000000000000001';
    const sampleLabel = I18nText(
      translations: {'en': 'Executive Case Brief', 'fi': 'Johdon tehtävänanto'},
    );
    const sampleDesc = I18nText(
      translations: {
        'en': 'Reusable task brief',
        'fi': 'Uudelleenkäytettävä ohje',
      },
    );

    test(
      'Positive: Deserializes, serializes, and parses TaskBrief in background isolates with 1:1 wire parity',
      () async {
        final rawMap = <String, dynamic>{
          'id': validBriefId,
          'slug': 'executive_case_brief',
          'organization_id': validOrgId,
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'instruction_text': 'Analyze the strategic board deck.',
          'source_url': 'https://docs.qrum.ai/case-brief.pdf',
        };

        final brief = TaskBrief.fromJson(rawMap);
        expect(brief.id, equals(validBriefId));
        expect(brief.slug, equals('executive_case_brief'));
        expect(brief.organizationId, equals(validOrgId));
        expect(brief.label.translations['en'], equals('Executive Case Brief'));
        expect(
          brief.instructionText,
          equals('Analyze the strategic board deck.'),
        );
        expect(brief.sourceUrl, equals('https://docs.qrum.ai/case-brief.pdf'));

        final roundtrip = TaskBrief.fromJson(brief.toJson());
        expect(roundtrip.id, equals(validBriefId));
        expect(roundtrip.sourceUrl, equals(brief.sourceUrl));

        final parsedSingle = await TaskBrief.parseInBackground(
          jsonEncode(rawMap),
        );
        expect(parsedSingle.id, equals(validBriefId));

        final parsedList = await TaskBrief.parseListInBackground(<Object?>[
          rawMap,
        ]);
        expect(parsedList, hasLength(1));
        expect(parsedList.single.slug, equals('executive_case_brief'));
      },
    );

    test(
      'Negative Partition 1 (BVA): StrictOpaqueIdConverter rejects 31-hex (min-1) and 33-hex (max+1) IDs on TaskBrief',
      () {
        final shortIdJson = <String, dynamic>{
          'id': 'tbr_0195f3a00000700d8a1b2c3d4e5f600',
          'slug': 'short_id_brief',
          'organization_id': validOrgId,
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'instruction_text': 'Valid instructions',
        };
        expect(
          () => TaskBrief.fromJson(shortIdJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final longIdJson = <String, dynamic>{
          'id': 'tbr_0195f3a00000700d8a1b2c3d4e5f6001a',
          'slug': 'long_id_brief',
          'organization_id': validOrgId,
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'instruction_text': 'Valid instructions',
        };
        expect(
          () => TaskBrief.fromJson(longIdJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );

    test(
      'Negative Partition 2: disallowUnrecognizedKeys rejects unknown properties and background parsers reject non-Map payloads',
      () async {
        final pollutedJson = <String, dynamic>{
          'id': validBriefId,
          'slug': 'polluted_brief',
          'organization_id': validOrgId,
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
          'instruction_text': 'Valid instructions',
          'unexpected_shadow_key': 'must_crash',
        };
        expect(
          () => TaskBrief.fromJson(pollutedJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        await expectLater(
          TaskBrief.parseInBackground('["not_a_json_object"]'),
          throwsA(isA<AppException>()),
        );
        await expectLater(
          TaskBrief.parseListInBackground(<Object?>['invalid_item']),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'Negative Partition 3: TaskBrief rejects null, omitted, or legacy SYSTEM organization_id',
      () {
        final omittedOrgJson = <String, dynamic>{
          'id': validBriefId,
          'slug': 'omitted_org_brief',
          'label': sampleLabel.toJson(),
          'description': sampleDesc.toJson(),
        };
        expect(
          () => TaskBrief.fromJson(omittedOrgJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final nullOrgJson = <String, dynamic>{
          ...omittedOrgJson,
          'organization_id': null,
        };
        expect(
          () => TaskBrief.fromJson(nullOrgJson),
          throwsA(isA<CheckedFromJsonException>()),
        );

        final systemOrgJson = <String, dynamic>{
          ...omittedOrgJson,
          'organization_id': 'SYSTEM',
        };
        expect(
          () => TaskBrief.fromJson(systemOrgJson),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
