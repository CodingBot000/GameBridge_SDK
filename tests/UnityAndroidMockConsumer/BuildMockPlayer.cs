using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class BuildMockPlayer
{
    // This creates assets only in the fresh, isolated consumer project.
    public static void Build()
    {
        var output = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_APK");
        if (string.IsNullOrEmpty(output) || !Path.IsPathRooted(output) || File.Exists(output))
            throw new InvalidOperationException("GAMEBRIDGE_UNITY_APK must be a new absolute path");
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        new GameObject("GameBridgeMockScenario").AddComponent<MockPlayerScenario>();
        const string scenePath = "Assets/GameBridgeMockScenario.unity";
        if (!EditorSceneManager.SaveScene(scene, scenePath)) throw new InvalidOperationException("scene save failed");
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.gamebridge.sdk.mockconsumer");
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        var result = BuildPipeline.BuildPlayer(new[] { scenePath }, output, BuildTarget.Android, BuildOptions.Development);
        if (result.summary.result != BuildResult.Succeeded) throw new InvalidOperationException("Android build failed: " + result.summary.result);
        Debug.Log("GB_MOCK_BUILD PASS");
    }
}
