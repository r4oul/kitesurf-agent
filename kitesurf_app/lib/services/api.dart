import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/beach.dart';
import '../models/recommendation.dart';
import '../models/forecast_window.dart';

const String baseUrl = 'https://web-production-7cfa1.up.railway.app';

class ApiService {
  static Future<List<Beach>> getBeaches() async {
    final response = await http.get(Uri.parse('$baseUrl/beaches/'));
    if (response.statusCode == 200) {
      final List data = jsonDecode(response.body);
      return data.map((j) => Beach.fromJson(j)).toList();
    }
    throw Exception('Failed to load beaches');
  }

  static Future<Map<String, dynamic>> getBeachForecast(int beachId, String riderLevel) async {
    final response = await http.get(
      Uri.parse('$baseUrl/forecast/beach/$beachId?rider_level=$riderLevel'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'beach_name': data['beach_name'],
        'windows': (data['windows'] as List)
            .map((w) => ForecastWindow.fromJson(w))
            .toList(),
        'tide_extremes': data['tide_extremes'] as List,
        'sewage_status': data['sewage_status'] ?? 'unknown',
        'nearest_overflow_m': data['nearest_overflow_m'],
      };
    }
    throw Exception('Failed to load beach forecast');
  }

  static Future<Map<String, dynamic>> getRecommendations(String riderLevel, {double? lat, double? lon}) async {
    var url = '$baseUrl/forecast/recommend?rider_level=$riderLevel';
    if (lat != null && lon != null) url += '&lat=$lat&lon=$lon';
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'conditions': Conditions.fromJson(data['conditions']),
        'recommendations': (data['recommendations'] as List)
            .map((r) => Recommendation.fromJson(r))
            .toList(),
      };
    }
    throw Exception('Failed to load recommendations');
  }
}
