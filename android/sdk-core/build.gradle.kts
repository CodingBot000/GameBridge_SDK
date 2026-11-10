import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins { kotlin("jvm") }
kotlin {
    jvmToolchain(21)
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}
java { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
dependencies { testImplementation(kotlin("test")) }
tasks.test { useJUnitPlatform() }
dependencies { testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.12.2") }
