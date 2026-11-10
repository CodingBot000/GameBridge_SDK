pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { maven { url = uri("../../artifacts/maven-repo") }; google(); mavenCentral() }
}
rootProject.name = "GameBridgeConsumerCheck"
include(":app")
