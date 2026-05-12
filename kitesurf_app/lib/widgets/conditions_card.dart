import 'package:flutter/material.dart';
import '../models/recommendation.dart';

class ConditionsCard extends StatelessWidget {
  final Conditions conditions;

  const ConditionsCard({super.key, required this.conditions});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Current Conditions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0077B6))),
            const SizedBox(height: 12),
            Row(
              children: [
                _stat('💨', '${conditions.windSpeedKnots}', 'knots'),
                _stat('💥', '${conditions.windGustKnots}', 'gusts'),
                _stat('🧭', conditions.windDirection, 'direction'),
                _stat('🌊', conditions.tideState, conditions.tideDirection),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _stat(String emoji, String value, String label) {
    return Expanded(
      child: Column(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 22)),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        ],
      ),
    );
  }
}
