// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

class SpotsService {
  static const _key = 'swk_pinned_spots';

  // Safari's ITP clears localStorage for sites not visited in 7 days.
  // First-party cookies survive much longer, so we write to both and
  // read from whichever has data.
  static Set<int> getPinnedIds() {
    final fromCookie = _readCookie();
    if (fromCookie.isNotEmpty) return fromCookie;
    final fromStorage = _readLocalStorage();
    if (fromStorage.isNotEmpty) {
      // Migrate to cookie on first read
      _writeCookie(fromStorage);
    }
    return fromStorage;
  }

  static void saveIds(Set<int> ids) {
    _writeCookie(ids);
    _writeLocalStorage(ids);
  }

  static Set<int> _readLocalStorage() {
    final val = html.window.localStorage[_key] ?? '';
    if (val.isEmpty) return {};
    try {
      return val.split(',').map(int.parse).toSet();
    } catch (_) {
      return {};
    }
  }

  static void _writeLocalStorage(Set<int> ids) {
    if (ids.isEmpty) {
      html.window.localStorage.remove(_key);
    } else {
      html.window.localStorage[_key] = ids.join(',');
    }
  }

  static Set<int> _readCookie() {
    final cookies = html.document.cookie ?? '';
    for (final part in cookies.split(';')) {
      final kv = part.trim().split('=');
      if (kv.length == 2 && kv[0].trim() == _key) {
        final val = Uri.decodeComponent(kv[1].trim());
        if (val.isEmpty) return {};
        try {
          return val.split(',').map(int.parse).toSet();
        } catch (_) {
          return {};
        }
      }
    }
    return {};
  }

  static void _writeCookie(Set<int> ids) {
    final value = ids.isEmpty ? '' : ids.join(',');
    // 365-day expiry; SameSite=Lax is sufficient for a first-party web app
    final expires = DateTime.now().add(const Duration(days: 365));
    final expiresStr = _httpDate(expires);
    html.document.cookie =
        '$_key=${Uri.encodeComponent(value)}; expires=$expiresStr; path=/; SameSite=Lax';
  }

  static String _httpDate(DateTime dt) {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    final utc = dt.toUtc();
    final day = days[utc.weekday - 1];
    final month = months[utc.month - 1];
    return '$day, ${utc.day.toString().padLeft(2, '0')} $month ${utc.year} '
        '${utc.hour.toString().padLeft(2, '0')}:${utc.minute.toString().padLeft(2, '0')}:${utc.second.toString().padLeft(2, '0')} GMT';
  }
}
