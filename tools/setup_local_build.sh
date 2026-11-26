#!/bin/bash
# 로컬에서 APK를 빌드하기 위한 JDK/SDK/Gradle 준비 (워크스페이스 안에만 설치)
set -euo pipefail
ROOT=/workspace/.cache/android-build
mkdir -p "$ROOT"

echo "== JDK =="
if [ ! -d "$ROOT/jdk" ]; then
  URL=$(curl -sS -m 60 "https://api.adoptium.net/v3/assets/latest/17/hotspot?architecture=x64&image_type=jdk&os=linux&vendor=eclipse" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['binary']['package']['link'])")
  echo "url: $URL"
  curl -sS -L -m 280 -o "$ROOT/jdk.tar.gz" "$URL"
  mkdir -p "$ROOT/jdk_tmp"
  tar -xzf "$ROOT/jdk.tar.gz" -C "$ROOT/jdk_tmp"
  mv "$ROOT"/jdk_tmp/* "$ROOT/jdk"
  rm -rf "$ROOT/jdk_tmp" "$ROOT/jdk.tar.gz"
fi
"$ROOT/jdk/bin/java" -version 2>&1 | head -3

echo "== cmdline-tools =="
if [ ! -d "$ROOT/sdk/cmdline-tools/latest" ]; then
  curl -sS -L -m 280 -o "$ROOT/cmdline.zip" "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
  mkdir -p "$ROOT/sdk/cmdline-tools"
  python3 - "$ROOT/cmdline.zip" "$ROOT/sdk/cmdline-tools" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); z.extractall(sys.argv[2])
PY
  mv "$ROOT/sdk/cmdline-tools/cmdline-tools" "$ROOT/sdk/cmdline-tools/latest"
  rm -f "$ROOT/cmdline.zip"
fi
ls "$ROOT/sdk/cmdline-tools/latest/bin" | head

echo "== gradle =="
if [ ! -d "$ROOT/gradle-8.7" ]; then
  curl -sS -L -m 280 -o "$ROOT/gradle.zip" "https://services.gradle.org/distributions/gradle-8.7-bin.zip"
  python3 - "$ROOT/gradle.zip" "$ROOT" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1]); z.extractall(sys.argv[2])
PY
  rm -f "$ROOT/gradle.zip"
fi
ls -d "$ROOT/gradle-8.7"

echo "== done =="
du -sh "$ROOT"/*
