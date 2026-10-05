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
    // Tracked links all open in a new tab (target="_blank"), so this page never
    // unloads — a plain cross-origin fetch is correct here. (sendBeacon is NOT:
    // its cross-origin requests can only use CORS-"simple" content types —
    // text/plain, multipart/form-data, application/x-www-form-urlencoded — and
    // silently drop anything else, including application/json, with no error.)
    var payload = JSON.stringify({ page: pageSlug(), url: url, label: label || '' });
    try {
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true,
        mode: 'cors',
      }).catch(function () {});
    } catch (e) { /* no-op — tracking must never break the link */ }
  }

  document.addEventListener('click', function (e) {
    var el = e.target.closest ? e.target.closest('a[data-track="school"]') : null;
    if (!el) return;
    track(el.href, (el.textContent || '').trim());
  }, true);
}());
