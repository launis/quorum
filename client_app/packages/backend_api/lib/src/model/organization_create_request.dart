//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/subscription_status.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization_create_request.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class OrganizationCreateRequest {
  /// Returns a new [OrganizationCreateRequest] instance.
  OrganizationCreateRequest({

     this.id,

    required  this.name,

     this.tier = 'standard',

     this.contactEmail,

     this.billingId,

     this.subscriptionStatus = SubscriptionStatus.trial,

     this.quotaLimit = 10.0,

     this.settingsOverride,
  });

  @JsonKey(
    
    name: r'id',
    required: false,
    
  )


  final String? id;



  @JsonKey(
    
    name: r'name',
    required: true,
    
  )


  final String name;



  @JsonKey(
    defaultValue: 'standard',
    name: r'tier',
    required: false,
    
  )


  final String? tier;



  @JsonKey(
    
    name: r'contact_email',
    required: false,
    
  )


  final String? contactEmail;



  @JsonKey(
    
    name: r'billing_id',
    required: false,
    
  )


  final String? billingId;



  @JsonKey(
    defaultValue: SubscriptionStatus.trial,
    name: r'subscription_status',
    required: false,
    
  )


  final SubscriptionStatus? subscriptionStatus;



  @JsonKey(
    defaultValue: 10.0,
    name: r'quota_limit',
    required: false,
    
  )


  final num? quotaLimit;



  @JsonKey(
    
    name: r'settings_override',
    required: false,
    
  )


  final Map<String, Object>? settingsOverride;





    @override
    bool operator ==(Object other) => identical(this, other) || other is OrganizationCreateRequest &&
      other.id == id &&
      other.name == name &&
      other.tier == tier &&
      other.contactEmail == contactEmail &&
      other.billingId == billingId &&
      other.subscriptionStatus == subscriptionStatus &&
      other.quotaLimit == quotaLimit &&
      other.settingsOverride == settingsOverride;

    @override
    int get hashCode =>
        (id == null ? 0 : id.hashCode) +
        name.hashCode +
        tier.hashCode +
        (contactEmail == null ? 0 : contactEmail.hashCode) +
        (billingId == null ? 0 : billingId.hashCode) +
        subscriptionStatus.hashCode +
        quotaLimit.hashCode +
        (settingsOverride == null ? 0 : settingsOverride.hashCode);

  factory OrganizationCreateRequest.fromJson(Map<String, dynamic> json) => _$OrganizationCreateRequestFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationCreateRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

