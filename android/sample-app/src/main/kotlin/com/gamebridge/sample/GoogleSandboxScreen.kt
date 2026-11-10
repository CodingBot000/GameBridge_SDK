package com.gamebridge.sample

import android.app.Activity
import android.content.Context
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import com.gamebridge.*
import com.gamebridge.android.KeystoreTokenStore
import com.gamebridge.android.auth.GoogleAuthProvider
import com.gamebridge.android.purchase.GooglePlayStore
import kotlinx.coroutines.*

class GoogleSandboxModel : ViewModel() {
    var appId by mutableStateOf("")
    var backendURL by mutableStateOf("")
    var clientId by mutableStateOf("")
    var coinsId by mutableStateOf("")
    var premiumId by mutableStateOf("")
    var status by mutableStateOf("Enter sandbox configuration."); private set
    var configured by mutableStateOf(false); private set
    var signedIn by mutableStateOf(false); private set
    var connected by mutableStateOf(false); private set
    var busy by mutableStateOf(false); private set
    var products by mutableStateOf<List<StoreProduct>>(emptyList()); private set
    var wallet by mutableStateOf<EntitlementSnapshot?>(null); private set
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private var auth: GoogleAuthProvider? = null
    private var store: GooglePlayStore? = null
    private var events: Job? = null

    fun attachHost(activity: Activity) { store?.attachHost(activity) }
    fun detachHost() { store?.detachHost() }
    fun configure(context: Context, activity: Activity) = run {
        if (configured) throw SdkFailure("BUSY")
        if (clientId.isBlank()) throw SdkFailure("CONFIG_REQUIRED")
        val config = GameBridgeConfig(appId, ProviderMode.PLATFORM_SANDBOX, backendURL, clientId)
        val auth = GoogleAuthProvider.create(context, config, KeystoreTokenStore(context, "sandbox_google"))
        val store = GooglePlayStore.create(context, config, auth, mapOf("coins_100" to coinsId, "premium_unlock" to premiumId))
        this.auth = auth; this.store = store; store.attachHost(activity); configured = true
        events = scope.launch {
            store.events.collect { event ->
                status = "Purchase: ${event.status}"
                if (event.status == PurchaseStatus.PURCHASED) try { wallet = store.entitlements() }
                catch (cancel: CancellationException) { throw cancel }
                catch (_: Exception) { status = "Balance refresh unavailable" }
            }
        }
        status = "Sandbox configured. Sign in to continue."
    }
    fun signIn() = run { val auth = auth ?: throw SdkFailure("CONFIG_REQUIRED"); auth.signIn(); signedIn = true; status = "Google sign-in complete." }
    fun restoreSession() = run { val auth = auth ?: throw SdkFailure("CONFIG_REQUIRED"); signedIn = auth.restore() != null; status = if (signedIn) "Session restored." else "No saved session." }
    fun connectStore() = run { val store = store ?: throw SdkFailure("CONFIG_REQUIRED"); store.recover(); connected = true; status = "Store connected." }
    fun load() = run { val store = store ?: throw SdkFailure("CONFIG_REQUIRED"); products = store.products(); wallet = store.entitlements(); status = "Products and server balance loaded." }
    fun purchase(product: StoreProduct) = run { val store = store ?: throw SdkFailure("CONFIG_REQUIRED"); status = "Purchase: ${store.purchase(product.productId)}" }
    fun restorePurchases() = run { val store = store ?: throw SdkFailure("CONFIG_REQUIRED"); store.recover(); wallet = store.entitlements(); status = "Restore requested." }
    fun signOut() = run {
        val auth = auth ?: throw SdkFailure("CONFIG_REQUIRED")
        try { auth.signOut(); status = "Signed out." }
        finally { events?.cancel(); events = null; store?.close(); store = null; this.auth = null; configured = false; signedIn = false; connected = false; products = emptyList(); wallet = null }
    }
    private fun run(action: suspend () -> Unit) {
        if (busy) return
        busy = true
        scope.launch {
            try { action() }
            catch (_: ConfigurationException) { status = "CONFIG_REQUIRED" }
            catch (error: SdkFailure) { status = if (error.nativeCode == "REVOCATION_UNCONFIRMED") "${error.code} — local session cleared; server revoke unconfirmed" else error.code }
            catch (_: CancellationException) { throw CancellationException() }
            catch (_: Exception) { status = "INTERNAL_ERROR" }
            finally { busy = false }
        }
    }
    override fun onCleared() { events?.cancel(); store?.close(); scope.cancel(); super.onCleared() }
}

@Composable
fun GoogleSandboxScreen(model: GoogleSandboxModel, activity: Activity, onBack: () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("Google Sandbox", style = MaterialTheme.typography.titleLarge)
        Text("Use a configured Play test app and test account.")
        Text(model.status)
        OutlinedTextField(model.appId, { model.appId = it }, label = { Text("App ID") }, enabled = !model.configured, modifier = Modifier.fillMaxWidth(), singleLine = true)
        OutlinedTextField(model.backendURL, { model.backendURL = it }, label = { Text("HTTPS Backend URL") }, enabled = !model.configured, modifier = Modifier.fillMaxWidth(), singleLine = true)
        OutlinedTextField(model.clientId, { model.clientId = it }, label = { Text("Google server client ID") }, enabled = !model.configured, modifier = Modifier.fillMaxWidth(), singleLine = true)
        OutlinedTextField(model.coinsId, { model.coinsId = it }, label = { Text("Coins store product ID") }, enabled = !model.configured, modifier = Modifier.fillMaxWidth(), singleLine = true)
        OutlinedTextField(model.premiumId, { model.premiumId = it }, label = { Text("Premium store product ID") }, enabled = !model.configured, modifier = Modifier.fillMaxWidth(), singleLine = true)
        Button(enabled = !model.busy && !model.configured, onClick = { model.configure(activity.applicationContext, activity) }) { Text("Configure sandbox") }
        Button(enabled = !model.busy && model.configured && !model.signedIn, onClick = model::signIn) { Text("Sign in with Google") }
        Button(enabled = !model.busy && model.configured && !model.signedIn, onClick = model::restoreSession) { Text("Restore session") }
        Button(enabled = !model.busy && model.signedIn && !model.connected, onClick = model::connectStore) { Text("Connect store") }
        Button(enabled = !model.busy && model.connected, onClick = model::load) { Text("Load products and balance") }
        model.products.forEach { product -> Button(enabled = !model.busy && model.connected, onClick = { model.purchase(product) }) { Text("${product.title} — ${product.localizedPrice}") } }
        Button(enabled = !model.busy && model.connected, onClick = model::restorePurchases) { Text("Restore purchases") }
        Button(enabled = !model.busy && model.configured, onClick = model::signOut) { Text("Sign out sandbox") }
        Text("Coins: ${model.wallet?.coinBalance ?: "—"}; premium: ${model.wallet?.premiumEnabled ?: false}")
        Button(onClick = onBack) { Text("Back to local mock") }
    }
}
