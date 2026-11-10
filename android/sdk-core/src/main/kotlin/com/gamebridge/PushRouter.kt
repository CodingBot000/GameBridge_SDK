package com.gamebridge

enum class PushEventKind { RECEIVED, OPENED }
data class PushRouteEvent(val payload: PushPayload, val kind: PushEventKind)
enum class PushEnqueueResult { QUEUED, DELIVER, DUPLICATE, BUSY }

/** One instance per SDK session. Call reset on logout/account change. */
class PushRouter {
    private var ready = false
    private val queue = ArrayDeque<PushRouteEvent>()
    private val seen = LinkedHashMap<String, MutableSet<PushEventKind>>(200, 0.75f, true)
    @Synchronized fun submit(event: PushRouteEvent): PushEnqueueResult {
        val prior = seen[event.payload.messageId]
        if (prior?.contains(event.kind) == true) return PushEnqueueResult.DUPLICATE
        if (!ready && queue.size >= 100) return PushEnqueueResult.BUSY
        val types = prior ?: mutableSetOf<PushEventKind>().also { seen[event.payload.messageId] = it }
        types.add(event.kind)
        while (seen.size > 200) seen.remove(seen.entries.first().key)
        if (ready) return PushEnqueueResult.DELIVER
        queue.addLast(event); return PushEnqueueResult.QUEUED
    }
    @Synchronized fun setReady(): List<PushRouteEvent> {
        ready = true
        return queue.toList().also { queue.clear() }
    }
    @Synchronized fun reset() { ready = false; queue.clear(); seen.clear() }
}
