// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

class SpotsService {
  static const _key = 'swk_pinned_spots';

  static Set<int> getPinnedIds() {
    final val = html.window.localStorage[_key] ?? '';
    if (val.isEmpty) return {};
    try {
      return val.split(',').map(int.parse).toSet();
    } catch (_) {
      return {};
    }
  }

  static void saveIds(Set<int> ids) {
    if (ids.isEmpty) {
      html.window.localStorage.remove(_key);
    } else {
      html.window.localStorage[_key] = ids.join(',');
    }
  }
}
