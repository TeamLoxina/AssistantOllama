package com.example.assistant

import android.content.Context
import android.media.MediaRecorder
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException

object AudioService {

    private var recorder: MediaRecorder? = null
    private var audioFile: File? = null

    private val client = OkHttpClient()
    private const val SERVER_URL = "http://IP_DE_TON_PC:8000/upload_audio" 

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
        // Correction de la syntaxe RequestBody (Ligne 46)
        val audioBody = audioFile!!.asRequestBody("audio/wav".toMediaTypeOrNull())
        
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", "audio.wav", audioBody)
            .build()

        val request = Request.Builder()
            .url(SERVER_URL)
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) { e.printStackTrace() }
            override fun onResponse(call: Call, response: Response) {
                // Correction : body() est devenu une propriété body (Ligne 58)
                val json = response.body?.string()
                
                // Correction : Utilisation de guillemets simples pour entourer les guillemets doubles (Ligne 59)
                val answer = json?.split("\"answer\":\"")?.getOrNull(1)?.split("\"")?.get(0) ?: "Erreur"
                
                // Note : Assurez-vous que MainActivity possède bien cette fonction
                (context as? MainActivity)?.runOnUiThread {
                    (context as? MainActivity)?.showResponse(answer)
                }
            }
        })
    }
}
