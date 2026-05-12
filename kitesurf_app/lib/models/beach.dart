class WhatsAppGroup {
  final String name;
  final String inviteLink;

  WhatsAppGroup({required this.name, required this.inviteLink});

  factory WhatsAppGroup.fromJson(Map<String, dynamic> json) {
    return WhatsAppGroup(
      name: json['name'] ?? '',
      inviteLink: json['invite_link'] ?? '',
    );
  }
}

class Beach {
  final int id;
  final String name;
  final double latitude;
  final double longitude;
  final List<String> windDirections;
  final int windSpeedMin;
  final int windSpeedMax;
  final List<String> tideStates;
  final List<String> tideDirections;
  final List<String> riderLevels;
  final String? hazards;
  final String? notes;
  final List<WhatsAppGroup> whatsappGroups;

  Beach({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.windDirections,
    required this.windSpeedMin,
    required this.windSpeedMax,
    required this.tideStates,
    required this.tideDirections,
    required this.riderLevels,
    this.hazards,
    this.notes,
    required this.whatsappGroups,
  });

  factory Beach.fromJson(Map<String, dynamic> json) {
    return Beach(
      id: json['id'],
      name: json['name'],
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      windDirections: List<String>.from(json['wind_directions'] ?? []),
      windSpeedMin: json['wind_speed_min'] ?? 0,
      windSpeedMax: json['wind_speed_max'] ?? 0,
      tideStates: List<String>.from(json['tide_states'] ?? []),
      tideDirections: List<String>.from(json['tide_directions'] ?? []),
      riderLevels: List<String>.from(json['rider_levels'] ?? []),
      hazards: json['hazards'],
      notes: json['notes'],
      whatsappGroups: (json['whatsapp_groups'] as List? ?? [])
          .map((g) => WhatsAppGroup.fromJson(g))
          .toList(),
    );
  }
}
