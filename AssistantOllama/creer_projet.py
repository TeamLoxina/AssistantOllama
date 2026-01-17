import os

# Remplace ce chemin par l'endroit où tu veux créer le projet
BASE_DIR = r"C:\Users\qwuic\Desktop\AssistantOllama"

files = {
    # Gradle racine
    "settings.gradle.kts": 'rootProject.name = "AssistantOllama"\ninclude(":app")',
    "build.gradle.kts": '''plugins {
    id("com.android.application") version "8.2.0" apply false
    kotlin("android") version "1.9.10" apply false
}''',

    # App build.gradle.kts
    "app/build.gradle.kts": '''plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.example.assistant"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.assistant"
        minSdk = 23
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}''',

    # AndroidManifest.xml
    "app/src/main/AndroidManifest.xml": '''<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.assistant">

    <uses-permission android:name="android.permission.RECORD_AUDIO"/>
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE"/>

    <application
        android:allowBackup="true"
        android:label="Assistant Ollama"
        android:theme="@style/Theme.AppCompat.Light.NoActionBar">

        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

        <service
            android:name=".PowerButtonService"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE"
            android:exported="true">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_service_config"/>
        </service>

    </application>
</manifest>''',

    # Layout
    "app/src/main/res/layout/activity_main.xml": '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:padding="16dp"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <TextView
        android:id="@+id/responseText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Réponse Ollama"
        android:textSize="20sp"/>
</LinearLayout>''',

    # Accessibility config
    "app/src/main/res/xml/accessibility_service_config.xml": '''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:notificationTimeout="100"
    android:canRetrieveWindowContent="true"
    android:accessibilityFlags="flagDefault"
    android:canRequestFilterKeyEvents="true"/>''',

    # MainActivity.kt
    "app/src/main/java/com/example/assistant/MainActivity.kt": '''package com.example.assistant

import android.os.Bundle
import android.widget.TextView
import android.speech.tts.TextToSpeech
import androidx.appcompat.app.AppCompatActivity
import java.util.Locale

class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {

    private lateinit var tts: TextToSpeech
    private lateinit var responseText: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        responseText = findViewById(R.id.responseText)
        tts = TextToSpeech(this, this)

        AudioService.start(this)
    }

    fun showResponse(text: String) {
        runOnUiThread {
            responseText.text = text
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "1")
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts.language = Locale.FRENCH
        }
    }

    override fun onDestroy() {
        tts.stop()
        tts.shutdown()
        super.onDestroy()
    }
}''',

    # AudioService.kt
    "app/src/main/java/com/example/assistant/AudioService.kt": '''package com.example.assistant

import android.content.Context
import android.media.MediaRecorder
import kotlinx.coroutines.*
import okhttp3.*
import java.io.File
import java.io.IOException

object AudioService {

    private var recorder: MediaRecorder? = null
    private var audioFile: File? = null

    private val client = OkHttpClient()
    private const val SERVER_URL = "http://IP_DE_TON_PC:8000/upload_audio" // Remplace par ton IP locale

    fun start(context: Context) {}

    fun recordAndSend(context: Context) {
        audioFile = File(context.cacheDir, "audio.wav")
        recorder = MediaRecorder().apply {
            setAudioSource(MediaRecorder.AudioSource.MIC)
            setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
            setOutputFile(audioFile!!.absolutePath)
            prepare()
            start()
        }

        GlobalScope.launch {
            delay(5000)
            recorder?.stop()
            recorder?.release()
            recorder = null
            sendAudio(context)
        }
    }

    private fun sendAudio(context: Context) {
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "file",
                "audio.wav",
                RequestBody.create(MediaType.parse("audio/wav"), audioFile!!)
            )
            .build()

        val request = Request.Builder()
            .url(SERVER_URL)
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) { e.printStackTrace() }
            override fun onResponse(call: Call, response: Response) {
                val json = response.body()?.string()
                val answer = json?.split("\"answer\":\"")?.getOrNull(1)?.split("\"")?.get(0) ?: "Erreur"
                (context as MainActivity).showResponse(answer)
            }
        })
    }
}''',

    # PowerButtonService.kt
    "app/src/main/java/com/example/assistant/PowerButtonService.kt": '''package com.example.assistant

import android.accessibilityservice.AccessibilityService
import android.view.KeyEvent
import android.widget.Toast

class PowerButtonService : AccessibilityService() {

    private var lastPressTime: Long = 0
    private val doublePressThreshold = 500L

    override fun onKeyEvent(event: KeyEvent?): Boolean {
        if (event?.keyCode == KeyEvent.KEYCODE_POWER && event.action == KeyEvent.ACTION_DOWN) {
            val currentTime = System.currentTimeMillis()
            if (currentTime - lastPressTime < doublePressThreshold) {
                Toast.makeText(this, "Double appui détecté", Toast.LENGTH_SHORT).show()
                AudioService.recordAndSend(applicationContext)
            }
            lastPressTime = currentTime
            return true
        }
        return super.onKeyEvent(event)
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        Toast.makeText(this, "Service PowerButton activé", Toast.LENGTH_SHORT).show()
    }

    override fun onInterrupt() {}
}'''
}

# Création des fichiers
for path, content in files.items():
    full_path = os.path.join(BASE_DIR, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Projet créé avec succès dans {BASE_DIR} !")
