// Opt-in P09 database runner; never changes the ordinary backend build classpath.
initscript {
    repositories { mavenCentral() }
    dependencies {
        classpath("org.testcontainers:testcontainers-postgresql:2.0.5")
        classpath("org.postgresql:postgresql:42.7.11")
        classpath("org.flywaydb:flyway-core:11.7.2")
        classpath("org.flywaydb:flyway-database-postgresql:11.7.2")
    }
}

import com.github.dockerjava.api.model.ExposedPort
import com.github.dockerjava.api.model.PortBinding
import com.github.dockerjava.api.model.Ports
import groovy.json.JsonOutput
import org.flywaydb.core.Flyway
import org.gradle.api.tasks.SourceSetContainer
import org.gradle.api.tasks.testing.Test
import org.testcontainers.postgresql.PostgreSQLContainer
import org.testcontainers.utility.DockerImageName
import java.util.UUID

// New containers own all data. Existing test classes still create their unique schemas.
gradle.projectsEvaluated {
    val target = gradle.rootProject
    val sources = target.extensions.getByType(SourceSetContainer::class.java)
    val cases = linkedMapOf(
        "tcPurchaseLocal" to listOf("LedgerInvariantDatabaseTest", "GoogleGrantDatabaseTest", "AppleGrantDatabaseTest", "FinalizationDatabaseTest", "PurchaseBindingsDatabaseTest"),
        "tcLedgerMutation" to listOf("LedgerInvariantDatabaseTest"),
        "tcLedgerNormal" to listOf("LedgerInvariantDatabaseTest"),
        "tcPurchaseSandbox" to listOf("GooglePurchaseHttpIntegrationTest", "ApplePurchaseHttpIntegrationTest")
    )
    cases.forEach { (name, classes) ->
        var owned: PostgreSQLContainer? = null
        val state = linkedMapOf<String, Any?>("task" to name, "image" to "postgres:17.6-alpine3.22", "containerStarted" to false, "containerStopped" to false)
        val stop = target.tasks.register("${name}StopOwned") {
            doLast {
                try {
                    owned?.stop()
                    state["containerStopped"] = owned != null && !owned!!.isRunning
                } finally {
                    val value = System.getenv("GAMEBRIDGE_TESTCONTAINERS_EVIDENCE")
                    if (value != null) {
                        val directory = File(value).canonicalFile
                        check(directory.toPath().startsWith(target.rootDir.parentFile.resolve("artifacts").canonicalFile.toPath()))
                        directory.mkdirs()
                        directory.resolve("$name.container.json").writeText(JsonOutput.toJson(state) + "\n")
                    }
                }
            }
        }
        target.tasks.register(name, Test::class.java) {
            val worker = this
            dependsOn(target.tasks.named("testClasses"))
            useJUnitPlatform()
            testClassesDirs = sources.getByName("test").output.classesDirs
            classpath = sources.getByName("test").runtimeClasspath
            maxParallelForks = 1
            filter { classes.forEach { includeTestsMatching("com.gamebridge.purchase.$it") } }
            reports.junitXml.outputLocation.set(target.layout.buildDirectory.dir("test-results/$name"))
            reports.html.required.set(false)
            finalizedBy(stop)
            doFirst {
                check(System.getenv("GAMEBRIDGE_RUN_TESTCONTAINERS") == "true") { "Explicit local Testcontainers opt-in required" }
                check(System.getenv("DOCKER_HOST")?.startsWith("unix://") == true) { "Local Unix Docker endpoint required" }
                val evidence = File(requireNotNull(System.getenv("GAMEBRIDGE_TESTCONTAINERS_EVIDENCE"))).canonicalFile
                check(evidence.toPath().startsWith(target.rootDir.parentFile.resolve("artifacts").canonicalFile.toPath()))
                val run = requireNotNull(System.getenv("GAMEBRIDGE_TESTCONTAINERS_RUN_ID"))
                val profile = if (name == "tcPurchaseSandbox") "sandbox" else "local-mock"
                state["sourceHead"] = System.getenv("GAMEBRIDGE_TESTCONTAINERS_SOURCE_HEAD")
                state["runId"] = run
                state["profile"] = profile
                val container = PostgreSQLContainer(DockerImageName.parse("postgres:17.6-alpine3.22"))
                    .withDatabaseName("gamebridge_test")
                    .withUsername("gamebridge_test")
                    .withPassword(UUID.randomUUID().toString())
                    .withLabel("com.gamebridge.harness.run", run)
                    .withCommand("postgres", "-c", "fsync=on")
                    .withCreateContainerCmdModifier { command ->
                        command.hostConfig!!.withPublishAllPorts(false).withPortBindings(
                            PortBinding(Ports.Binding.bindIpAndPort("127.0.0.1", 0), ExposedPort.tcp(5432))
                        )
                    }
                owned = container
                container.start()
                state["containerStarted"] = true
                state["containerId"] = container.containerId
                val bindings = container.containerInfo.networkSettings.ports.bindings[ExposedPort.tcp(5432)]
                check(bindings != null && bindings.isNotEmpty() && bindings.all { it.hostIp == "127.0.0.1" }) { "Loopback-only PostgreSQL binding required" }
                state["loopbackOnly"] = true
                state["mappedPort"] = container.getMappedPort(5432)
                check(container.containerInfo.config.labels?.get("com.gamebridge.harness.run") == run)
                if (profile == "local-mock") {
                    Flyway.configure().dataSource(container.jdbcUrl, container.username, container.password)
                        .locations("filesystem:${target.rootDir}/src/main/resources/db/migration", "filesystem:${target.rootDir}/src/main/resources/db/mock-migration")
                        .load().migrate()
                    val sql = "INSERT INTO gamebridge_environment VALUES(true,'local-mock');"
                    val initialized = container.execInContainer("psql", "-U", container.username, "-d", container.databaseName, "-v", "ON_ERROR_STOP=1", "-c", sql)
                    check(initialized.exitCode == 0) { "Owned local marker initialization failed" }
                }
                worker.environment("GAMEBRIDGE_RUN_DB_TESTS", (profile == "local-mock").toString())
                worker.environment("GAMEBRIDGE_RUN_AUTH_DB_TESTS", (profile == "sandbox").toString())
                worker.environment("GAMEBRIDGE_TEST_DB_URL", container.jdbcUrl)
                worker.environment("GAMEBRIDGE_TEST_DB_USER", container.username)
                worker.environment("GAMEBRIDGE_TEST_DB_PASSWORD", container.password)
                worker.environment("GAMEBRIDGE_MUTATE_LEDGER_TEST", (name == "tcLedgerMutation").toString())
            }
        }
    }
}
