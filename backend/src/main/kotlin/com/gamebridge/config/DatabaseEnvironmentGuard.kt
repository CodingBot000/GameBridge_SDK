package com.gamebridge.config

import jakarta.annotation.PostConstruct
import org.springframework.boot.sql.init.dependency.DependsOnDatabaseInitialization
import org.springframework.core.env.Environment
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.stereotype.Component

/** A database belongs to exactly one provider profile; never silently reuse mock data. */
@Component
@DependsOnDatabaseInitialization
class DatabaseEnvironmentGuard(private val db: JdbcTemplate, private val environment: Environment) {
    @PostConstruct
    fun verify() {
        val profile = environment.activeProfiles.filter { it in setOf("local-mock", "sandbox", "production") }.singleOrNull()
            ?: error("CONFIG_REQUIRED: exactly one environment profile")
        db.update("INSERT INTO gamebridge_environment (singleton,profile) VALUES (true,?) ON CONFLICT (singleton) DO NOTHING", profile)
        val actual = db.queryForObject("SELECT profile FROM gamebridge_environment WHERE singleton=true", String::class.java)
        check(actual == profile) { "CONFIG_REQUIRED: database belongs to a different environment profile" }
    }
}

@org.springframework.context.annotation.Configuration
class FlywayEnvironmentPolicy {
    @org.springframework.context.annotation.Bean
    fun environmentMigrationStrategy(environment: Environment): org.springframework.boot.autoconfigure.flyway.FlywayMigrationStrategy =
        org.springframework.boot.autoconfigure.flyway.FlywayMigrationStrategy { flyway ->
            val profile = environment.activeProfiles.filter { it in setOf("local-mock", "sandbox", "production") }.singleOrNull()
                ?: error("CONFIG_REQUIRED: exactly one environment profile")
            flyway.configuration.dataSource.connection.use { connection ->
                connection.prepareStatement("SELECT to_regclass('public.gamebridge_environment') IS NOT NULL").use { statement ->
                    statement.executeQuery().use { result ->
                        result.next()
                        if (result.getBoolean(1)) {
                            connection.prepareStatement("SELECT profile FROM gamebridge_environment WHERE singleton=true").use { check ->
                                check.executeQuery().use { marker ->
                                    if (marker.next()) check(marker.getString(1) == profile) { "CONFIG_REQUIRED: database belongs to a different environment profile" }
                                }
                            }
                        } else {
                            connection.prepareStatement("SELECT to_regclass('public.flyway_schema_history') IS NOT NULL").use { checkLegacy ->
                                checkLegacy.executeQuery().use { legacy ->
                                    legacy.next()
                                    check(!legacy.getBoolean(1)) { "CONFIG_REQUIRED: existing database has no environment marker" }
                                }
                            }
                        }
                    }
                }
            }
            flyway.migrate()
        }
}
