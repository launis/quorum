//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:json_annotation/json_annotation.dart';

/// SaaS Subscription Status.
enum SubscriptionStatus {
          /// SaaS Subscription Status.
      @JsonValue(r'active')
      active(r'active'),
          /// SaaS Subscription Status.
      @JsonValue(r'past_due')
      pastDue(r'past_due'),
          /// SaaS Subscription Status.
      @JsonValue(r'canceled')
      canceled(r'canceled'),
          /// SaaS Subscription Status.
      @JsonValue(r'trial')
      trial(r'trial');

  const SubscriptionStatus(this.value);

  final String value;

  @override
  String toString() => value;
}
