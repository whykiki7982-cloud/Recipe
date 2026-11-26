# keystore (저장소에 올리지 않음)

APK 서명용 키스토어입니다. 이 폴더의 파일들은 `.gitignore` 로 제외되어 GitHub 에 올라가지 않습니다.

| 파일 | 설명 |
| --- | --- |
| `release.p12` | 서명 키스토어 (PKCS12), 별칭 `minjeong-recipe-book` |
| `passwords.txt` | 비밀번호와 인증서 지문 |
| `.cert.pem` | 공개 인증서 (지문 확인용) |
| `.ks.b64` | CI secret `KEYSTORE_BASE64` 에 넣는 base64 문자열 |

**이 폴더를 지우거나 잃어버리면 이후 업데이트가 같은 서명으로 나갈 수 없습니다.** 그 경우 앱을 삭제 후 재설치해야 하고 저장된 레시피가 초기화됩니다.
