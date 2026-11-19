package com.gamebridge.contracts

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.client.ClientHttpRequestInterceptor
import org.springframework.http.client.ClientHttpResponse
import java.io.ByteArrayInputStream
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption

/** Opt-in test-only structural evidence. Never writes string values, tokens or request bodies. */
object OpenApiCapture {
    private val mapper = ObjectMapper()
    private val lock = Any()
    internal fun shape(node: JsonNode): Any? = when {
        node.isObject -> node.fields().asSequence().associate { it.key to shape(it.value) }
        node.isArray -> node.map(::shape)
        node.isTextual -> "redacted"
        node.isBoolean -> node.booleanValue()
        node.isIntegralNumber -> node.longValue()
        node.isNumber -> node.doubleValue()
        else -> null
    }
    fun install(rest: TestRestTemplate) {
        val target = System.getenv("GAMEBRIDGE_OPENAPI_HTTP_EVIDENCE") ?: return
        require(Path.of(target).isAbsolute)
        val template=rest.restTemplate
        if (template.interceptors.any { it is Capture }) return
        template.interceptors=template.interceptors + Capture(Path.of(target))
    }
    private class Capture(private val target: Path): ClientHttpRequestInterceptor {
        override fun intercept(request: org.springframework.http.HttpRequest, body: ByteArray,
                               execution: org.springframework.http.client.ClientHttpRequestExecution): ClientHttpResponse {
            val response=execution.execute(request,body)
            if (response.headers.contentType?.toString()?.startsWith("text/event-stream")==true) return response
            val bytes=response.body.readAllBytes()
            val tree=runCatching { mapper.readTree(bytes) }.getOrNull()
            val id=response.headers.getFirst("X-Request-Id")
            val row=mapOf("path" to request.uri.path,"method" to request.method.name().lowercase(),"status" to response.statusCode.value(),
                "bodyShape" to tree?.let(::shape),"requestIdHeaderPresent" to (id!=null),
                "requestIdCorrelated" to (response.statusCode.value()<400 || tree?.get("requestId")?.asText()==id))
            synchronized(lock) {
                Files.writeString(target,mapper.writeValueAsString(row)+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND)
            }
            return object: ClientHttpResponse by response { override fun getBody() = ByteArrayInputStream(bytes) }
        }
    }
}
