package com.gamebridge.push

import java.security.MessageDigest
import java.time.Duration

enum class PushProvider { FCM, APNS }
enum class PushFailure { TIMEOUT, RATE_LIMIT, SERVER_ERROR, INVALID_TOKEN, PERMANENT }

/** maxRetries counts retries after the original attempt. */
internal class PushRetryPolicy(val maxRetries: Int = 3, val initialSeconds: Long = 5) {
    init { require(maxRetries >= 0 && initialSeconds > 0) }
    fun delay(provider: PushProvider, failure: PushFailure, retriesAlreadyPerformed: Int): Duration? {
        require(retriesAlreadyPerformed >= 0)
        if (retriesAlreadyPerformed >= maxRetries || failure in setOf(PushFailure.INVALID_TOKEN, PushFailure.PERMANENT)) return null
        val shift = retriesAlreadyPerformed.coerceAtMost(60)
        val exponential = if (initialSeconds > Long.MAX_VALUE shr shift) Long.MAX_VALUE else initialSeconds shl shift
        val seconds = if (provider == PushProvider.APNS && failure == PushFailure.SERVER_ERROR) maxOf(exponential, 900) else exponential
        return Duration.ofSeconds(seconds)
    }
}
/** One process only; identities are hashed and stale buckets are discarded. */
internal class DevPushRateLimiter(private val limit: Int = 10, private val nanoTime: () -> Long = System::nanoTime) {
    private val buckets = mutableMapOf<String, ArrayDeque<Long>>()
    init { require(limit > 0) }
    @Synchronized fun allow(adminKey: String): Boolean {
        val now = nanoTime(); val window = Duration.ofMinutes(1).toNanos()
        buckets.values.forEach { queue -> while (queue.isNotEmpty() && now - queue.first() >= window) queue.removeFirst() }
        buckets.entries.removeIf { it.value.isEmpty() }
        val hash = MessageDigest.getInstance("SHA-256").digest(adminKey.toByteArray(Charsets.UTF_8)).joinToString("") { "%02x".format(it) }
        val bucket = buckets.getOrPut(hash) { ArrayDeque() }
        if (bucket.size >= limit) return false
        bucket.addLast(now); return true
    }
}
