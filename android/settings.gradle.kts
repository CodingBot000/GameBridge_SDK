pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }
rootProject.name = "GameBridgeAndroid"
include(":sdk-core", ":sdk-android", ":sdk-unity-bridge", ":sample-app")
