#if UNITY_ANDROID
using System.IO;
using UnityEditor.Android;
using UnityEditor.Build;

// Test-only host dependency; no Firebase project, credentials or remote sends.
internal sealed class PermissionFirebaseDependency : IPostGenerateGradleAndroidProject
{
    public int callbackOrder => 1000;
    public void OnPostGenerateGradleAndroidProject(string path)
    {
        var file = Path.Combine(path, "build.gradle");
        if (!File.Exists(file)) throw new BuildFailedException("Unity library Gradle file missing");
        File.AppendAllText(file, "\ndependencies { implementation 'com.google.firebase:firebase-messaging:26.0.1' }\n");
    }
}
#endif
