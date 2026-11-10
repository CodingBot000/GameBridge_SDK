package com.gamebridge.android.purchase

import android.content.Context
import com.gamebridge.BackendClient
import com.gamebridge.backendServiceConfiguration
import com.gamebridge.android.auth.GoogleAuthProvider

/** Native-only composition; the host must supply a real Backend proof sink. */
internal object GoogleStoreRuntime {
    fun create(context: Context, auth: GoogleAuthProvider, client: BackendClient, productIds: Map<String, String>,
               sink: PlayProofSink, verificationConcurrency: Int = 1): GooglePlayBillingProvider {
        val config = backendServiceConfiguration(client)
        return GooglePlayBillingProvider(AndroidPlayGateway(context), productIds, GooglePurchaseAccountSource(auth, client), sink,
            verificationConcurrency = verificationConcurrency, uiGate = auth.uiGate, maintenanceState = { config.current()?.settings?.maintenanceEnabled })
    }
}
