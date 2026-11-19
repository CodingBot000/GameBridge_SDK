using System;
using System.IO;
using UnityEditor;
using UnityEngine;

// Only in the fresh Android test consumer; the SDK and original builder are unchanged.
public static class GuiAndroidBuild
{
    [Serializable] public sealed class Receipt
    {
        public int schemaVersion = 1, editorPid, packageFilesVerified;
        public long artifactSize;
        public string status, operation, runId, sourceHead, projectRoot, unityVersion, scriptSha256;
        public string adapterSha256, buildScriptSha256, scenarioSha256, stagingManifestSha256, variant;
        public string method, startedUtc, finishedUtc, outputPath, artifactSha256, editorLogPath, errorType;
        public bool isBatchMode, originalBuilderReturned;
    }
    [MenuItem("GameBridge Verification/Switch Android Target")]
    public static void SwitchTarget()
    {
        GameBridgeGuiVerification.ReadConfig("android");
        if (!EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android))
            throw new InvalidOperationException("Android target switch failed");
        Debug.Log("GB_GUI_TARGET Android");
    }
    [MenuItem("GameBridge Verification/Build Android Mock", true)]
    public static bool CanBuild() => EditorUserBuildSettings.activeBuildTarget == BuildTarget.Android &&
        !EditorApplication.isCompiling && !EditorApplication.isPlayingOrWillChangePlaymode;

    static int CheckPackage(GameBridgeGuiVerification.Config config)
    {
        var manifest = Path.Combine(config.projectRoot, "GameBridgeStaging.SHA256SUMS");
        if (GameBridgeGuiVerification.FileHash(manifest) != config.stagingManifestSha256)
            throw new InvalidOperationException("Staging manifest changed");
        var root = Path.GetFullPath(Path.Combine(config.projectRoot, "Packages/com.gamebridge.sdk")) + Path.DirectorySeparatorChar;
        int count = 0;
        foreach (var line in File.ReadAllLines(manifest))
        {
            if (line.Length < 67 || line.Substring(64, 2) != "  ") throw new InvalidOperationException("Invalid package manifest");
            var relative = line.Substring(66);
            var file = Path.GetFullPath(Path.Combine(config.projectRoot, "Packages", relative));
            if (!file.StartsWith(root, StringComparison.Ordinal) ||
                GameBridgeGuiVerification.FileHash(file) != line.Substring(0, 64))
                throw new InvalidOperationException("Packaged SDK bytes changed");
            count++;
        }
        if (count != 147) throw new InvalidOperationException("Unexpected staged package file count");
        return count;
    }
    [MenuItem("GameBridge Verification/Build Android Mock")]
    public static void Build()
    {
        var c = GameBridgeGuiVerification.ReadConfig("android");
        var parent = Path.GetFullPath(Path.Combine(c.projectRoot, "..")) + Path.DirectorySeparatorChar;
        var output = Path.GetFullPath(c.outputPath);
        if (!CanBuild() || !Path.IsPathRooted(c.outputPath) || !output.StartsWith(parent, StringComparison.Ordinal) ||
            !output.EndsWith(".apk", StringComparison.Ordinal) || File.Exists(output) || Directory.Exists(output) ||
            File.Exists(GameBridgeGuiVerification.ReceiptPath(c))) throw new InvalidOperationException("Fresh owned Android GUI build required");
        var r = new Receipt { status = "FAIL", operation = "android", runId = c.runId, sourceHead = c.sourceHead,
            projectRoot = c.projectRoot, unityVersion = Application.unityVersion, isBatchMode = Application.isBatchMode,
            scriptSha256 = c.scriptSha256, adapterSha256 = c.adapterSha256, buildScriptSha256 = c.buildScriptSha256,
            scenarioSha256 = c.scenarioSha256, stagingManifestSha256 = c.stagingManifestSha256, variant = c.variant,
            method = "GuiAndroidBuild.Build", outputPath = output, editorLogPath = Application.consoleLogPath,
            editorPid = System.Diagnostics.Process.GetCurrentProcess().Id, startedUtc = DateTime.UtcNow.ToString("O") };
        string old = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_APK");
        try
        {
            if (GameBridgeGuiVerification.FileHash(Path.Combine(Application.dataPath, "Editor/GuiAndroidBuild.cs")) != c.adapterSha256 ||
                GameBridgeGuiVerification.FileHash(Path.Combine(Application.dataPath, "Editor/BuildMockPlayer.cs")) != c.buildScriptSha256 ||
                GameBridgeGuiVerification.FileHash(Path.Combine(Application.dataPath, "MockPlayerScenario.cs")) != c.scenarioSha256)
                throw new InvalidOperationException("GUI builder/scenario source changed");
            r.packageFilesVerified = CheckPackage(c);
            Debug.Log("GB_GUI_ANDROID_STARTED " + c.runId);
            // Explicit project-local non-secret configuration, not inherited shell state.
            Environment.SetEnvironmentVariable("GAMEBRIDGE_UNITY_APK", output);
            BuildMockPlayer.Build();
            r.originalBuilderReturned = true;
            r.artifactSize = new FileInfo(output).Length;
            if (r.artifactSize <= 0) throw new InvalidOperationException("APK missing or empty");
            r.artifactSha256 = GameBridgeGuiVerification.FileHash(output);
            r.status = "PASS";
        }
        catch (Exception error) { r.errorType = error.GetType().Name; Debug.LogException(error); }
        finally
        {
            Environment.SetEnvironmentVariable("GAMEBRIDGE_UNITY_APK", old);
            r.finishedUtc = DateTime.UtcNow.ToString("O");
            GameBridgeGuiVerification.SaveReceipt(c, JsonUtility.ToJson(r, true));
        }
        if (r.status == "PASS") Debug.Log("GB_GUI_ANDROID_PASS " + c.runId);
        else Debug.LogError("GB_GUI_ANDROID_FAIL " + c.runId + " " + r.errorType);
    }
}
