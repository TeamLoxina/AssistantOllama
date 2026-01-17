package com.example.assistant

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
                val answer = json?.split(""answer":"")?.getOrNull(1)?.split(""")?.get(0) ?: "Erreur"
                (context as MainActivity).showResponse(answer)
            }
        })
    }
}