using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;

// Only used in a new isolated consumer, never in a user's project.
public static class IosHookIdempotence
{
    public static void Run()
    {
        BuildMockIosPlayer.Build();
        var output = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_IOS_OUTPUT");
        var type = Type.GetType("GameBridge.Editor.IosXcodeBuildHook, GameBridge.Editor") ?? throw new InvalidOperationException("HOOK_MISSING");
        var hook = type.GetMethod("OnPostprocessBuild", BindingFlags.Static | BindingFlags.NonPublic) ?? throw new InvalidOperationException("HOOK_METHOD_MISSING");
        var project = Path.Combine(output, "Unity-iPhone.xcodeproj/project.pbxproj");
        var framework = Path.Combine(output, "Frameworks/GameBridge/GameBridgeNative.xcframework");
        var before = Digest(project, framework);
        hook.Invoke(null, new object[] { BuildTarget.iOS, output }); var once = Digest(project, framework);
        hook.Invoke(null, new object[] { BuildTarget.iOS, output }); var twice = Digest(project, framework);
        if (before != once || once != twice) throw new InvalidOperationException("HOOK_NOT_IDEMPOTENT");
        Debug.Log("GB_IOS_HOOK_REPEAT PASS");
    }
    private static string Digest(string project, string framework)
    {
        if (!File.Exists(project) || !Directory.Exists(framework)) throw new InvalidOperationException("HOOK_OUTPUT_MISSING");
        var files = Directory.GetFiles(framework, "*", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray();
        if (files.Length == 0) throw new InvalidOperationException("FRAMEWORK_EMPTY");
        using var sha = SHA256.Create();
        string Hash(string path) { using var stream = File.OpenRead(path); return BitConverter.ToString(sha.ComputeHash(stream)); }
        return Hash(project) + string.Concat(files.Select(path => path.Substring(framework.Length) + ":" + Hash(path)));
    }
}
