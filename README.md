# minjeong-recipe-book (민정 레시피북)

민정님의 레시피북(`recipe-book.html`)을 **안드로이드에 설치할 수 있는 앱(.apk)** 으로 만들어 주는 저장소입니다.

휴대폰에서 HTML 파일을 열 때와 달리, 홈 화면 아이콘으로 바로 열리고 `localStorage` 에 저장한 레시피가 앱 데이터로 남습니다.

## 구조

```
app/src/main/assets/index.html      ← 앱에 들어가는 레시피북 (워크스페이스의 recipe-book.html 을 복사)
app/src/main/java/.../MainActivity.java  ← WebView 껍데기 (localStorage, 뒤로가기, 백업 저장/불러오기)
app/src/main/res/...                ← 앱 이름, 아이콘(토마토 푸딩셰프)
.github/workflows/build-apk.yml     ← push 할 때마다 APK 를 자동으로 빌드
tools/make_icons.py                 ← 런처 아이콘 다시 그리는 스크립트
```

## 빌드

`main` 브랜치에 push 하면 GitHub Actions 가 자동으로 빌드합니다.

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
