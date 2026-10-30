import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('generateOpaqueUuid7 & StrictOpaqueIdConverter Tests', () {
    test(
      'Positive: generateOpaqueUuid7 generates 32-hex RFC 9562 UUIDv7 matching StrictOpaqueIdConverter',
      () {
        const converter = StrictOpaqueIdConverter();
        final srId = generateOpaqueUuid7('sr');
        final grpId = generateOpaqueUuid7('grp');
        final tdaId = generateOpaqueUuid7('tda');

        expect(srId, matches(RegExp(r'^sr_[0-9a-f]{32}$')));
        expect(grpId, matches(RegExp(r'^grp_[0-9a-f]{32}$')));
        expect(tdaId, matches(RegExp(r'^tda_[0-9a-f]{32}$')));

        // RFC 9562 UUIDv7 version nibble is at hex character index 12 (0-based after prefix_)
        final srHex = srId.split('_')[1];
        expect(srHex.length, equals(32));
        expect(srHex[12], equals('7'));

        expect(converter.fromJson(srId), equals(srId));
        expect(converter.toJson(srId), equals(srId));
      },
    );

    test(
      'Negative 1: StrictOpaqueIdConverter rejects legacy 16-hex and 31-hex strings with AppException',
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
      },
    );

    test(
      'Negative 2: generateOpaqueUuid7 and StrictOpaqueIdConverter reject invalid prefixes with AppException',
      () {
        const converter = StrictOpaqueIdConverter();

        expect(() => generateOpaqueUuid7('x'), throwsA(isA<AppException>()));
        expect(
          () => generateOpaqueUuid7('too_long_prefix'),
          throwsA(isA<AppException>()),
        );
        expect(() => generateOpaqueUuid7('123'), throwsA(isA<AppException>()));
        expect(
          () => converter.fromJson('x_0195f3a0000070008000000000000001'),
          throwsA(isA<AppException>()),
        );
      },
    );
  });
}
