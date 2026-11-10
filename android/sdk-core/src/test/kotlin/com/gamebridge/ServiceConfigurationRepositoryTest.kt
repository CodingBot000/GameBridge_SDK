package com.gamebridge

import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import java.time.Instant
import kotlin.test.*

class ServiceConfigurationRepositoryTest {
    @Test fun `offline cache expires and unknown config blocks only new purchase`() = runBlocking {
        var now = Instant.parse("2030-01-01T00:00:00Z"); var available = true
        val repository = ServiceConfigurationRepository({ if (!available) error("offline"); ServiceSettings("test", false, null, now.plusSeconds(300)) }, { now })
        assertEquals(ConfigurationSource.REMOTE, repository.current()!!.source)
        available = false; now = now.plusSeconds(299); assertEquals(ConfigurationSource.CACHE, repository.current()!!.source)
        now = now.plusSeconds(1); val expired = repository.current(); assertNull(expired)
        assertFalse(MaintenanceGate.permits(expired?.settings?.maintenanceEnabled, ProtectedOperation.START_PURCHASE))
        assertTrue(MaintenanceGate.permits(expired?.settings?.maintenanceEnabled, ProtectedOperation.RECOVER_PURCHASE))
    }
}
