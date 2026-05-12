import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/recommendation.dart';
import '../screens/beach_forecast_screen.dart';

class RecommendationCard extends StatelessWidget {
  final Recommendation recommendation;
  final String riderLevel;

  const RecommendationCard({super.key, required this.recommendation, this.riderLevel = 'intermediate'});

  @override
  Widget build(BuildContext context) {
    final r = recommendation;
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: GestureDetector(
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => BeachForecastScreen(
                          beachId: r.beachId,
                          beachName: r.beachName,
                          riderLevel: riderLevel,
                        ),
                      ),
                    ),
                    child: Row(
                      children: [
                        Text(r.beachName, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                        const SizedBox(width: 4),
                        const Icon(Icons.chevron_right, size: 18, color: Color(0xFF0077B6)),
                      ],
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Color(r.scoreColor),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(r.scoreLabel, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
                ),
              ],
            ),
            const SizedBox(height: 10),
            if (r.reasons.isNotEmpty) ...[
              ...r.reasons.map((reason) => _row('✅', reason, Colors.green.shade700)),
            ],
            if (r.warnings.isNotEmpty) ...[
              ...r.warnings.map((w) => _row('⚠️', w, Colors.orange.shade800)),
            ],
            if (r.hazards != null && r.hazards!.isNotEmpty) ...[
              const SizedBox(height: 6),
              _row('🚨', r.hazards!, Colors.red.shade700),
            ],
            if (r.notes != null && r.notes!.isNotEmpty) ...[
              const SizedBox(height: 6),
              _row('📝', r.notes!, Colors.grey.shade700),
            ],
            if (r.whatsappGroups.isNotEmpty) ...[
              const SizedBox(height: 10),
              const Divider(),
              const SizedBox(height: 4),
              ...r.whatsappGroups.map((group) => _whatsappButton(group)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _row(String emoji, String text, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 14)),
          const SizedBox(width: 6),
          Expanded(child: Text(text, style: TextStyle(fontSize: 13, color: color))),
        ],
      ),
    );
  }

  Widget _whatsappButton(Map<String, dynamic> group) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: OutlinedButton.icon(
        icon: const Text('💬', style: TextStyle(fontSize: 16)),
        label: Text(group['name'] ?? 'WhatsApp Group', style: const TextStyle(fontSize: 13)),
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFF25D366),
          side: const BorderSide(color: Color(0xFF25D366)),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        onPressed: () async {
          final url = Uri.parse(group['invite_link'] ?? '');
          if (await canLaunchUrl(url)) launchUrl(url);
        },
      ),
    );
  }
}
