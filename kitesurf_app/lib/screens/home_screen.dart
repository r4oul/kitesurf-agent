import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/recommendation.dart';
import '../services/api.dart';
import '../services/spots_service.dart';
import '../widgets/conditions_card.dart';
import '../widgets/recommendation_card.dart';
import '../theme.dart';

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
  Set<int> _pinnedIds = {};

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
    _loadPins();
    _load(); // ignore: unawaited_futures
  }

  void _loadPins() {
    setState(() => _pinnedIds = SpotsService.getPinnedIds());
  }

  void _togglePin(int beachId) {
    setState(() {
      if (_pinnedIds.contains(beachId)) {
        _pinnedIds = {..._pinnedIds}..remove(beachId);
      } else {
        _pinnedIds = {..._pinnedIds, beachId};
      }
    });
    SpotsService.saveIds(_pinnedIds);
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
    final pinned = _recommendations.where((r) => _pinnedIds.contains(r.beachId)).toList();
    final others = _recommendations.where((r) => !_pinnedIds.contains(r.beachId)).toList();
    final displayedOthers = _showAll ? others : others.take(5).toList();

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (_conditions != null) ConditionsCard(conditions: _conditions!),
          const SizedBox(height: 12),
          _GuideBanner(),
          const SizedBox(height: 16),

          if (pinned.isNotEmpty) ...[
            Row(
              children: const [
                Icon(Icons.bookmark, color: kAccent, size: 18),
                SizedBox(width: 6),
                Text('My Spots', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: kTextPrimary)),
              ],
            ),
            const SizedBox(height: 8),
            ...pinned.map((r) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: RecommendationCard(
                recommendation: r,
                riderLevel: widget.riderLevel,
                isPinned: true,
                onTogglePin: () => _togglePin(r.beachId),
              ),
            )),
            const Divider(color: Color(0xFF1E3A50), height: 24),
          ],

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('All Beaches', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: kTextPrimary)),
              TextButton.icon(
                icon: Icon(_showAll ? Icons.expand_less : Icons.expand_more, size: 18),
                label: Text(_showAll ? 'Top 5 only' : 'Show all', style: const TextStyle(fontSize: 13)),
                onPressed: () => setState(() => _showAll = !_showAll),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...displayedOthers.map((r) => Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: RecommendationCard(
              recommendation: r,
              riderLevel: widget.riderLevel,
              isPinned: false,
              onTogglePin: () => _togglePin(r.beachId),
            ),
          )),
        ],
      ),
    );
  }
}

class _GuideBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => launchUrl(
        Uri.parse('https://southwestkitesurf.co.uk/guide/'),
        mode: LaunchMode.externalApplication,
      ),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF0A2540), Color(0xFF0D3B6E)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: kAccent.withOpacity(0.3), width: 1),
        ),
        child: Row(
          children: [
            const Icon(Icons.menu_book_rounded, color: kAccent, size: 22),
            const SizedBox(width: 12),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Beach Guides',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: kTextPrimary)),
                  SizedBox(height: 2),
                  Text('Spot guides, gear tips & local knowledge',
                      style: TextStyle(fontSize: 12, color: kTextSecondary)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, size: 20, color: kAccent),
          ],
        ),
      ),
    );
  }
}
