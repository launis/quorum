//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:json_annotation/json_annotation.dart';


enum SectionType {
      @JsonValue(r'SCORE_CARD')
      SCORE_CARD(r'SCORE_CARD'),
      @JsonValue(r'MARKDOWN_BLOCK')
      MARKDOWN_BLOCK(r'MARKDOWN_BLOCK'),
      @JsonValue(r'TIMELINE_FEED')
      TIMELINE_FEED(r'TIMELINE_FEED'),
      @JsonValue(r'HEADER')
      HEADER(r'HEADER'),
      @JsonValue(r'KEY_METRICS')
      KEY_METRICS(r'KEY_METRICS'),
      @JsonValue(r'EVIDENCE_LIST')
      EVIDENCE_LIST(r'EVIDENCE_LIST'),
      @JsonValue(r'KEY_VALUE_GRID')
      KEY_VALUE_GRID(r'KEY_VALUE_GRID'),
      @JsonValue(r'DATA_TABLE')
      DATA_TABLE(r'DATA_TABLE'),
      @JsonValue(r'ACCORDION')
      ACCORDION(r'ACCORDION'),
      @JsonValue(r'USAGE_STATS')
      USAGE_STATS(r'USAGE_STATS'),
      @JsonValue(r'LOGIC_ANALYSIS')
      LOGIC_ANALYSIS(r'LOGIC_ANALYSIS'),
      @JsonValue(r'STRESS_TEST')
      STRESS_TEST(r'STRESS_TEST'),
      @JsonValue(r'CAUSAL_ANALYSIS')
      CAUSAL_ANALYSIS(r'CAUSAL_ANALYSIS'),
      @JsonValue(r'PERFORMATIVITY_CHECK')
      PERFORMATIVITY_CHECK(r'PERFORMATIVITY_CHECK'),
      @JsonValue(r'FACT_CHECK')
      FACT_CHECK(r'FACT_CHECK'),
      @JsonValue(r'PROFILER_ANALYSIS')
      PROFILER_ANALYSIS(r'PROFILER_ANALYSIS'),
      @JsonValue(r'ARCHIVIST_CHECK')
      ARCHIVIST_CHECK(r'ARCHIVIST_CHECK'),
      @JsonValue(r'DRIVER_PROFILE')
      DRIVER_PROFILE(r'DRIVER_PROFILE'),
      @JsonValue(r'SECURITY_CHECK')
      SECURITY_CHECK(r'SECURITY_CHECK');

  const SectionType(this.value);

  final String value;

  @override
  String toString() => value;
}
