plugins { id("com.android.application"); kotlin("android") }
android {
    namespace = "com.gamebridge.consumer"
    compileSdk = 36
    defaultConfig { applicationId = "com.gamebridge.consumer"; minSdk = 26; targetSdk = 36 }
    buildTypes { release { isMinifyEnabled = true; proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro") } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
val sdkVersion = providers.environmentVariable("GAMEBRIDGE_SDK_VERSION").orElse(
    providers.provider { rootProject.file("../../VERSION").readText().trim() }
)
dependencies {
    implementation("com.gamebridge:sdk-android:${sdkVersion.get()}")
    implementation("com.gamebridge:sdk-unity-bridge:${sdkVersion.get()}")
}
