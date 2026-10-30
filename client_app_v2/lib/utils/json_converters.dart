import 'package:client_app/core/error/app_exception.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:uuid/uuid.dart';

final RegExp _opaquePrefixRegex = RegExp(r'^[a-z]{2,5}$');
final RegExp _opaqueStripeIdRegex = RegExp(
  r'^[a-z]{2,5}_[a-f0-9]{32}$',
  caseSensitive: false,
);

/// Generates a canonical 32-character hexadecimal RFC 9562 UUIDv7 Opaque Stripe ID.
String generateOpaqueUuid7(String prefix) {
  final cleanedPrefix = prefix.trim().toLowerCase();
  if (!_opaquePrefixRegex.hasMatch(cleanedPrefix)) {
    throw AppException.validation(
      'Invalid Opaque ID prefix: "$prefix". Expected 2-5 lowercase ASCII letters.',
    );
  }
  final hexPayload = const Uuid().v7().replaceAll('-', '').toLowerCase();
  return '${cleanedPrefix}_$hexPayload';
}

/// Converter for DateTime objects expecting ISO-8601 UTC strings.
class StrictDateTimeConverter implements JsonConverter<DateTime, String> {
  const StrictDateTimeConverter();

  @override
  DateTime fromJson(String json) {
    try {
      return DateTime.parse(json).toUtc();
    } catch (e) {
      throw AppException.validation(
        'Invalid DateTime format: $json. Expected ISO-8601. Detail: $e',
      );
    }
  }

  @override
  String toJson(DateTime object) {
    return object.toUtc().toIso8601String();
  }
}

/// Strict Enum converter without fallback values.
/// Throws AppException immediately if an unrecognized enum value is received.
class StrictEnumConverter<T extends Enum> implements JsonConverter<T, String> {
  final List<T> enumValues;
  final String Function(T)? toJsonFn;

  const StrictEnumConverter(this.enumValues, {this.toJsonFn});

  @override
  T fromJson(String json) {
    for (final value in enumValues) {
      final backendValue = toJsonFn != null ? toJsonFn!(value) : value.name;
      if (backendValue == json) {
        return value;
      }
    }
    throw AppException.validation(
      'Invalid enum value: "$json". Expected one of: ${enumValues.map((e) => toJsonFn != null ? toJsonFn!(e) : e.name).join(', ')}.',
    );
  }

  @override
  String toJson(T object) {
    return toJsonFn != null ? toJsonFn!(object) : object.name;
  }
}

/// Opaque ID converter enforcing 32-character hexadecimal RFC 9562 UUIDv7 format.
class StrictOpaqueIdConverter implements JsonConverter<String, String> {
  const StrictOpaqueIdConverter();

  @override
  String fromJson(String json) {
    if (!_opaqueStripeIdRegex.hasMatch(json)) {
      throw AppException.validation(
        'Invalid Opaque Stripe ID format: "$json". Must start with a 2-5 letter prefix, followed by underscore and exactly 32 hex characters.',
      );
    }
    return json;
  }

  @override
  String toJson(String object) {
    if (!_opaqueStripeIdRegex.hasMatch(object)) {
      throw AppException.validation(
        'Invalid Opaque Stripe ID format: "$object". Must start with a 2-5 letter prefix, followed by underscore and exactly 32 hex characters.',
      );
    }
    return object;
  }
}
