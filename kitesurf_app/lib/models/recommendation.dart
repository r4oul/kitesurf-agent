class Conditions {
  final double windSpeedKnots;
  final double windGustKnots;
  final String windDirection;
  final String tideState;
  final String tideDirection;
  final String fetchedAt;
  final String windModel;

  Conditions({
    required this.windSpeedKnots,
    required this.windGustKnots,
    required this.windDirection,
    required this.tideState,
    required this.tideDirection,
    required this.fetchedAt,
    this.windModel = '',
  });

  factory Conditions.fromJson(Map<String, dynamic> json) {
    return Conditions(
      windSpeedKnots: (json['wind_speed_knots'] as num).toDouble(),
      windGustKnots: (json['wind_gust_knots'] as num).toDouble(),
      windDirection: json['wind_direction'] ?? '',
      tideState: json['tide_state'] ?? '',
      tideDirection: json['tide_direction'] ?? '',
      fetchedAt: json['fetched_at'] ?? '',
      windModel: json['wind_model'] ?? '',
    );
  }
}

class Recommendation {
  final int beachId;
  final String beachName;
  final int score;
  final List<String> reasons;
  final List<String> warnings;
  final String? hazards;
  final String? notes;
  final List<Map<String, dynamic>> whatsappGroups;
  final double latitude;
  final double longitude;
  final String sewageStatus; // 'discharging', 'clear', 'offline', 'unknown'
  final int? nearestOverflowM;
  final double? waveHeightM;
  final int? wavePeriodS;
  final String? waveDirection;
  final double? waterTempC;

  Recommendation({
    required this.beachId,
    required this.beachName,
    required this.score,
    required this.reasons,
    required this.warnings,
    this.hazards,
    this.notes,
    required this.whatsappGroups,
    required this.latitude,
    required this.longitude,
    this.sewageStatus = 'unknown',
    this.nearestOverflowM,
    this.waveHeightM,
    this.wavePeriodS,
    this.waveDirection,
    this.waterTempC,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) {
    return Recommendation(
      beachId: json['beach_id'],
      beachName: json['beach_name'],
      score: json['score'],
      reasons: List<String>.from(json['reasons'] ?? []),
      warnings: List<String>.from(json['warnings'] ?? []),
      hazards: json['hazards'],
      notes: json['notes'],
      whatsappGroups: List<Map<String, dynamic>>.from(json['whatsapp_groups'] ?? []),
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      sewageStatus: json['sewage_status'] ?? 'unknown',
      nearestOverflowM: json['nearest_overflow_m'],
      waveHeightM: (json['wave_height_m'] as num?)?.toDouble(),
      wavePeriodS: json['wave_period_s'] as int?,
      waveDirection: json['wave_direction'] as String?,
      waterTempC: (json['water_temp_c'] as num?)?.toDouble(),
    );
  }

  String get scoreLabel {
    if (score >= 88) return 'Excellent';
    if (score >= 65) return 'Good';
    if (score >= 40) return 'Marginal';
    return 'Poor';
  }

  int get scoreColor {
    if (score >= 88) return 0xFF2E7D32;
    if (score >= 65) return 0xFF558B2F;
    if (score >= 40) return 0xFFF57F17;
    return 0xFFC62828;
  }
}
