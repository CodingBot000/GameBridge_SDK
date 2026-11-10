plugins { id("com.android.application"); kotlin("android") }
android {
    namespace = "com.gamebridge.consumer"
    compileSdk = 36
    defaultConfig { applicationId = "com.gamebridge.consumer"; minSdk = 26; targetSdk = 36 }
    buildTypes { release { isMinifyEnabled = true; proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro") } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    implementation("com.gamebridge:sdk-android:0.1.0-dev")
    implementation("com.gamebridge:sdk-unity-bridge:0.1.0-dev")
}
