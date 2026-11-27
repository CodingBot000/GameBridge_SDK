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
        // IMGUI paints transparent controls over this frame's cleared background.
        var background = new GameObject("Screen Background").AddComponent<Camera>();
        background.clearFlags = CameraClearFlags.SolidColor;
        background.backgroundColor = new Color32(31, 31, 31, 255);
        background.cullingMask = 0;

        new GameObject("GameBridgeMockScenario").AddComponent<MockPlayerScenario>();
        const string scenePath = "Assets/GameBridgeMockScenario.unity";
        if (!EditorSceneManager.SaveScene(scene, scenePath)) throw new InvalidOperationException("scene save failed");
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.gamebridge.sdk.googleoauth.androidtest");
        var versionCode = Environment.GetEnvironmentVariable("GAMEBRIDGE_TEST_ANDROID_VERSION_CODE");
        if (versionCode != null)
        {
            if (!int.TryParse(versionCode, out var number) || number <= 0)
                throw new InvalidOperationException("GAMEBRIDGE_TEST_ANDROID_VERSION_CODE must be positive");
            PlayerSettings.Android.bundleVersionCode = number;
        }
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
        var result = BuildPipeline.BuildPlayer(new[] { scenePath }, output, BuildTarget.Android, BuildOptions.Development);
        if (result.summary.result != BuildResult.Succeeded) throw new InvalidOperationException("Android build failed: " + result.summary.result);
        Debug.Log("GB_MOCK_BUILD PASS");
    }
}
