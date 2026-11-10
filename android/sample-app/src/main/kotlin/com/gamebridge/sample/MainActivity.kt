package com.gamebridge.sample

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.gamebridge.*
import com.gamebridge.android.KeystoreTokenStore
import kotlinx.coroutines.launch
import java.util.UUID

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                var url by remember { mutableStateOf("http://10.0.2.2:18080") }
                var key by remember { mutableStateOf("") }
                var client by remember { mutableStateOf<LocalMockClient?>(null) }
                var message by remember { mutableStateOf("LOCAL_MOCK — not connected") }
                var products by remember { mutableStateOf<List<LocalProduct>>(emptyList()) }
                var wallet by remember { mutableStateOf<LocalWallet?>(null) }
                var busy by remember { mutableStateOf(false) }
                val scope = rememberCoroutineScope()
                fun run(action: suspend () -> Unit) {
                    if (busy) return
                    busy = true
                    scope.launch {
                        try { action() }
                        catch (e: SdkFailure) { message = e.code }
                        catch (_: Exception) { message = "INTERNAL_ERROR" }
                        finally { busy = false }
                    }
                }
                Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("GameBridge ${GameBridgeVersion.CURRENT} — LOCAL_MOCK", style = MaterialTheme.typography.titleLarge)
                    Text("Only a local fake backend. No real store purchase is performed.")
                    OutlinedTextField(value = url, onValueChange = { url = it }, label = { Text("Backend URL") }, modifier = Modifier.fillMaxWidth(), singleLine = true)
                    OutlinedTextField(value = key, onValueChange = { key = it }, label = { Text("Development key") }, modifier = Modifier.fillMaxWidth(), singleLine = true,
                        visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password))
                    Button(enabled = !busy, onClick = {
                        run {
                            client = LocalMockClient(GameBridgeConfig("gamebridge-sample", ProviderMode.LOCAL_MOCK, url), KeystoreTokenStore(applicationContext), key)
                            message = "Initialized LOCAL_MOCK"
                        }
                    }) { Text("Initialize") }
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Button(enabled = !busy && client != null, onClick = { run { val user = client!!.signIn("A"); message = "Signed in: ${user.userId}" } }) { Text("Mock login A") }
                        Button(enabled = !busy && client != null, onClick = { run { val user = client!!.restore(); message = if (user == null) "No session" else "Restored: ${user.userId}" } }) { Text("Restore") }
                    }
                    Button(enabled = !busy && client != null, onClick = { run { products = client!!.products(); wallet = client!!.wallet(); message = "Server state loaded" } }) { Text("Load products & balance") }
                    products.forEach { product ->
                        Button(enabled = !busy && client != null, onClick = { run {
                            val result = client!!.purchase(product.productId, UUID.randomUUID(), UUID.randomUUID())
                            wallet = result.entitlements; message = "${result.fulfillmentStatus} / ${result.finalizationStatus}"
                        } }) { Text("Mock purchase ${product.productId}") }
                    }
                    Button(enabled = !busy && client != null, onClick = { run { client!!.signOut(); products = emptyList(); wallet = null; message = "Signed out" } }) { Text("Sign out") }
                    Text("Coins: ${wallet?.coinBalance ?: "—"}; premium: ${wallet?.premiumEnabled ?: false}")
                    Text(message)
                }
            }
        }
    }
}
