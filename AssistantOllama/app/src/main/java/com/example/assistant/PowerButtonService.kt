package com.example.assistant

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
}