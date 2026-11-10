plugins { `maven-publish`; id("com.android.library"); kotlin("android"); kotlin("plugin.serialization") }
android { namespace = "com.gamebridge.sdk"; compileSdk = 36
    publishing { singleVariant("release") }
    defaultConfig { minSdk = 26 }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    api(project(":sdk-core"))
    implementation("androidx.credentials:credentials:1.6.0")
    implementation("androidx.credentials:credentials-play-services-auth:1.6.0")
    implementation("com.google.android.libraries.identity.googleid:googleid:1.1.1")
    implementation("com.android.billingclient:billing:9.1.0")
    compileOnly("com.google.firebase:firebase-messaging:26.0.1")
    api("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.2")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1")
    testImplementation(kotlin("test"))
    testImplementation("com.google.firebase:firebase-messaging:26.0.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.12.2")
}
tasks.withType<Test>().configureEach { useJUnitPlatform() }

afterEvaluate {
    publishing {
        publications { create<MavenPublication>("release") { from(components["release"]) } }
        repositories { maven { name = "staging"; url = uri(rootProject.layout.projectDirectory.dir("../artifacts/maven-repo")) } }
    }
}
