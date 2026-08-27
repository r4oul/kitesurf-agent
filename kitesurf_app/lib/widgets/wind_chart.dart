import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/forecast_window.dart';

/// Hourly wind speed / gust trend for a single day.
class WindChart extends StatelessWidget {
  final List<ForecastWindow> windows;

  const WindChart({super.key, required this.windows});

  static const _speedColor = Color(0xFF0077B6);
  static const _gustColor = Color(0xFFF6A800);
  static const _gridColor = Color(0xFFE2E8F0);
  static const _labelColor = Color(0xFF718096);

  int _labelInterval(int count) {
    if (count <= 6) return 1;
    if (count <= 12) return 2;
    return 3;
  }

  @override
  Widget build(BuildContext context) {
    if (windows.isEmpty) return const SizedBox.shrink();

    final maxGust = windows.map((w) => w.windGustKnots).reduce((a, b) => a > b ? a : b);
    final maxY = ((maxGust / 5).ceil() * 5).toDouble().clamp(10.0, double.infinity);
    final interval = _labelInterval(windows.length);

    final speedSpots = <FlSpot>[
      for (var i = 0; i < windows.length; i++) FlSpot(i.toDouble(), windows[i].windSpeedKnots),
    ];
    final gustSpots = <FlSpot>[
      for (var i = 0; i < windows.length; i++) FlSpot(i.toDouble(), windows[i].windGustKnots),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            _legendDot(_speedColor),
            const SizedBox(width: 4),
            const Text('Speed', style: TextStyle(fontSize: 11, color: _labelColor)),
            const SizedBox(width: 12),
            _legendDot(_gustColor),
            const SizedBox(width: 4),
            const Text('Gust', style: TextStyle(fontSize: 11, color: _labelColor)),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 130,
          child: LineChart(
            LineChartData(
              minY: 0,
              maxY: maxY,
              minX: 0,
              maxX: (windows.length - 1).toDouble(),
              gridData: FlGridData(
                show: true,
                drawVerticalLine: false,
                horizontalInterval: maxY / 4,
                getDrawingHorizontalLine: (_) => const FlLine(color: _gridColor, strokeWidth: 1),
              ),
              borderData: FlBorderData(show: false),
              titlesData: FlTitlesData(
                topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 30,
                    interval: maxY / 4,
                    getTitlesWidget: (value, meta) => Text(
                      '${value.toInt()}',
                      style: const TextStyle(fontSize: 10, color: _labelColor),
                    ),
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 22,
                    interval: interval.toDouble(),
                    getTitlesWidget: (value, meta) {
                      final i = value.round();
                      if (i < 0 || i >= windows.length || i % interval != 0) {
                        return const SizedBox.shrink();
                      }
                      return Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          DateFormat('HH:mm').format(windows[i].time),
                          style: const TextStyle(fontSize: 10, color: _labelColor),
                        ),
                      );
                    },
                  ),
                ),
              ),
              lineTouchData: LineTouchData(
                touchTooltipData: LineTouchTooltipData(
                  getTooltipItems: (spots) => spots.map((s) {
                    final w = windows[s.x.toInt()];
                    final isGust = s.barIndex == 0;
                    return LineTooltipItem(
                      isGust
                          ? 'Gust ${w.windGustKnots.toStringAsFixed(0)}kt'
                          : '${w.windSpeedKnots.toStringAsFixed(0)}kt · ${w.windDirection}',
                      TextStyle(
                        color: isGust ? _gustColor : _speedColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    );
                  }).toList(),
                ),
              ),
              lineBarsData: [
                // Gust line drawn first so the speed line sits on top of it.
                LineChartBarData(
                  spots: gustSpots,
                  isCurved: true,
                  curveSmoothness: 0.2,
                  color: _gustColor,
                  barWidth: 1.5,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(show: false),
                ),
                LineChartBarData(
                  spots: speedSpots,
                  isCurved: true,
                  curveSmoothness: 0.2,
                  color: _speedColor,
                  barWidth: 2.5,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(show: true, color: Color(0x1A0077B6)),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _legendDot(Color color) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
    );
  }
}
