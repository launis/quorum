import 'package:client_app/core/error/app_exception.dart';
import 'package:json_annotation/json_annotation.dart';

/// Konvertteri DateTime-objekteille. Odottaa ISO-8601 muotoiltua stringiä (UTC).
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

/// Strict Enum Konvertteri. Ei tunne varatyylejä (Fallback / Unknown).
/// Kaatuu heti heittäen AppExceptionin jos backendistä tulee tuntematon data-kenttä.
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

/// Opaque ID Konvertteri. Varmistaa RegExillä että tunnisteet ovat aitoja.
class StrictOpaqueIdConverter implements JsonConverter<String, String> {
  const StrictOpaqueIdConverter();

  @override
  String fromJson(String json) {
    final regex = RegExp(r'^[a-z]{2,5}_[a-f0-9]{16,32}$', caseSensitive: false);
    if (!regex.hasMatch(json)) {
      throw AppException.validation(
        'Invalid Opaque Stripe ID format: "$json". Must start with a 2-5 letter prefix, followed by underscore and exactly 16-32 hex characters.',
      );
    }
    return json;
  }

  @override
  String toJson(String object) {
    return object;
  }
}
