import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';

enum _TestEnum { alpha, beta }

void main() {
  group('generateOpaqueUuid7 & StrictOpaqueIdConverter Tests', () {
    test(
      'Positive: generateOpaqueUuid7 generates 32-hex RFC 9562 UUIDv7 matching StrictOpaqueIdConverter',
      () {
        const converter = StrictOpaqueIdConverter();
        final srId = generateOpaqueUuid7('sr');
        final grpId = generateOpaqueUuid7('grp');
        final tdaId = generateOpaqueUuid7('tda');
        final maxPrefixId = generateOpaqueUuid7('abcde');

        expect(srId, matches(RegExp(r'^sr_[0-9a-f]{32}$')));
        expect(grpId, matches(RegExp(r'^grp_[0-9a-f]{32}$')));
        expect(tdaId, matches(RegExp(r'^tda_[0-9a-f]{32}$')));
        expect(maxPrefixId, matches(RegExp(r'^abcde_[0-9a-f]{32}$')));

        // RFC 9562 UUIDv7 version nibble is at hex character index 12 (0-based after prefix_)
        final srHex = srId.split('_')[1];
        expect(srHex.length, equals(32));
        expect(srHex[12], equals('7'));

        expect(converter.fromJson(srId), equals(srId));
        expect(converter.toJson(srId), equals(srId));
      },
    );

    test(
      'Negative 1: StrictOpaqueIdConverter rejects legacy 16-hex, 31-hex, and 33-hex strings on fromJson and toJson with AppException',
      () {
        const converter = StrictOpaqueIdConverter();

        expect(
          () => converter.fromJson('grp_0123456789abcdef'),
          throwsA(isA<AppException>()),
        );
        expect(
          () => converter.fromJson('sr_0195f3a000007000800000000000000'),
          throwsA(isA<AppException>()),
        );
        expect(
          () => converter.fromJson('sr_0195f3a00000700080000000000000012'),
          throwsA(isA<AppException>()),
        );
        expect(
          () => converter.toJson('grp_0123456789abcdef'),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'Negative 2: generateOpaqueUuid7 and StrictOpaqueIdConverter reject invalid prefixes (min-1, max+1, non-alpha) with AppException',
      () {
        const converter = StrictOpaqueIdConverter();

        expect(() => generateOpaqueUuid7(''), throwsA(isA<AppException>()));
        expect(() => generateOpaqueUuid7('x'), throwsA(isA<AppException>()));
        expect(
          () => generateOpaqueUuid7('abcdef'),
          throwsA(isA<AppException>()),
        );
        expect(() => generateOpaqueUuid7('123'), throwsA(isA<AppException>()));
        expect(
          () => converter.fromJson('x_0195f3a0000070008000000000000001'),
          throwsA(isA<AppException>()),
        );
        expect(
          () => converter.fromJson('abcdef_0195f3a0000070008000000000000001'),
          throwsA(isA<AppException>()),
        );
      },
    );
  });

  group('StrictDateTimeConverter Tests', () {
    const converter = StrictDateTimeConverter();

    test(
      'Positive: StrictDateTimeConverter parses ISO-8601 string to UTC DateTime and serializes back',
      () {
        const isoUtc = '2026-10-30T12:00:00.000Z';
        final parsed = converter.fromJson(isoUtc);
        expect(parsed.isUtc, isTrue);
        expect(converter.toJson(parsed), equals(isoUtc));
      },
    );

    test(
      'Negative 1: StrictDateTimeConverter throws AppException on malformed DateTime string',
      () {
        expect(
          () => converter.fromJson('not-a-date'),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'Negative 2: StrictDateTimeConverter throws AppException on empty string boundary',
      () {
        expect(() => converter.fromJson(''), throwsA(isA<AppException>()));
      },
    );
  });

  group('StrictEnumConverter Tests', () {
    test(
      'Positive: StrictEnumConverter roundtrips enum values using default name and custom toJsonFn',
      () {
        const defaultConverter = StrictEnumConverter(_TestEnum.values);
        expect(defaultConverter.fromJson('alpha'), equals(_TestEnum.alpha));
        expect(defaultConverter.toJson(_TestEnum.beta), equals('beta'));

        final customConverter = StrictEnumConverter<_TestEnum>(
          _TestEnum.values,
          toJsonFn: (e) => e.name.toUpperCase(),
        );
        expect(customConverter.fromJson('ALPHA'), equals(_TestEnum.alpha));
        expect(customConverter.toJson(_TestEnum.beta), equals('BETA'));
      },
    );

    test(
      'Negative 1: StrictEnumConverter throws AppException on unrecognized enum string',
      () {
        const converter = StrictEnumConverter(_TestEnum.values);
        expect(
          () => converter.fromJson('gamma'),
          throwsA(isA<AppException>()),
        );
      },
    );

    test(
      'Negative 2: StrictEnumConverter throws AppException on empty string or case mismatch',
      () {
        const converter = StrictEnumConverter(_TestEnum.values);
        expect(() => converter.fromJson(''), throwsA(isA<AppException>()));
        expect(
          () => converter.fromJson('ALPHA'),
          throwsA(isA<AppException>()),
        );
      },
    );
  });
}
