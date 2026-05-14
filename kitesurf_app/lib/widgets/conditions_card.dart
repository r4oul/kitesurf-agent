import 'package:flutter/material.dart';
import '../models/recommendation.dart';
import '../theme.dart';

class ConditionsCard extends StatelessWidget {
  final Conditions conditions;

  const ConditionsCard({super.key, required this.conditions});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0A2540), Color(0xFF0D3B6E)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: kAccent.withOpacity(0.3), width: 1),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 3,
                height: 16,
                decoration: BoxDecoration(
                  color: kAccent,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 8),
              const Text('Current Conditions Where You Are',
                  style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: kAccent)),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              _stat('💨', '${conditions.windSpeedKnots}', 'knots'),
              _stat('💥', '${conditions.windGustKnots}', 'gusts'),
              _stat('🧭', conditions.windDirection, 'direction'),
              _stat('🌊', conditions.tideState, conditions.tideDirection),
            ],
          ),
          if (conditions.windModel.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text('Model: ${conditions.windModel}',
                style: const TextStyle(fontSize: 10, color: kTextSecondary)),
          ],
        ],
      ),
    );
  }

  Widget _stat(String emoji, String value, String label) {
    return Expanded(
      child: Column(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 22)),
          const SizedBox(height: 4),
          Text(value,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: kTextPrimary)),
          Text(label, style: const TextStyle(fontSize: 11, color: kTextSecondary)),
        ],
      ),
    );
  }
}
