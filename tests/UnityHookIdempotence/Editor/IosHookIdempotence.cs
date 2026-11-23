using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;

// Only used in a new isolated consumer, never in a user's project.
public static class IosHookIdempotence
{
    public static void Run()
    {
        var target = NamedBuildTarget.iOS;
        PlayerSettings.SetScriptingDefineSymbols(target, "GAMEBRIDGE_IOS_GOOGLE_AUTH_CALLBACK");
        BuildMockIosPlayer.Build();
        var output = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_IOS_OUTPUT");
        var type = Type.GetType("GameBridge.Editor.IosXcodeBuildHook, GameBridge.Editor") ?? throw new InvalidOperationException("HOOK_MISSING");
        var hook = type.GetMethod("OnPostprocessBuild", BindingFlags.Static | BindingFlags.NonPublic) ?? throw new InvalidOperationException("HOOK_METHOD_MISSING");
        var project = Path.Combine(output, "Unity-iPhone.xcodeproj/project.pbxproj");
        var framework = Path.Combine(output, "Frameworks/GameBridge/GameBridgeNative.xcframework");
        var controller = Path.Combine(output, "Classes/UnityAppController.mm");
        var scene = Path.Combine(output, "Classes/UI/UnityScene.mm");
        var source = File.ReadAllText(controller);
        var callback = source.IndexOf("GB_HandleAuthURL(", StringComparison.Ordinal);
        var unityUrl = source.IndexOf("UnitySetAbsoluteURL(", callback < 0 ? 0 : callback, StringComparison.Ordinal);
        if (callback < 0 || unityUrl < 0 || callback != source.LastIndexOf("GB_HandleAuthURL(", StringComparison.Ordinal))
            throw new InvalidOperationException("GOOGLE_CALLBACK_FORWARDING_MISSING_OR_DUPLICATED");
        if (File.Exists(scene))
        {
            var sceneSource = File.ReadAllText(scene);
            if (!sceneSource.Contains("GameBridgeConsumeGoogleSceneURL(_pendingURLContext.URL)") ||
                !sceneSource.Contains("if (GameBridgeConsumeGoogleSceneURL(url)) return;"))
                throw new InvalidOperationException("GOOGLE_SCENE_FORWARDING_MISSING");
        }
        var before = Digest(project, framework, controller, scene);
        hook.Invoke(null, new object[] { BuildTarget.iOS, output }); var once = Digest(project, framework, controller, scene);
        hook.Invoke(null, new object[] { BuildTarget.iOS, output }); var twice = Digest(project, framework, controller, scene);
        if (before != once || once != twice) throw new InvalidOperationException("HOOK_NOT_IDEMPOTENT");
        Debug.Log("GB_IOS_HOOK_REPEAT PASS");
    }
    private static string Digest(string project, string framework, string controller, string scene)
    {
        if (!File.Exists(project) || !Directory.Exists(framework)) throw new InvalidOperationException("HOOK_OUTPUT_MISSING");
        var files = Directory.GetFiles(framework, "*", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray();
        if (files.Length == 0) throw new InvalidOperationException("FRAMEWORK_EMPTY");
        using var sha = SHA256.Create();
        string Hash(string path) { using var stream = File.OpenRead(path); return BitConverter.ToString(sha.ComputeHash(stream)); }
        return Hash(project) + Hash(controller) + (File.Exists(scene) ? Hash(scene) : "") +
            string.Concat(files.Select(path => path.Substring(framework.Length) + ":" + Hash(path)));
    }
}
