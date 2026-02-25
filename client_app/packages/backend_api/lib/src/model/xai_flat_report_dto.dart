//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'xai_flat_report_dto.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class XAIFlatReportDTO {
  /// Returns a new [XAIFlatReportDTO] instance.
  XAIFlatReportDTO({

    required  this.executionId,

    required  this.timestamp,

    required  this.verdict,

    required  this.scoreTotal,

    required  this.confidenceScore,

     this.topStrengthId,

     this.topWeaknessId,

     this.flattenedScores,
  });

      /// The unique ID of the workflow execution.
  @JsonKey(
    
    name: r'execution_id',
    required: true,
    
  )


  final String executionId;



      /// When this report was generated.
  @JsonKey(
    
    name: r'timestamp',
    required: true,
    
  )


  final DateTime timestamp;



      /// Final decision (e.g., 'Approved', 'Rejected').
  @JsonKey(
    
    name: r'verdict',
    required: true,
    
  )


  final String verdict;



      /// The total calculated score (0.0 - 5.0).
  @JsonKey(
    
    name: r'score_total',
    required: true,
    
  )


  final num scoreTotal;



      /// AI confidence in the result (0.0 - 1.0).
  @JsonKey(
    
    name: r'confidence_score',
    required: true,
    
  )


  final num confidenceScore;



  @JsonKey(
    
    name: r'top_strength_id',
    required: false,
    
  )


  final String? topStrengthId;



  @JsonKey(
    
    name: r'top_weakness_id',
    required: false,
    
  )


  final String? topWeaknessId;



      /// Key-value map of dimension IDs to their numeric scores.
  @JsonKey(
    
    name: r'flattened_scores',
    required: false,
    
  )


  final Map<String, num>? flattenedScores;





    @override
    bool operator ==(Object other) => identical(this, other) || other is XAIFlatReportDTO &&
      other.executionId == executionId &&
      other.timestamp == timestamp &&
      other.verdict == verdict &&
      other.scoreTotal == scoreTotal &&
      other.confidenceScore == confidenceScore &&
      other.topStrengthId == topStrengthId &&
      other.topWeaknessId == topWeaknessId &&
      other.flattenedScores == flattenedScores;

    @override
    int get hashCode =>
        executionId.hashCode +
        timestamp.hashCode +
        verdict.hashCode +
        scoreTotal.hashCode +
        confidenceScore.hashCode +
        (topStrengthId == null ? 0 : topStrengthId.hashCode) +
        (topWeaknessId == null ? 0 : topWeaknessId.hashCode) +
        flattenedScores.hashCode;

  factory XAIFlatReportDTO.fromJson(Map<String, dynamic> json) => _$XAIFlatReportDTOFromJson(json);

  Map<String, dynamic> toJson() => _$XAIFlatReportDTOToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

