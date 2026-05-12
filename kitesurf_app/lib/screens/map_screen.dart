import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/recommendation.dart';
import '../models/beach.dart';
import '../services/api.dart';
import '../widgets/recommendation_card.dart';

class MapScreen extends StatefulWidget {
  final String riderLevel;
  const MapScreen({super.key, required this.riderLevel});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  List<Recommendation> _recommendations = [];
  bool _loading = true;
  Recommendation? _selected;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.getRecommendations(widget.riderLevel);
      setState(() {
        _recommendations = data['recommendations'];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  Color _scoreColor(int score) {
    if (score >= 80) return const Color(0xFF2E7D32);
    if (score >= 60) return const Color(0xFF558B2F);
    if (score >= 40) return const Color(0xFFF57F17);
    return const Color(0xFFC62828);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF0077B6)))
          : Stack(
              children: [
                FlutterMap(
                  options: MapOptions(
                    initialCenter: const LatLng(50.65, -1.8),
                    initialZoom: 8.0,
                    onTap: (_, __) => setState(() => _selected = null),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                      userAgentPackageName: 'com.kitesurf.app',
                    ),
                    MarkerLayer(
                      markers: _recommendations.map((r) {
                        return Marker(
                          point: LatLng(r.latitude, r.longitude),
                          width: 44,
                          height: 44,
                          child: GestureDetector(
                            onTap: () => setState(() => _selected = r),
                            child: Container(
                              decoration: BoxDecoration(
                                color: _scoreColor(r.score),
                                shape: BoxShape.circle,
                                border: Border.all(color: Colors.white, width: 2),
                                boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 4)],
                              ),
                              child: Center(
                                child: Text(
                                  '${r.score}',
                                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                                ),
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
                if (_selected != null)
                  Positioned(
                    bottom: 16,
                    left: 16,
                    right: 16,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        RecommendationCard(recommendation: _selected!),
                      ],
                    ),
                  ),
              ],
            ),
    );
  }
}
