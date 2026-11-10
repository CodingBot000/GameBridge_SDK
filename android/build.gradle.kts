plugins {
    kotlin("jvm") version "2.1.20" apply false
    kotlin("android") version "2.1.20" apply false
    kotlin("plugin.serialization") version "2.1.20" apply false
    id("com.android.library") version "8.13.0" apply false
    id("com.android.application") version "8.13.0" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.20" apply false
}

subprojects {
    group = "com.gamebridge"
    version = "0.1.0-dev"
}
