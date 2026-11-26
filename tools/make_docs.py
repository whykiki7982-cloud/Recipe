#!/usr/bin/env python3
"""GitHub Pages(PWA)용 docs/ 만들기.

/workspace/recipe-book.html 을 복사하면서
  - 아이들 실제 하교 시간 같은 개인 정보가 들어간 기본값을 비운다 (공개 페이지!)
  - manifest / apple-touch-icon / service worker 등록을 넣는다
나머지는 앱과 완전히 같게 두어 localStorage 키·스키마가 그대로 이어진다.
"""
import pathlib, re, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent          # recipe-book-android/tools
PROJ = ROOT.parent                                      # recipe-book-android
SRC = PROJ.parent / "recipe-book.html"
DOCS = PROJ / "docs"

NEUTRAL_SEED = """function seedSchool(){
  /* 공개(PWA) 기본값: 아이 이름만 두고 하교 시간은 비워 둔다.
     저장된 값이 있으면 그대로 쓰고, 백업을 불러오면 그 값으로 채워진다. */
  return {
    children: [
      { id:'kid-1', name:'첫째', age:0, alert:true, days:{
        '월':{time:'',memo:''}, '화':{time:'',memo:''}, '수':{time:'',memo:''},
        '목':{time:'',memo:''}, '금':{time:'',memo:''}, '토':{time:'',memo:''}, '일':{time:'',memo:''}
      }},
      { id:'kid-2', name:'둘째', age:0, alert:true, days:{
        '월':{time:'',memo:''}, '화':{time:'',memo:''}, '수':{time:'',memo:''},
        '목':{time:'',memo:''}, '금':{time:'',memo:''}, '토':{time:'',memo:''}, '일':{time:'',memo:''}
      }}
    ],
    alert: {on:true, lead:10, sound:true, weekend:false, hintDismissed:false}
  };
}"""

HEAD_LINKS = """<meta name="theme-color" content="#E85D3F">
<meta name="description" content="레시피와 장보기, 아이들 하교 시간, 몸무게 기록과 자전거 타이머를 한 곳에 담은 민정님의 레시피북">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="레시피북">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">"""

SW_REGISTER = """<script>
/* GitHub Pages(https)에서만 서비스 워커를 붙인다. file:// 로 열면 그냥 앱처럼 동작. */
if('serviceWorker' in navigator && (location.protocol === 'https:' || location.protocol === 'http:')){
  window.addEventListener('load', function(){
    navigator.serviceWorker.register('sw.js').catch(function(){ /* 등록 실패해도 앱은 그대로 */ });
  });
}
</script>
</body>"""

MANIFEST = """{
  "name": "민정님의 레시피북",
  "short_name": "레시피북",
  "description": "레시피와 장보기, 아이들 하교 시간, 몸무게 기록과 자전거 타이머를 한 곳에",
  "lang": "ko",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "theme_color": "#E85D3F",
  "background_color": "#FFF9F3",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
"""

SW_JS = """/* 민정님의 레시피북 — 네트워크 우선(online) · 캐시 대체(offline) */
var CACHE = 'minjeong-recipebook-pwa-2026-11-26-3';
var ASSETS = ['./', './index.html', './manifest.json', './icon-180.png', './icon-192.png', './icon-512.png'];

self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(CACHE).then(function(c){
      return Promise.all(ASSETS.map(function(u){ return c.add(u).catch(function(){}); }));
    }).then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(e){
  var req = e.request;
  if(req.method !== 'GET') return;
  var url;
  try { url = new URL(req.url); } catch(err){ return; }
  if(url.origin !== self.location.origin) return;   /* 유튜브 썸네일 등 바깥 요청은 그대로 */

  var isNav = req.mode === 'navigate';
  e.respondWith(
    fetch(req, isNav ? {cache: 'no-store'} : undefined).then(function(res){
      if(res && res.ok){
        var copy = res.clone();
        caches.open(CACHE).then(function(c){ c.put(req, copy).catch(function(){}); });
      }
      return res;
    }).catch(function(){
      return caches.match(req).then(function(hit){
        if(hit) return hit;
        if(req.mode === 'navigate') return caches.match('./index.html');
        return Response.error();
      });
    })
  );
});
"""


def main():
    if not SRC.exists():
        sys.exit(f"원본이 없어요: {SRC}")
    html = SRC.read_text(encoding="utf-8")

    # 1) 공개 기본값으로: 하교 시간 시드 비우기
    html, n = re.subn(r"function seedSchool\(\)\{[\s\S]*?\n\}", NEUTRAL_SEED, html, count=1)
    if n != 1:
        sys.exit("seedSchool() 을 찾지 못했어요 — 원본 구조를 확인해 주세요")

    # 2) 알림 팝업의 예시 문구도 특정 시간 없이
    html = html.replace('id="schoolAlertBody">첫째 13:50 하교<', 'id="schoolAlertBody">아이 하교 시간<')

    # 3) head: 테마 색·manifest·아이콘 메타
    old_theme = '<meta name="theme-color" content="#FF5A36">'
    if old_theme not in html:
        sys.exit("theme-color 메타를 찾지 못했어요")
    html = html.replace(old_theme, HEAD_LINKS, 1)

    # 4) body 끝: 서비스 워커 등록
    if "</body>" not in html:
        sys.exit("</body> 를 찾지 못했어요")
    html = html.replace("</body>", SW_REGISTER, 1)

    # 5) 개인 정보(실제 하교 시간)가 남아 있지 않은지 확인
    leaks = [t for t in ("14:40", "17:00", "16:10", "13:50", "13:00") if t in html]
    if leaks:
        sys.exit(f"공개 페이지에 하교 시간이 남아 있어요: {leaks}")

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    (DOCS / "manifest.json").write_text(MANIFEST, encoding="utf-8")
    (DOCS / "sw.js").write_text(SW_JS, encoding="utf-8")
    print("docs/index.html", len(html), "bytes")

    # 6) 아이콘: 같은 토마토 푸딩 셰프 아이콘에서 크기만 바꾼다
    src_icon = ROOT / "preview" / "icon-legacy-512.png"
    if not src_icon.exists():
        sys.exit(f"아이콘 원본이 없어요: {src_icon}")
    base = Image.open(src_icon).convert("RGBA")
    for size in (180, 192, 512):
        out = base if size == 512 else base.resize((size, size), Image.LANCZOS)
        out.save(DOCS / f"icon-{size}.png", optimize=True)
        print(f"docs/icon-{size}.png")


if __name__ == "__main__":
    main()
