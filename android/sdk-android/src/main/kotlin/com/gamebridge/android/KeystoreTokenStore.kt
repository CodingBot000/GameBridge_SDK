package com.gamebridge.android

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import com.gamebridge.SdkFailure
import com.gamebridge.TokenStore
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

/** Application-private encrypted storage; the encryption key remains in Android Keystore. */
class KeystoreTokenStore @JvmOverloads constructor(context: Context, namespace: String = "default") : TokenStore {
    init { require(namespace.matches(Regex("[a-z0-9_-]{1,48}"))) { "Invalid storage namespace" } }
    private val prefs = context.applicationContext.getSharedPreferences(if (namespace == "default") "gamebridge_secure_tokens" else "gamebridge_secure_tokens_$namespace", Context.MODE_PRIVATE)
    private val alias = if (namespace == "default") "com.gamebridge.sdk.session.v1" else "com.gamebridge.sdk.session.v1.$namespace"
    companion object { private val keyLock = Any() }
    private fun key(): SecretKey = synchronized(keyLock) {
        val store = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (store.getKey(alias, null) as? SecretKey)?.let { return it }
        val generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        generator.init(KeyGenParameterSpec.Builder(alias, KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build())
        generator.generateKey()
    }
    override fun save(value: String) {
        try {
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.ENCRYPT_MODE, key())
            val packed = cipher.iv + cipher.doFinal(value.toByteArray(Charsets.UTF_8))
            if (!prefs.edit().putString("session", Base64.encodeToString(packed, Base64.NO_WRAP)).commit()) throw SdkFailure("INTERNAL_ERROR")
        } catch (error: Exception) { throw SdkFailure("INTERNAL_ERROR") }
    }
    override fun load(): String? {
        val encoded = prefs.getString("session", null) ?: return null
        try {
            val packed = Base64.decode(encoded, Base64.NO_WRAP)
            if (packed.size < 29) throw SdkFailure("INTERNAL_ERROR")
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, key(), GCMParameterSpec(128, packed.copyOfRange(0, 12)))
            return cipher.doFinal(packed.copyOfRange(12, packed.size)).toString(Charsets.UTF_8)
        } catch (error: Exception) { throw SdkFailure("INTERNAL_ERROR") }
    }
    override fun clear() {
        if (!prefs.edit().remove("session").commit()) throw SdkFailure("INTERNAL_ERROR")
    }
}
