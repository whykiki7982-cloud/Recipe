package com.minjeong.recipebook;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * 민정 레시피북: assets/index.html 을 WebView 로 띄우는 얇은 껍데기.
 *
 * - localStorage 가 살아남도록 DOM storage / database 를 켠다 (레시피 데이터가 여기에 저장된다)
 * - 뒤로가기: 열린 창을 먼저 닫고, 없으면 두 번 눌러 종료
 * - 백업 파일(blob) 내보내기와 .json 불러오기를 네이티브로 이어준다
 */
public class MainActivity extends Activity {

    private static final String APP_URL = "file:///android_asset/index.html";
    private static final int REQ_FILE_CHOOSER = 1001;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private long lastBackPressed = 0L;

    /** 열려 있는 모달/창을 HTML 쪽 close*() 함수로 닫는다. */
    private static final String BACK_JS =
            "(function(){try{" +
            "var m={confirmOverlay:'closeConfirm',detailOverlay:'closeDetail',formOverlay:'closeForm'," +
            "fridgeOverlay:'closeFridge',shopOverlay:'closeShop',schoolOverlay:'closeSchool'," +
            "weightOverlay:'closeWeight',bikeOverlay:'closeBike'};" +
            "var api=window.RecipeBookClose||{};" +
            "for(var k in m){var el=document.getElementById(k);" +
            "if(el&&el.classList&&el.classList.contains('show')){" +
            "var fn=api[k]||window[m[k]];" +
            "if(typeof fn==='function'){try{fn();}catch(e){}}" +
            "return 'handled';}}" +
            "}catch(e){}return 'no';})()";

    /** 백업 내보내기(blob 다운로드)를 네이티브 저장으로 연결한다. */
    private static final String BLOB_PATCH_JS =
            "(function(){if(window.__rbBlobPatched)return 'already';window.__rbBlobPatched=true;" +
            "document.addEventListener('click',function(e){" +
            "var a=(e.target&&e.target.closest)?e.target.closest('a[download]'):null;" +
            "if(!a)return;var href=a.getAttribute('href')||'';" +
            "if(href.indexOf('blob:')!==0)return;" +
            "e.preventDefault();e.stopPropagation();" +
            "fetch(href).then(function(r){return r.blob();}).then(function(b){" +
            "var fr=new FileReader();" +
            "fr.onload=function(){try{window.RecipeBookNative.saveFile(a.getAttribute('download')||'recipe-book-backup.json',String(fr.result));}catch(err){}};" +
            "fr.readAsDataURL(b);}).catch(function(){});" +
            "},true);return 'ok';})()";

    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        web = new WebView(this);
        web.setLayoutParams(new android.widget.FrameLayout.LayoutParams(
                android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                android.view.ViewGroup.LayoutParams.MATCH_PARENT));
        web.setBackgroundColor(Color.parseColor("#FFFBF2"));
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);            // localStorage — 레시피 데이터 보존의 핵심
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowContentAccess(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setJavaScriptCanOpenWindowsAutomatically(false);
        s.setSupportMultipleWindows(false);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            s.setSafeBrowsingEnabled(true);
        }

        web.addJavascriptInterface(new NativeBridge(), "RecipeBookNative");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return handleUrl(request.getUrl().toString());
            }

            @Override
            @SuppressWarnings("deprecation")
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleUrl(url);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                view.evaluateJavascript(BLOB_PATCH_JS, null);
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                if (fileCallback != null) {
                    fileCallback.onReceiveValue(null);
                }
                fileCallback = callback;
                try {
                    Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    // accept=".json,application/json" — 확장자 필터는 피커마다 달라서 전체 허용
                    intent.setType("*/*");
                    startActivityForResult(Intent.createChooser(intent, "백업 파일 선택"), REQ_FILE_CHOOSER);
                    return true;
                } catch (Exception e) {
                    fileCallback = null;
                    Toast.makeText(MainActivity.this, "파일을 열 수 있는 앱을 찾지 못했어요", Toast.LENGTH_SHORT).show();
                    return false;
                }
            }
        });

        web.setDownloadListener((url, userAgent, contentDisposition, mimetype, contentLength) -> {
            // http(s) 파일은 기본 브라우저에 맡긴다 (blob 은 BLOB_PATCH_JS 가 처리)
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
            } catch (Exception ignored) {
            }
        });

        setContentView(web);
        WebView.setWebContentsDebuggingEnabled(false);

        applySystemBarStyle();
        web.loadUrl(APP_URL);
    }

    private void applySystemBarStyle() {
        int flags = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        }
        getWindow().getDecorView().setSystemUiVisibility(flags);
    }

    /** file:// 은 앱 안에서, 바깥 링크는 기본 브라우저에서 연다. */
    private boolean handleUrl(String url) {
        if (url == null) return false;
        if (url.startsWith("file://")) return false;
        if (url.startsWith("http://") || url.startsWith("https://")
                || url.startsWith("mailto:") || url.startsWith("tel:")) {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
            } catch (Exception ignored) {
            }
            return true;
        }
        return true;
    }

    @Override
    public void onBackPressed() {
        web.evaluateJavascript(BACK_JS, value -> {
            boolean handled = value != null && value.contains("handled");
            if (handled) return;
            if (web.canGoBack()) {
                web.goBack();
                return;
            }
            long now = System.currentTimeMillis();
            if (now - lastBackPressed < 2000) {
                moveTaskToBack(true);
            } else {
                lastBackPressed = now;
                Toast.makeText(MainActivity.this, "한 번 더 누르면 앱이 닫혀요", Toast.LENGTH_SHORT).show();
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQ_FILE_CHOOSER) {
            if (fileCallback != null) {
                Uri[] result = null;
                if (resultCode == RESULT_OK && data != null && data.getData() != null) {
                    result = new Uri[]{data.getData()};
                }
                fileCallback.onReceiveValue(result);
                fileCallback = null;
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    protected void onPause() {
        if (web != null) web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.loadUrl("about:blank");
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }

    /** 백업 파일(data URL)을 다운로드 폴더에 저장한다. */
    private class NativeBridge {
        @JavascriptInterface
        public void saveFile(String fileName, String dataUrl) {
            try {
                int comma = dataUrl.indexOf(',');
                if (comma < 0) return;
                byte[] bytes = Base64.decode(dataUrl.substring(comma + 1), Base64.DEFAULT);

                String safeName = (fileName == null || fileName.trim().isEmpty())
                        ? "recipe-book-backup.json"
                        : fileName.replaceAll("[\\\\/:*?\"<>|]", "_");

                String where;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    ContentValues values = new ContentValues();
                    values.put(MediaStore.Downloads.DISPLAY_NAME, safeName);
                    values.put(MediaStore.Downloads.MIME_TYPE, "application/json");
                    values.put(MediaStore.Downloads.IS_PENDING, 1);
                    Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                    if (uri == null) throw new IllegalStateException("insert failed");
                    try (OutputStream out = getContentResolver().openOutputStream(uri)) {
                        if (out == null) throw new IllegalStateException("no stream");
                        out.write(bytes);
                    }
                    values.clear();
                    values.put(MediaStore.Downloads.IS_PENDING, 0);
                    getContentResolver().update(uri, values, null, null);
                    where = "다운로드 폴더";
                } else {
                    File dir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
                    if (dir == null) dir = new File(getFilesDir(), "backup");
                    if (!dir.exists() && !dir.mkdirs()) throw new IllegalStateException("mkdir failed");
                    File outFile = new File(dir, safeName);
                    try (FileOutputStream out = new FileOutputStream(outFile)) {
                        out.write(bytes);
                    }
                    where = outFile.getAbsolutePath();
                }

                final String message = "백업 파일을 저장했어요: " + where;
                runOnUiThread(() -> Toast.makeText(MainActivity.this, message, Toast.LENGTH_LONG).show());
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "백업 파일을 저장하지 못했어요", Toast.LENGTH_SHORT).show());
            }
        }
    }
}
