package com.gamebridge.android.push

import android.Manifest
import android.app.Activity
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.RemoteMessage

/** Host owns Firebase initialization, service registration and Android permission results. */
class AndroidPushHostAdapter(
    private val onToken: (String) -> Unit,
    private val onMessage: (Map<String, String>, Boolean) -> Unit,
    private val onError: () -> Unit,
) {
    fun hasNotificationPermission(context: Context): Boolean = Build.VERSION.SDK_INT < 33 ||
        context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    /** Call only in response to the user's explicit action; host handles onRequestPermissionsResult. */
    fun requestNotificationPermission(activity: Activity, requestCode: Int) {
        if (Build.VERSION.SDK_INT >= 33) activity.requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), requestCode)
    }

    fun createChannel(context: Context, channelId: String, displayName: String) {
        require(channelId.isNotBlank() && displayName.isNotBlank())
        val manager = context.getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(NotificationChannel(channelId, displayName, NotificationManager.IMPORTANCE_DEFAULT))
    }

    /** Explicit only: host must have initialized the default FirebaseApp. */
    @Suppress("DEPRECATION")
    fun register() {
        try {
            FirebaseMessaging.getInstance().token.addOnSuccessListener { onToken(it) }.addOnFailureListener { onError() }
        } catch (_: IllegalStateException) { onError() }
    }
    /** Host service forwards token rotation; token must be sent only to the configured Backend. */
    fun onNewToken(token: String) { if (token.isNotBlank()) onToken(token) else onError() }
    fun onMessageReceived(message: RemoteMessage) { onMessage(message.data.toMap(), false) }
    /** Host validates and forwards its launch/click intent data. */
    fun onNotificationOpened(data: Map<String, String>) { onMessage(data.toMap(), true) }
}
