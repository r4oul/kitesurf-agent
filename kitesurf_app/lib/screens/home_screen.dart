import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../models/recommendation.dart';
import '../services/api.dart';
import '../widgets/conditions_card.dart';
import '../widgets/recommendation_card.dart';

class HomeScreen extends StatefulWidget {
  final String riderLevel;
  const HomeScreen({super.key, required this.riderLevel});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _loading = false;
  bool _showAll = false;
  String? _error;
  Conditions? _conditions;
  List<Recommendation> _recommendations = [];
  String? _lastLoadedLevel;

  @override
  void didUpdateWidget(HomeScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.riderLevel != widget.riderLevel) {
      _load();
    }
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      double? lat, lon;
      try {
        LocationPermission permission = await Geolocator.checkPermission();
        if (permission == LocationPermission.denied) {
          permission = await Geolocator.requestPermission();
        }
        if (permission == LocationPermission.whileInUse || permission == LocationPermission.always) {
          final pos = await Geolocator.getCurrentPosition(
            locationSettings: const LocationSettings(accuracy: LocationAccuracy.low),
          ).timeout(const Duration(seconds: 5));
          lat = pos.latitude;
          lon = pos.longitude;
        }
      } catch (_) {
        // Location unavailable — fall back to central reference
      }
      final data = await ApiService.getRecommendations(widget.riderLevel, lat: lat, lon: lon);
      setState(() {
        _conditions = data['conditions'];
        _recommendations = data['recommendations'];
        _lastLoadedLevel = widget.riderLevel;
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return _loading
        ? const Center(child: CircularProgressIndicator(color: Color(0xFF0077B6)))
        : _error != null
            ? _buildError()
            : _buildContent();
  }

  Widget _buildError() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.cloud_off, size: 48, color: Colors.grey),
          const SizedBox(height: 12),
          const Text('Could not load conditions', style: TextStyle(fontSize: 16, color: Colors.grey)),
          const SizedBox(height: 8),
          const Text('Make sure the API server is running', style: TextStyle(fontSize: 13, color: Colors.grey)),
          const SizedBox(height: 16),
          ElevatedButton(onPressed: _load, child: const Text('Retry')),
        ],
      ),
    );
  }

  Widget _buildContent() {
    final displayed = _showAll ? _recommendations : _recommendations.take(5).toList();
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (_conditions != null) ConditionsCard(conditions: _conditions!),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Recommendations', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1A202C))),
              TextButton.icon(
                icon: Icon(_showAll ? Icons.expand_less : Icons.expand_more, size: 18),
                label: Text(_showAll ? 'Top 5 only' : 'Show all beaches', style: const TextStyle(fontSize: 13)),
                onPressed: () => setState(() => _showAll = !_showAll),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...displayed.map((r) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: RecommendationCard(recommendation: r, riderLevel: widget.riderLevel),
          )),
        ],
      ),
    );
  }
}
