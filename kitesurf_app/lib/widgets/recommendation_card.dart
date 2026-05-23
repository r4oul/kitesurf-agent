import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/recommendation.dart';
import '../screens/beach_forecast_screen.dart';
import '../theme.dart';

class RecommendationCard extends StatelessWidget {
  final Recommendation recommendation;
  final String riderLevel;
  final bool isPinned;
  final VoidCallback? onTogglePin;

  const RecommendationCard({
    super.key,
    required this.recommendation,
    this.riderLevel = 'intermediate',
    this.isPinned = false,
    this.onTogglePin,
  });

  @override
  Widget build(BuildContext context) {
    final r = recommendation;
    return Container(
      decoration: BoxDecoration(
        color: kCardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isPinned ? kAccent.withOpacity(0.6) : const Color(0xFF1E3A50),
          width: isPinned ? 1.5 : 1,
        ),
      ),
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
                      Text(r.beachName,
                          style: const TextStyle(
                              fontSize: 17, fontWeight: FontWeight.bold, color: kTextPrimary)),
                      const SizedBox(width: 4),
                      const Icon(Icons.chevron_right, size: 18, color: kAccent),
                    ],
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Color(r.scoreColor).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Color(r.scoreColor), width: 1),
                ),
                child: Text(r.scoreLabel,
                    style: TextStyle(
                        color: Color(r.scoreColor),
                        fontWeight: FontWeight.bold,
                        fontSize: 13)),
              ),
              IconButton(
                onPressed: onTogglePin,
                icon: Icon(
                  isPinned ? Icons.bookmark : Icons.bookmark_border,
                  color: isPinned ? kAccent : kTextSecondary,
                  size: 22,
                ),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
                tooltip: isPinned ? 'Remove from My Spots' : 'Add to My Spots',
              ),
            ],
          ),
          const SizedBox(height: 10),
          if (r.waterTempC != null || r.waveHeightM != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Wrap(
                spacing: 8,
                runSpacing: 4,
                children: [
                  if (r.waterTempC != null)
                    _marinechip('🌡️', '${r.waterTempC!.toStringAsFixed(1)}°C'),
                  if (r.waveHeightM != null) ...[
                    _marinechip('🌊', [
                      '${r.waveHeightM!.toStringAsFixed(1)}m',
                      if (r.wavePeriodS != null) '${r.wavePeriodS}s',
                      if (r.waveDirection != null) r.waveDirection!,
                    ].join(' · ')),
                  ],
                ],
              ),
            ),
          if (r.sewageStatus == 'clear')
            _row('🟢', 'Water quality clear', const Color(0xFF4CAF50)),
          if (r.sewageStatus == 'discharging')
            _row('🚫', 'Sewage discharge active nearby', const Color(0xFFEF5350)),
          if (r.sewageStatus == 'recent_spill')
            _row('⚠️', 'Recent sewage spill — avoid water for 48hrs', const Color(0xFFFF9800)),
          if (r.sewageStatus == 'offline')
            _row('📡', 'Sewage monitor offline', const Color(0xFF9E9E9E)),
          if (r.reasons.isNotEmpty)
            ...r.reasons.map((reason) => _row('✅', reason, const Color(0xFF4CAF50))),
          if (r.warnings.isNotEmpty)
            ...r.warnings.map((w) => _row('⚠️', w, const Color(0xFFFF9800))),
          if (r.hazards != null && r.hazards!.isNotEmpty) ...[
            const SizedBox(height: 6),
            _row('🚨', r.hazards!, const Color(0xFFEF5350)),
          ],
          if (r.notes != null && r.notes!.isNotEmpty) ...[
            const SizedBox(height: 6),
            _row('📝', r.notes!, kTextSecondary),
          ],
          if (r.whatsappGroups.isNotEmpty) ...[
            const SizedBox(height: 10),
            Divider(color: const Color(0xFF1E3A50)),
            const SizedBox(height: 4),
            ...r.whatsappGroups.map((group) => _whatsappButton(group)),
          ],
        ],
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

  Widget _marinechip(String emoji, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: const Color(0xFF1E3A50),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text('$emoji $text',
          style: const TextStyle(fontSize: 12, color: kTextSecondary)),
    );
  }

  Widget _whatsappButton(Map<String, dynamic> group) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: OutlinedButton.icon(
        icon: const Text('💬', style: TextStyle(fontSize: 16)),
        label: Text(group['name'] ?? 'WhatsApp Group',
            style: const TextStyle(fontSize: 13)),
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
