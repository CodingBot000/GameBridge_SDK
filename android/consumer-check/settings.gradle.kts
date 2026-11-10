pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { maven { url = System.getenv("GAMEBRIDGE_MAVEN_REPO")?.let { uri(it) } ?: uri("../../artifacts/maven-repo") }; google(); mavenCentral() }
}
rootProject.name = "GameBridgeConsumerCheck"
include(":app")
