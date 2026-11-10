plugins { `maven-publish`; id("com.android.library"); kotlin("android") }
android { namespace = "com.gamebridge.bridge"; compileSdk = 36
    publishing { singleVariant("release") }
    defaultConfig { minSdk = 26; consumerProguardFiles("consumer-rules.pro") }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
dependencies { implementation(project(":sdk-android")); implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1") }

afterEvaluate {
    publishing {
        publications { create<MavenPublication>("release") { from(components["release"]) } }
        repositories { maven { name = "staging"; url = uri(rootProject.layout.projectDirectory.dir("../artifacts/maven-repo")) } }
    }
}
