/* Tracks clicks on outbound kite-school links so the admin report can show
   how many visitors each guide page sent to each school's site. */
(function () {
  'use strict';

  var ENDPOINT = 'https://web-production-7cfa1.up.railway.app/api/track/click';

  function pageSlug() {
    var path = location.pathname.replace(/\/+$/, '');
    var parts = path.split('/');
    return parts[parts.length - 1] || 'index';
  }

  function track(url, label) {
    var payload = JSON.stringify({ page: pageSlug(), url: url, label: label || '' });
    try {
      if (navigator.sendBeacon) {
        var blob = new Blob([payload], { type: 'application/json' });
        navigator.sendBeacon(ENDPOINT, blob);
        return;
      }
    } catch (e) { /* fall through to fetch */ }
    try {
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true,
      }).catch(function () {});
    } catch (e) { /* no-op — tracking must never break the link */ }
  }

  document.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('a[data-track="school"]') : null;
    if (!el) return;
    track(el.href, (el.textContent || '').trim());
  }, true);
}());
