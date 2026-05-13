import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/recommendation.dart';
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
  final MapController _mapController = MapController();

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
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: const LatLng(50.65, -1.8),
                    initialZoom: 8.0,
                    minZoom: 6.0,
                    maxZoom: 15.0,
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
                // Zoom controls
                Positioned(
                  right: 16,
                  bottom: _selected != null ? 220 : 16,
                  child: Column(
                    children: [
                      FloatingActionButton.small(
                        heroTag: 'zoom_in',
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFF0077B6),
                        onPressed: () {
                          _mapController.move(
                            _mapController.camera.center,
                            _mapController.camera.zoom + 1,
                          );
                        },
                        child: const Icon(Icons.add),
                      ),
                      const SizedBox(height: 8),
                      FloatingActionButton.small(
                        heroTag: 'zoom_out',
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFF0077B6),
                        onPressed: () {
                          _mapController.move(
                            _mapController.camera.center,
                            _mapController.camera.zoom - 1,
                          );
                        },
                        child: const Icon(Icons.remove),
                      ),
                      const SizedBox(height: 8),
                      FloatingActionButton.small(
                        heroTag: 'zoom_reset',
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFF0077B6),
                        onPressed: () {
                          _mapController.move(const LatLng(50.65, -1.8), 8.0);
                        },
                        child: const Icon(Icons.my_location),
                      ),
                    ],
                  ),
                ),
                if (_selected != null)
                  Positioned(
                    bottom: 16,
                    left: 16,
                    right: 72,
                    child: RecommendationCard(
                      recommendation: _selected!,
                      riderLevel: widget.riderLevel,
                    ),
                  ),
              ],
            ),
    );
  }
}
