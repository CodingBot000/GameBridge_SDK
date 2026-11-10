import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins { kotlin("jvm"); kotlin("plugin.serialization"); `maven-publish` }
kotlin {
    jvmToolchain(21)
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}
java { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    testImplementation(kotlin("test"))
}
tasks.test { useJUnitPlatform() }
dependencies { testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.12.2") }

publishing {
    publications { create<MavenPublication>("release") { from(components["java"]) } }
    repositories { maven { name = "staging"; url = uri(rootProject.layout.projectDirectory.dir("../artifacts/maven-repo")) } }
}
