package com.gamebridge

import java.io.File
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFails

@Serializable private data class Fixture(val profile: UserProfile, val product: StoreProduct, val purchase: PurchaseResult, val error: SdkError)
class ModelFixtureTest {
    private val json = Json { ignoreUnknownKeys = true }
    private fun fixture() = File("../../contracts/fixtures/models/roundtrip.json").readText()
    @Test fun `shared fixture round trips without loss`() {
        val original = json.decodeFromString<Fixture>(fixture())
        val roundTrip = json.decodeFromString<Fixture>(json.encodeToString(original))
        assertEquals(original, roundTrip)
        assertEquals("9223372036854775807", roundTrip.product.priceMicros)
        assertEquals("별빛 🎮", roundTrip.profile.displayName)
    }
    @Test fun `missing required nullable field and unknown enum are rejected`() {
        assertFails { json.decodeFromString<Fixture>(fixture().replace("\"displayName\":\"별빛 🎮\",", "")) }
        assertFails { json.decodeFromString<Fixture>(fixture().replace("\"CONSUMABLE\"", "\"UNKNOWN\"")) }
    }
}
