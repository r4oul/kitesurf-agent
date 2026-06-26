import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
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
  double? _waveHeightM;
  int? _wavePeriodS;
  String? _waveDirection;
  double? _waterTempC;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  // Flutter web's toLocal() doesn't always apply DST correctly.
  // Adding the offset explicitly is reliable in both native and web.
  static DateTime _utcToLocal(String iso) {
    final utc = DateTime.parse(iso).toUtc();
    return utc.add(DateTime.now().timeZoneOffset);
  }

  Future<void> _load() async {
    try {
      final data = await ApiService.getBeachForecast(widget.beachId, widget.riderLevel);
      setState(() {
        _windows = data['windows'];
        _tideExtremes = data['tide_extremes'];
        _sewageStatus = data['sewage_status'] ?? 'unknown';
        _waveHeightM = (data['wave_height_m'] as num?)?.toDouble();
        _wavePeriodS = data['wave_period_s'] as int?;
        _waveDirection = data['wave_direction'] as String?;
        _waterTempC = (data['water_temp_c'] as num?)?.toDouble();
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
        if (_waveHeightM != null || _waterTempC != null) _buildMarineCard(),
        if (_tideExtremes.isNotEmpty) _buildTideCard(),
        const SizedBox(height: 16),
        ...grouped.entries.map((entry) => _buildDaySection(entry.key, entry.value)),
      ],
    );
  }

  Widget _buildMarineCard() {
    final parts = <Widget>[];
    if (_waveHeightM != null) {
      var label = '${_waveHeightM!.toStringAsFixed(1)}m';
      if (_wavePeriodS != null) label += ' · ${_wavePeriodS}s';
      if (_waveDirection != null) label += ' · $_waveDirection';
      parts.add(_marineChip('🌊', label));
    }
    if (_waterTempC != null) {
      parts.add(_marineChip('🌡️', '${_waterTempC!.toStringAsFixed(1)}°C'));
    }
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF132236),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFF1E3A50)),
      ),
      child: Row(
        children: [
          const Text('Current conditions', style: TextStyle(fontSize: 13, color: Color(0xFF00D4FF), fontWeight: FontWeight.w600)),
          const SizedBox(width: 12),
          ...parts,
        ],
      ),
    );
  }

  Widget _marineChip(String emoji, String text) {
    return Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: const Color(0xFF1E3A50),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text('$emoji $text', style: const TextStyle(fontSize: 12, color: Color(0xFFB0BEC5))),
    );
  }

  Future<void> _openSas() async {
    final uri = Uri.parse('https://www.sas.org.uk/safer-seas-service/');
    if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
  }

  Widget _sasLink(Color textColor) {
    return GestureDetector(
      onTap: _openSas,
      child: Text(
        'Also check SAS ↗',
        style: TextStyle(color: textColor, fontSize: 11, decoration: TextDecoration.underline, decorationColor: textColor),
      ),
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
      child: Row(
        children: [
          const Text('🟢', style: TextStyle(fontSize: 18)),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Water quality clear', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
              const SizedBox(height: 2),
              _sasLink(const Color(0xFFB8FFB8)),
            ],
          ),
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
      child: Row(
        children: [
          const Text('🚫', style: TextStyle(fontSize: 20)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Sewage discharge active nearby — check before entering the water',
                  style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                _sasLink(const Color(0xFFFFCDD2)),
              ],
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
      child: Row(
        children: [
          const Text('⚠️', style: TextStyle(fontSize: 20)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Recent sewage spill nearby — avoid entering the water for 48hrs',
                  style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                _sasLink(const Color(0xFFFFE0B2)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTideCard() {
    final now = DateTime.now();

    String stateText = '';
    final past = _tideExtremes
        .where((e) => _utcToLocal(e['time']).isBefore(now))
        .toList();
    if (past.isNotEmpty) {
      final last = past.last;
      final lastTime = _utcToLocal(last['time']);
      final mins = now.difference(lastTime).inMinutes;
      final isHigh = last['type'] == 'High';
      final arrow = isHigh ? '▲' : '▼';
      final label = isHigh ? 'High' : 'Low';
      if (mins < 5) {
        stateText = '≈ $arrow $label Tide now';
      } else if (mins < 90) {
        stateText = '≈ $arrow $label Tide $mins mins ago';
      } else {
        stateText = '≈ $arrow $label Tide ${(mins / 60).round()}h ago';
      }
    }

    final tomorrow = now.add(const Duration(days: 1));
    final todayTides = _tideExtremes.where((e) {
      final d = _utcToLocal(e['time']);
      return d.year == now.year && d.month == now.month && d.day == now.day;
    }).toList();
    final tomorrowTides = _tideExtremes.where((e) {
      final d = _utcToLocal(e['time']);
      return d.year == tomorrow.year && d.month == tomorrow.month && d.day == tomorrow.day;
    }).toList();

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Tide Times',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0077B6))),
            if (stateText.isNotEmpty) ...[
              const SizedBox(height: 6),
              Text(stateText,
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF00D4FF))),
            ],
            const SizedBox(height: 10),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: SizedBox(
                height: 110,
                width: double.infinity,
                child: CustomPaint(painter: _TidePainter(_tideExtremes, now)),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (todayTides.isNotEmpty)
                  Expanded(child: _buildTideTable('Today\'s Tides', todayTides)),
                if (tomorrowTides.isNotEmpty)
                  Expanded(child: _buildTideTable('Tomorrow\'s Tides', tomorrowTides)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTideTable(String title, List<dynamic> tides) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title.toUpperCase(),
            style: const TextStyle(
                fontSize: 10, fontWeight: FontWeight.w700,
                color: Color(0xFFB0BEC5), letterSpacing: 0.7)),
        const SizedBox(height: 6),
        ...tides.map((e) {
          final isHigh = e['type'] == 'High';
          final time = _utcToLocal(e['time']);
          return Padding(
            padding: const EdgeInsets.only(bottom: 5),
            child: Row(
              children: [
                SizedBox(
                  width: 46,
                  child: Text(DateFormat('HH:mm').format(time),
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.white)),
                ),
                SizedBox(
                  width: 46,
                  child: Text('${(e['height_m'] as num).toStringAsFixed(2)}m',
                      style: const TextStyle(fontSize: 12, color: Color(0xFFB0BEC5))),
                ),
                Text(isHigh ? '▲ High' : '▼ Low',
                    style: TextStyle(
                        fontSize: 12, fontWeight: FontWeight.w600,
                        color: isHigh ? const Color(0xFF00D4FF) : const Color(0xFFF6A800))),
              ],
            ),
          );
        }),
      ],
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

class _TidePainter extends CustomPainter {
  final List<dynamic> extremes;
  final DateTime now;

  const _TidePainter(this.extremes, this.now);

  double _cosInterp(double t, double t1, double h1, double t2, double h2) {
    return (h1 + h2) / 2 + (h1 - h2) / 2 * cos(pi * (t - t1) / (t2 - t1));
  }

  double? _tideAt(double ms) {
    for (int i = 0; i < extremes.length - 1; i++) {
      final t1 = DateTime.parse(extremes[i]['time']).millisecondsSinceEpoch.toDouble();
      final t2 = DateTime.parse(extremes[i + 1]['time']).millisecondsSinceEpoch.toDouble();
      if (ms >= t1 && ms <= t2) {
        return _cosInterp(ms, t1, (extremes[i]['height_m'] as num).toDouble(),
            t2, (extremes[i + 1]['height_m'] as num).toDouble());
      }
    }
    return null;
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Background
    canvas.drawRRect(
      RRect.fromRectAndRadius(Offset.zero & size, const Radius.circular(8)),
      Paint()..color = const Color(0xFF0A1520),
    );

    final localMidnight = DateTime(now.year, now.month, now.day);
    final t0 = localMidnight.millisecondsSinceEpoch.toDouble();
    final t1 = t0 + 48 * 3600000;
    final tNow = now.millisecondsSinceEpoch.toDouble();
    const labelH = 20.0;
    final plotH = size.height - labelH;

    final heights = extremes.map((e) => (e['height_m'] as num).toDouble()).toList();
    var minH = heights.reduce(min);
    var maxH = heights.reduce(max);
    final pad = (maxH - minH) * 0.12;
    minH -= pad;
    maxH += pad;

    double xOf(double ms) => size.width * (ms - t0) / (t1 - t0);
    double yOf(double h) => plotH * (1 - (h - minH) / (maxH - minH));

    // Build curve points
    final pts = <Offset>[];
    for (int i = 0; i <= 300; i++) {
      final ms = t0 + (t1 - t0) * i / 300;
      final h = _tideAt(ms);
      if (h != null) pts.add(Offset(xOf(ms), yOf(h)));
    }
    if (pts.isEmpty) return;

    // Fill
    final fillPath = Path()..moveTo(xOf(t0), plotH);
    for (final pt in pts) fillPath.lineTo(pt.dx, pt.dy);
    fillPath.lineTo(xOf(t1), plotH);
    fillPath.close();
    canvas.drawPath(fillPath,
        Paint()..color = const Color(0xFF00D4FF).withOpacity(0.08)..style = PaintingStyle.fill);

    // Curve
    final linePath = Path()..moveTo(pts.first.dx, pts.first.dy);
    for (int i = 1; i < pts.length; i++) linePath.lineTo(pts[i].dx, pts[i].dy);
    canvas.drawPath(linePath,
        Paint()..color = const Color(0xFF00D4FF)..strokeWidth = 1.8..style = PaintingStyle.stroke..strokeCap = StrokeCap.round);

    // Day divider
    final divX = xOf(t0 + 24 * 3600000);
    canvas.drawLine(Offset(divX, 0), Offset(divX, plotH),
        Paint()..color = const Color(0xFF1E3A50)..strokeWidth = 1);

    // Current time marker (dashed)
    if (tNow >= t0 && tNow <= t1) {
      final nowX = xOf(tNow);
      final dashPaint = Paint()..color = Colors.white.withOpacity(0.45)..strokeWidth = 1.5;
      var y = 0.0;
      while (y < plotH) {
        canvas.drawLine(Offset(nowX, y), Offset(nowX, min(y + 4, plotH)), dashPaint);
        y += 7;
      }
    }

    // Today / Tomorrow labels
    void drawLabel(String text, double cx) {
      final tp = TextPainter(
        text: TextSpan(
            text: text,
            style: const TextStyle(color: Color(0xFFB0BEC5), fontSize: 10, fontFamily: 'sans-serif')),
        textDirection: ui.TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(cx - tp.width / 2, plotH + (labelH - tp.height) / 2));
    }
    drawLabel('Today', xOf(t0 + 12 * 3600000));
    drawLabel('Tomorrow', xOf(t0 + 36 * 3600000));

    // Extreme dots
    for (final e in extremes) {
      final ems = DateTime.parse(e['time']).millisecondsSinceEpoch.toDouble();
      final ex = xOf(ems);
      if (ex < 0 || ex > size.width) continue;
      canvas.drawCircle(
        Offset(ex, yOf((e['height_m'] as num).toDouble())),
        4,
        Paint()..color = e['type'] == 'High' ? const Color(0xFF00D4FF) : const Color(0xFFF6A800),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _TidePainter old) =>
      old.extremes != extremes || old.now != now;
}
