# minjeong-recipe-book (민정 레시피북)

민정님의 레시피북(`recipe-book.html`)을 **홈 화면에 바로 열리는 앱**으로 만들어 주는 저장소입니다.

- **웹 앱(PWA, `docs/`)** — GitHub Pages 에서 열리고, 홈 화면에 추가하면 앱처럼 뜹니다. 고친 내용이 새로고침만으로 바로 반영됩니다.
- **안드로이드 앱(APK)** — 같은 HTML 을 WebView 로 감싼 설치 파일(v1.0.0). 필요할 때만 다시 빌드합니다.

두 방식 모두 `localStorage` 에 저장하므로, 앱을 지우거나 브라우저 데이터를 지우면 기록도 함께 사라집니다. 백업(📤 백업 저장)으로 옮길 수 있습니다.

## 웹 앱(PWA) — `docs/`

| 파일 | 설명 |
| --- | --- |
| `docs/index.html` | 앱 본문 (`/workspace/recipe-book.html` 에서 생성) |
| `docs/manifest.json` | 이름·아이콘·테마 색(설치형 앱 설정) |
| `docs/sw.js` | 서비스 워커 — **온라인이면 서버에서 먼저**, 오프라인이면 캐시로 |
| `docs/icon-180/192/512.png` | 토마토 푸딩셰프 아이콘 |

- 주소: https://whykiki7982-cloud.github.io/Recipe/
- 다시 만들기: `python3 tools/make_docs.py` — `recipe-book.html` 을 복사하면서 **공개 페이지에 아이들 실제 하교 시간이 들어가지 않도록 빈 기본값**으로 바꾸고, manifest·아이콘·서비스 워커를 붙입니다.

### 켜는 방법 (2단계)

1. 저장소를 **Public** 으로 바꿉니다 — Settings → General → 맨 아래 Danger Zone → Change visibility. (GitHub Free 에서 Pages 를 쓰려면 공개 저장소여야 합니다.)
2. Settings → **Pages** → Build and deployment → Source **Deploy from a branch** → Branch **main**, Folder **/docs** → Save.

1~2분 뒤 위 주소가 열립니다. 휴대폰 브라우저에서 열고 메뉴의 **홈 화면에 추가**를 누르면 앱처럼 설치됩니다.

> 공개되는 것은 앱 화면과 빈 기본값뿐입니다. 레시피·하교 시간·몸무게 기록·생리 주기 기록은 각 기기 브라우저에만 저장되고 서버로 올라가지 않습니다. 생리 주기 날짜도 화면(HTML)에 적어 두지 않고, 기록한 기기의 `localStorage`(`minjeong-recipebook-cycle-v1`)에만 남습니다. 서명 키(`keystore/`)는 `.gitignore` 로 저장소에 없습니다.

## 구조

```
docs/                               ← GitHub Pages(PWA) 배포 폴더
app/src/main/assets/index.html      ← APK 에 들어가는 레시피북 (워크스페이스의 recipe-book.html 을 복사)
app/src/main/java/.../MainActivity.java  ← WebView 껍데기 (localStorage, 뒤로가기, 백업 저장/불러오기)
app/src/main/res/...                ← 앱 이름, 아이콘(토마토 푸딩셰프)
tools/make_docs.py                  ← docs/ 생성 (공개 기본값 + PWA 설정)
tools/make_icons.py                 ← 런처 아이콘 다시 그리는 스크립트
```

## 빌드

현재 버전(v1.0.0)은 워크스페이스에서 직접 빌드해 전달했습니다. 빌드 환경(Gradle 8.7 / AGP 8.5.2 / JDK 17 / Android SDK 34)이 `/workspace/.cache/android-build` 에 준비되어 있어서, 다음 버전도 같은 방법으로 몇 분 안에 다시 만들 수 있습니다.

### GitHub Actions 자동 빌드 (아직 꺼져 있음)

워크플로 파일이 `tools/build-apk.workflow.yml` 에 있습니다. 저장소에 GitHub App 으로는 `.github/workflows/` 아래 파일을 올릴 수 없어서(workflows 권한 없음) 따로 보관 중입니다. 켜는 방법은 두 가지입니다.

1. GitHub 웹에서 직접: 저장소 → **Add file** → **Create new file** → 이름에 `.github/workflows/build-apk.yml` → `tools/build-apk.workflow.yml` 내용을 붙여넣고 Commit
2. Pickle 의 GitHub 연결에 **Workflows** 권한을 추가한 뒤 알려주면 자동으로 올려 드립니다

한 번 켜지면 `main` 에 push 할 때마다 APK 가 자동으로 만들어집니다.

* Actions 탭 → **Build APK** → 가장 최근 실행 → 아래쪽 **Artifacts** 의 `minjeong-recipe-book-apk`
* 결과물: `minjeong-recipe-book-v1.0.0.apk`

## 서명 (중요)

APK 는 `keystore/release.p12` 로 서명됩니다. **이 키스토어를 잃어버리면 다음 버전을 설치했을 때 서명이 달라져서 앱을 지우고 다시 깔아야 하고, 저장된 레시피도 사라집니다.**

키스토어는 저장소에 올리지 않고 GitHub Actions secret 으로 보관합니다.

| secret | 값 |
| --- | --- |
| `KEYSTORE_BASE64` | `keystore/release.p12` 를 base64 로 인코딩한 문자열 |
| `KEYSTORE_PASSWORD` | 키스토어 비밀번호 |
| `KEY_PASSWORD` | 키 비밀번호 (같은 값) |
| `KEY_ALIAS` | `minjeong-recipe-book` |

원본 파일과 비밀번호는 워크스페이스의 `keystore/` 폴더에 있습니다.

## 레시피북 내용을 고칠 때

1. `/workspace/recipe-book.html` 을 고친다
2. `cp /workspace/recipe-book.html app/src/main/assets/index.html`
3. `versionCode`/`versionName` 을 올린다 (`app/build.gradle`)
4. commit & push → Actions 가 새 APK 를 만든다
