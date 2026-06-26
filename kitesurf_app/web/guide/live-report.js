/* Live Kitesurfing Report — wind forecast, tide curve & table, wave conditions */
(function () {
  'use strict';

  var API = 'https://web-production-7cfa1.up.railway.app';
  var DIRS = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];

  function degToCompass(d) { return DIRS[Math.round(d / 22.5) % 16]; }

  function fmtLocal(iso) {
    return new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
  }

  function fmtCoord(lat, lon) {
    return (Math.abs(lat).toFixed(3) + '°' + (lat >= 0 ? 'N' : 'S'))
      + ', ' + (Math.abs(lon).toFixed(3) + '°' + (lon >= 0 ? 'E' : 'W'));
  }

  function isLocalDay(iso, dayOffset) {
    var d = new Date(iso);
    var ref = new Date();
    ref.setDate(ref.getDate() + dayOffset);
    return d.getFullYear() === ref.getFullYear()
      && d.getMonth() === ref.getMonth()
      && d.getDate() === ref.getDate();
  }

  function cosInterp(t, t1, h1, t2, h2) {
    return (h1 + h2) / 2 + (h1 - h2) / 2 * Math.cos(Math.PI * (t - t1) / (t2 - t1));
  }

  function tideAt(ms, exts) {
    for (var i = 0; i < exts.length - 1; i++) {
      var t1 = new Date(exts[i].time).getTime();
      var t2 = new Date(exts[i + 1].time).getTime();
      if (ms >= t1 && ms <= t2) return cosInterp(ms, t1, exts[i].height_m, t2, exts[i + 1].height_m);
    }
    return null;
  }

  function tideStateText(exts) {
    var now = Date.now();
    var past = exts.filter(function (e) { return new Date(e.time).getTime() <= now; });
    if (!past.length) return '';
    var last = past[past.length - 1];
    var mins = Math.round((now - new Date(last.time).getTime()) / 60000);
    var arrow = last.type === 'High' ? '▲' : '▼';
    var label = last.type === 'High' ? 'High' : 'Low';
    if (mins < 5) return '≈ ' + arrow + ' ' + label + ' Tide now';
    if (mins < 90) return '≈ ' + arrow + ' ' + label + ' Tide ' + mins + ' mins ago';
    return '≈ ' + arrow + ' ' + label + ' Tide ' + Math.round(mins / 60) + 'h ago';
  }

  function compassSVG(deg) {
    return '<svg viewBox="-1 -1 2 2" width="88" height="88" xmlns="http://www.w3.org/2000/svg">'
      + '<circle cx="0" cy="0" r="0.92" fill="none" stroke="#1E3A50" stroke-width="0.06"/>'
      + '<line x1="0" y1="-0.92" x2="0" y2="-0.78" stroke="#1E3A50" stroke-width="0.03"/>'
      + '<line x1="0.92" y1="0" x2="0.78" y2="0" stroke="#1E3A50" stroke-width="0.03"/>'
      + '<line x1="0" y1="0.92" x2="0" y2="0.78" stroke="#1E3A50" stroke-width="0.03"/>'
      + '<line x1="-0.92" y1="0" x2="-0.78" y2="0" stroke="#1E3A50" stroke-width="0.03"/>'
      + '<text x="0" y="-0.6" text-anchor="middle" font-size="0.22" font-family="sans-serif" fill="#B0BEC5">N</text>'
      + '<text x="0.65" y="0.08" text-anchor="start" font-size="0.22" font-family="sans-serif" fill="#B0BEC5">E</text>'
      + '<text x="0" y="0.8" text-anchor="middle" font-size="0.22" font-family="sans-serif" fill="#B0BEC5">S</text>'
      + '<text x="-0.65" y="0.08" text-anchor="end" font-size="0.22" font-family="sans-serif" fill="#B0BEC5">W</text>'
      + '<g transform="rotate(' + deg + ')">'
      + '<polygon points="0,-0.6 0.08,0.05 -0.08,0.05" fill="#00D4FF"/>'
      + '<polygon points="0,0.6 0.08,-0.05 -0.08,-0.05" fill="#1A3A50"/>'
      + '<circle cx="0" cy="0" r="0.065" fill="#00D4FF"/>'
      + '</g>'
      + '</svg>';
  }

  function tideSVG(exts) {
    var W = 600, H = 100;
    var pL = 6, pR = 6, pT = 12, pB = 22;
    var plotW = W - pL - pR, plotH = H - pT - pB;

    var localMidnight = new Date();
    localMidnight.setHours(0, 0, 0, 0);
    var t0 = localMidnight.getTime();
    var t1 = t0 + 48 * 3600000;
    var now = Date.now();

    var heights = exts.map(function (e) { return e.height_m; });
    var minH = Math.min.apply(null, heights);
    var maxH = Math.max.apply(null, heights);
    var pad = (maxH - minH) * 0.12;
    minH -= pad; maxH += pad;

    function xOf(ms) { return pL + plotW * (ms - t0) / (t1 - t0); }
    function yOf(h) { return pT + plotH * (1 - (h - minH) / (maxH - minH)); }

    var pts = [];
    for (var i = 0; i <= 300; i++) {
      var t = t0 + (t1 - t0) * i / 300;
      var h = tideAt(t, exts);
      if (h !== null) pts.push(xOf(t).toFixed(1) + ',' + yOf(h).toFixed(1));
    }

    if (!pts.length) return '';

    var line = 'M ' + pts.join(' L ');
    var area = 'M ' + xOf(t0).toFixed(1) + ',' + (pT + plotH)
      + ' L ' + pts.join(' L ')
      + ' L ' + xOf(t1).toFixed(1) + ',' + (pT + plotH) + ' Z';

    var divX = xOf(t0 + 24 * 3600000).toFixed(1);
    var nowX = xOf(now).toFixed(1);

    var svg = '<svg class="lr-tide-svg" viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg">';
    svg += '<rect width="' + W + '" height="' + H + '" fill="#0A1520" rx="6"/>';
    svg += '<path d="' + area + '" fill="rgba(0,212,255,0.08)"/>';
    svg += '<path d="' + line + '" fill="none" stroke="#00D4FF" stroke-width="1.8"/>';
    svg += '<line x1="' + divX + '" y1="' + pT + '" x2="' + divX + '" y2="' + (pT + plotH) + '" stroke="#1E3A50" stroke-width="1"/>';
    if (now >= t0 && now <= t1) {
      svg += '<line x1="' + nowX + '" y1="' + pT + '" x2="' + nowX + '" y2="' + (pT + plotH) + '" stroke="rgba(255,255,255,0.45)" stroke-width="1.5" stroke-dasharray="3,2"/>';
    }
    svg += '<text x="' + xOf(t0 + 12 * 3600000).toFixed(1) + '" y="' + (H - 5) + '" text-anchor="middle" fill="#B0BEC5" font-size="10" font-family="sans-serif">Today</text>';
    svg += '<text x="' + xOf(t0 + 36 * 3600000).toFixed(1) + '" y="' + (H - 5) + '" text-anchor="middle" fill="#B0BEC5" font-size="10" font-family="sans-serif">Tomorrow</text>';
    exts.forEach(function (e) {
      var ems = new Date(e.time).getTime();
      var ex = xOf(ems), ey = yOf(e.height_m);
      if (ex >= pL && ex <= W - pR) {
        svg += '<circle cx="' + ex.toFixed(1) + '" cy="' + ey.toFixed(1) + '" r="3" fill="' + (e.type === 'High' ? '#00D4FF' : '#F6A800') + '"/>';
      }
    });
    svg += '</svg>';
    return svg;
  }

  function tideTableHTML(exts, dayOffset) {
    var rows = exts.filter(function (e) { return isLocalDay(e.time, dayOffset); });
    if (!rows.length) return '';
    var html = '<table class="lr-tide-table"><tbody>';
    rows.forEach(function (e) {
      var isH = e.type === 'High';
      html += '<tr><td>' + fmtLocal(e.time) + '</td>'
        + '<td>' + e.height_m.toFixed(2) + 'm</td>'
        + '<td class="' + (isH ? 'lrh' : 'lrl') + '">' + (isH ? '▲ High' : '▼ Low') + '</td></tr>';
    });
    return html + '</tbody></table>';
  }

  function addStyles() {
    if (document.getElementById('lr-css')) return;
    var s = document.createElement('style');
    s.id = 'lr-css';
    s.textContent =
      '.lr-wind{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;margin-bottom:.5rem}' +
      '.lr-compass{flex-shrink:0;text-align:center}' +
      '.lr-clabel{font-size:.95rem;font-weight:700;color:#00D4FF;margin-top:.1rem}' +
      '.lr-gauges{flex:1;min-width:160px}' +
      '.lr-gr{display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem}' +
      '.lr-gl{font-size:.7rem;color:#B0BEC5;width:26px;text-align:right;flex-shrink:0}' +
      '.lr-gt{flex:1;height:8px;background:#0A1520;border-radius:4px;overflow:hidden}' +
      '.lr-gf{height:100%;border-radius:4px;background:#00D4FF}' +
      '.lr-gf.gust{background:#007A99}' +
      '.lr-gv{font-size:.82rem;font-weight:700;color:#fff;min-width:46px}' +
      '.lr-gscale{display:flex;justify-content:space-between;font-size:.62rem;color:#4A6070;padding:0 0 .1rem}' +
      '.lr-attr{font-size:.7rem;color:#B0BEC5;margin:.35rem 0 .75rem}' +
      '.lr-tstate{font-size:.88rem;color:#00D4FF;font-weight:600;margin-bottom:.45rem}' +
      '.lr-tide-svg{width:100%;height:auto;display:block;border-radius:6px;margin-bottom:.75rem}' +
      '.lr-tcols{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:.5rem}' +
      '@media(max-width:420px){.lr-tcols{grid-template-columns:1fr}}' +
      '.lr-tdl{font-size:.7rem;color:#B0BEC5;text-transform:uppercase;letter-spacing:.07em;font-weight:600;margin-bottom:.2rem}' +
      '.lr-tide-table{width:100%;border-collapse:collapse;font-size:.82rem}' +
      '.lr-tide-table td{padding:.22rem .25rem;color:#B0BEC5}' +
      '.lr-tide-table td:first-child{color:#fff;font-weight:600}' +
      '.lr-tide-table .lrh{color:#00D4FF}' +
      '.lr-tide-table .lrl{color:#F6A800}' +
      '.lr-waves{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.75rem}' +
      '.lr-chip{background:#0A1520;border:1px solid #1E3A50;border-radius:8px;padding:.3rem .65rem;font-size:.8rem;color:#B0BEC5}';
    document.head.appendChild(s);
  }

  window.initLiveReport = function (lat, lon) {
    var el = document.getElementById('live-report');
    if (!el) return;
    addStyles();
    el.innerHTML = '<span style="color:#B0BEC5;font-size:.85rem">Loading live conditions…</span>';

    var windUrl = 'https://api.open-meteo.com/v1/forecast?latitude=' + lat + '&longitude=' + lon
      + '&hourly=windspeed_10m,winddirection_10m,windgusts_10m'
      + '&windspeed_unit=mph&forecast_days=1&timezone=auto';
    var tidesUrl = API + '/forecast/tides/location?lat=' + lat + '&lon=' + lon;
    var marineUrl = 'https://marine-api.open-meteo.com/v1/marine?latitude=' + lat + '&longitude=' + lon
      + '&hourly=wave_height,wave_direction,wave_period,sea_surface_temperature&timezone=UTC&forecast_days=2';

    Promise.all([
      fetch(windUrl).then(function (r) { return r.json(); }).catch(function () { return null; }),
      fetch(tidesUrl).then(function (r) { return r.json(); }).catch(function () { return null; }),
      fetch(marineUrl).then(function (r) { return r.json(); }).catch(function () { return null; }),
    ]).then(function (res) {
      var wData = res[0], tData = res[1], mData = res[2];

      var now = new Date();
      var hStr = now.toISOString().slice(0, 13);
      var idx = (wData && wData.hourly && wData.hourly.time)
        ? wData.hourly.time.findIndex(function (t) { return t.startsWith(hStr); }) : -1;

      var spd = idx >= 0 ? Math.round(wData.hourly.windspeed_10m[idx]) : null;
      var gst = idx >= 0 ? Math.round(wData.hourly.windgusts_10m[idx]) : null;
      var dir = idx >= 0 ? wData.hourly.winddirection_10m[idx] : null;

      var exts = (tData && tData.tide_extremes) ? tData.tide_extremes : [];

      var mIdx = (mData && mData.hourly && mData.hourly.time)
        ? mData.hourly.time.findIndex(function (t) { return t.startsWith(hStr); }) : -1;
      var waveH = mIdx >= 0 ? mData.hourly.wave_height[mIdx] : null;
      var waveP = mIdx >= 0 ? mData.hourly.wave_period[mIdx] : null;
      var waveD = mIdx >= 0 ? mData.hourly.wave_direction[mIdx] : null;
      var waterT = mIdx >= 0 ? mData.hourly.sea_surface_temperature[mIdx] : null;
      var waveDirStr = waveD !== null ? DIRS[Math.round(waveD / 22.5) % 16] : null;

      var MAX = 50;
      var html = '';

      // Wind
      html += '<div class="lr-wind">';
      if (dir !== null) {
        html += '<div class="lr-compass">' + compassSVG(dir)
          + '<div class="lr-clabel">' + degToCompass(dir) + ' ' + Math.round(dir) + '°</div></div>';
      }
      html += '<div class="lr-gauges">';
      if (spd !== null) {
        html += '<div class="lr-gr"><span class="lr-gl">Wind</span>'
          + '<div class="lr-gt"><div class="lr-gf" style="width:' + Math.min(100, spd / MAX * 100).toFixed(1) + '%"></div></div>'
          + '<span class="lr-gv">' + spd + ' mph</span></div>';
      }
      if (gst !== null) {
        html += '<div class="lr-gr"><span class="lr-gl">Gust</span>'
          + '<div class="lr-gt"><div class="lr-gf gust" style="width:' + Math.min(100, gst / MAX * 100).toFixed(1) + '%"></div></div>'
          + '<span class="lr-gv">' + gst + ' mph</span></div>';
      }
      html += '<div class="lr-gscale"><span>0</span><span>50 mph</span></div>';
      html += '</div></div>';

      // Attribution — clearly labelled as forecast, not live station reading
      html += '<div class="lr-attr">Open-Meteo hourly forecast · ' + fmtCoord(lat, lon) + '</div>';

      // Tides
      if (exts.length) {
        var ts = tideStateText(exts);
        if (ts) html += '<div class="lr-tstate">' + ts + '</div>';
        html += tideSVG(exts);
        var t0html = tideTableHTML(exts, 0);
        var t1html = tideTableHTML(exts, 1);
        if (t0html || t1html) {
          html += '<div class="lr-tcols">';
          if (t0html) html += '<div><div class="lr-tdl">Today’s Tides</div>' + t0html + '</div>';
          if (t1html) html += '<div><div class="lr-tdl">Tomorrow’s Tides</div>' + t1html + '</div>';
          html += '</div>';
        }
      }

      // Wave chips
      var chips = [];
      if (waveH !== null) {
        var wl = waveH.toFixed(1) + 'm';
        if (waveP !== null) wl += ' · ' + Math.round(waveP) + 's';
        if (waveDirStr) wl += ' · ' + waveDirStr;
        chips.push('🌊 ' + wl);
      }
      if (waterT !== null) chips.push('🌡️ ' + waterT.toFixed(1) + '°C');
      if (chips.length) {
        html += '<div class="lr-waves">';
        chips.forEach(function (c) { html += '<div class="lr-chip">' + c + '</div>'; });
        html += '</div>';
      }

      el.innerHTML = html || '<span style="color:#B0BEC5;font-size:.85rem">Conditions unavailable</span>';
    }).catch(function () {
      el.innerHTML = '<span style="color:#B0BEC5;font-size:.85rem">Live conditions unavailable</span>';
    });
  };
}());
