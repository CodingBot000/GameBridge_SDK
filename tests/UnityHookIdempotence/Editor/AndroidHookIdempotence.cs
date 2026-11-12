using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

// Only used in a new isolated consumer, never in a user's project.
public static class AndroidHookIdempotence
{
    public static void Run()
    {
        var output = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_ANDROID_EXPORT");
        if (string.IsNullOrEmpty(output) || !Path.IsPathRooted(output) || Directory.Exists(output)) throw new InvalidOperationException("EXPORT_PATH_INVALID");
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        if (!EditorSceneManager.SaveScene(scene, "Assets/GameBridgeHookTest.unity")) throw new InvalidOperationException("SCENE_SAVE_FAILED");
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.gamebridge.sdk.hooktest");
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
        EditorUserBuildSettings.exportAsGoogleAndroidProject = true;
        var report = BuildPipeline.BuildPlayer(new[] { "Assets/GameBridgeHookTest.unity" }, output, BuildTarget.Android, BuildOptions.None);
        if (report.summary.result != BuildResult.Succeeded) throw new InvalidOperationException("ANDROID_EXPORT_FAILED");
        var type = Type.GetType("GameBridge.Editor.AndroidGradleBuildHook, GameBridge.Editor") ?? throw new InvalidOperationException("HOOK_MISSING");
        var hook = Activator.CreateInstance(type, true);
        var method = type.GetMethod("OnPostGenerateGradleAndroidProject", BindingFlags.Instance | BindingFlags.Public) ?? throw new InvalidOperationException("HOOK_METHOD_MISSING");
        var library = Path.Combine(output, "unityLibrary"); var before = Digest(output, library);
        method.Invoke(hook, new object[] { library }); var once = Digest(output, library);
        method.Invoke(hook, new object[] { library }); var twice = Digest(output, library);
        if (before != once || once != twice) throw new InvalidOperationException("HOOK_NOT_IDEMPOTENT");
        Debug.Log("GB_ANDROID_HOOK_REPEAT PASS");
    }
    private static string Digest(string output, string library)
    {
        var settings = Path.Combine(output, "settings.gradle"); var build = Path.Combine(library, "build.gradle"); var repo = Path.Combine(output, "gamebridge-maven");
        if (!File.Exists(settings) || !File.Exists(build) || !Directory.Exists(repo)) throw new InvalidOperationException("HOOK_OUTPUT_MISSING");
        var files = Directory.GetFiles(repo, "*", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray();
        if (files.Length == 0) throw new InvalidOperationException("MAVEN_EMPTY");
        using var sha = SHA256.Create();
        string Hash(string path) { using var stream = File.OpenRead(path); return BitConverter.ToString(sha.ComputeHash(stream)); }
        return Hash(settings) + Hash(build) + string.Concat(files.Select(path => path.Substring(repo.Length) + ":" + Hash(path)));
    }
}
