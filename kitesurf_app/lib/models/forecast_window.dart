class ForecastWindow {
  final DateTime time;
  final double windSpeedKnots;
  final double windGustKnots;
  final String windDirection;
  final String tideState;
  final String tideDirection;
  final int score;
  final String scoreLabel;

  ForecastWindow({
    required this.time,
    required this.windSpeedKnots,
    required this.windGustKnots,
    required this.windDirection,
    required this.tideState,
    required this.tideDirection,
    required this.score,
    required this.scoreLabel,
  });

  factory ForecastWindow.fromJson(Map<String, dynamic> json) {
    return ForecastWindow(
      time: DateTime.parse(json['time']).toLocal(),
      windSpeedKnots: (json['wind_speed_knots'] as num).toDouble(),
      windGustKnots: (json['wind_gust_knots'] as num).toDouble(),
      windDirection: json['wind_direction'] ?? '',
      tideState: json['tide_state'] ?? '',
      tideDirection: json['tide_direction'] ?? '',
      score: json['score'] ?? 0,
      scoreLabel: json['score_label'] ?? '',
    );
  }

  int get scoreColor {
    if (score >= 88) return 0xFF2E7D32;
    if (score >= 65) return 0xFF558B2F;
    if (score >= 40) return 0xFFF57F17;
    return 0xFFC62828;
  }
}
