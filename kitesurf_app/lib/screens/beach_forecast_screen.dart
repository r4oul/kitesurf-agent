import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/forecast_window.dart';
import '../services/api.dart';

class BeachForecastScreen extends StatefulWidget {
  final int beachId;
  final String beachName;
  final String riderLevel;

  const BeachForecastScreen({
    super.key,
    required this.beachId,
    required this.beachName,
    required this.riderLevel,
  });

  @override
  State<BeachForecastScreen> createState() => _BeachForecastScreenState();
}

class _BeachForecastScreenState extends State<BeachForecastScreen> {
  List<ForecastWindow> _windows = [];
  List<dynamic> _tideExtremes = [];
  String _sewageStatus = 'unknown';
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.getBeachForecast(widget.beachId, widget.riderLevel);
      setState(() {
        _windows = data['windows'];
        _tideExtremes = data['tide_extremes'];
        _sewageStatus = data['sewage_status'] ?? 'unknown';
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  Map<String, List<ForecastWindow>> _groupByDay() {
    final Map<String, List<ForecastWindow>> grouped = {};
    for (final w in _windows) {
      if (w.time.hour < 6 || w.time.hour >= 21) continue;
      final day = DateFormat('EEEE d MMM').format(w.time);
      grouped.putIfAbsent(day, () => []).add(w);
    }
    return grouped;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0077B6),
        foregroundColor: Colors.white,
        title: Text(widget.beachName),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF0077B6)))
          : _error != null
              ? Center(child: Text(_error!))
              : _buildContent(),
    );
  }

  Widget _buildContent() {
    final grouped = _groupByDay();
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (_sewageStatus == 'clear') _buildWaterClearBanner(),
        if (_sewageStatus == 'discharging') _buildSewageBanner(),
        if (_sewageStatus == 'recent_spill') _buildRecentSpillBanner(),
        if (_tideExtremes.isNotEmpty) _buildTideCard(),
        const SizedBox(height: 16),
        ...grouped.entries.map((entry) => _buildDaySection(entry.key, entry.value)),
      ],
    );
  }

  Widget _buildWaterClearBanner() {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1B5E20),
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Row(
        children: [
          Text('🟢', style: TextStyle(fontSize: 18)),
          SizedBox(width: 10),
          Text('Water quality clear', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildSewageBanner() {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFB71C1C),
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Row(
        children: [
          Text('🚫', style: TextStyle(fontSize: 20)),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'Sewage discharge active nearby — check before entering the water',
              style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentSpillBanner() {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFE65100),
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Row(
        children: [
          Text('⚠️', style: TextStyle(fontSize: 20)),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'Recent sewage spill nearby — avoid entering the water for 48hrs',
              style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTideCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Tide Times', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0077B6))),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _tideExtremes.map<Widget>((e) {
                final isHigh = e['type'] == 'High';
                final time = DateTime.parse(e['time']).toLocal();
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    color: isHigh ? const Color(0xFF0D3B6E) : const Color(0xFF8B6914),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Column(
                    children: [
                      Text(isHigh ? '🌊 High' : '🏖️ Low',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white)),
                      const SizedBox(height: 2),
                      Text(DateFormat('EEE HH:mm').format(time),
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white)),
                      Text('${e['height_m']}m',
                          style: const TextStyle(fontSize: 12, color: Color(0xFFCCDDEE))),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDaySection(String day, List<ForecastWindow> windows) {
    // Find best window of the day
    final best = windows.reduce((a, b) => a.score > b.score ? a : b);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            children: [
              Text(day, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF1A202C))),
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Color(best.scoreColor),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text('Best: ${best.scoreLabel}', style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Column(
            children: windows.asMap().entries.map((entry) {
              final i = entry.key;
              final w = entry.value;
              return Container(
                decoration: BoxDecoration(
                  color: w.score == best.score ? Color(w.scoreColor).withOpacity(0.08) : null,
                  border: i < windows.length - 1
                      ? const Border(bottom: BorderSide(color: Color(0xFFE2E8F0)))
                      : null,
                  borderRadius: i == windows.length - 1
                      ? const BorderRadius.vertical(bottom: Radius.circular(12))
                      : null,
                ),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                child: Row(
                  children: [
                    SizedBox(
                      width: 48,
                      child: Text(
                        DateFormat('HH:mm').format(w.time),
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                    ),
                    Text('${w.windSpeedKnots}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                    const Text('kts ', style: TextStyle(fontSize: 12, color: Colors.grey)),
                    Text(w.windDirection, style: const TextStyle(fontSize: 13)),
                    const SizedBox(width: 4),
                    Text('(gust ${w.windGustKnots})', style: const TextStyle(fontSize: 11, color: Colors.grey)),
                    const Spacer(),
                    Text('${w.tideState} ${w.tideDirection}', style: const TextStyle(fontSize: 11, color: Colors.blueGrey)),
                    const SizedBox(width: 8),
                    Container(
                      width: 36,
                      height: 24,
                      decoration: BoxDecoration(
                        color: Color(w.scoreColor),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Center(
                        child: Text('${w.score}', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: 8),
      ],
    );
  }
}
