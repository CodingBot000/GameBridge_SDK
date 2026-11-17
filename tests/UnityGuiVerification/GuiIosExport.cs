using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;

public static class GuiIosExport
{
    [Serializable] public sealed class Receipt
    {
        public int schemaVersion = 1, editorPid, packageFilesVerified, artifactFileCount;
        public string status, operation, runId, sourceHead, projectRoot, unityVersion, scriptSha256;
        public string adapterSha256, buildScriptSha256, scenarioSha256, stagingManifestSha256, variant;
        public string method, startedUtc, finishedUtc, outputPath, artifactSha256, pbxprojSha256, editorLogPath, errorType;
        public bool isBatchMode, originalBuilderReturned;
    }
    [MenuItem("GameBridge Verification/Switch iOS Target")]
    public static void SwitchTarget()
    {
        GameBridgeGuiVerification.ReadConfig("ios");
        if (!EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.iOS, BuildTarget.iOS))
            throw new InvalidOperationException("iOS target switch failed");
        Debug.Log("GB_GUI_TARGET iOS");
    }
    [MenuItem("GameBridge Verification/Export iOS Mock", true)]
    public static bool CanExport() => EditorUserBuildSettings.activeBuildTarget == BuildTarget.iOS &&
        !EditorApplication.isCompiling && !EditorApplication.isPlayingOrWillChangePlaymode;
    static string TreeHash(string root, out int count)
    {
        var files = Directory.GetFiles(root, "*", SearchOption.AllDirectories)
            .OrderBy(p => p.Substring(root.Length + 1).Replace('\\','/'), StringComparer.Ordinal).ToArray();
        using (var sha = SHA256.Create())
        {
            foreach (var file in files)
            {
                if ((File.GetAttributes(file) & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("Export symlink not allowed");
                var line = file.Substring(root.Length + 1).Replace('\\','/') + "\0" + GameBridgeGuiVerification.FileHash(file) + "\n";
                var bytes = Encoding.UTF8.GetBytes(line); sha.TransformBlock(bytes, 0, bytes.Length, bytes, 0);
            }
            sha.TransformFinalBlock(new byte[0], 0, 0); count = files.Length;
            return BitConverter.ToString(sha.Hash).Replace("-", "").ToLowerInvariant();
        }
    }
    static int PackageCheck(GameBridgeGuiVerification.Config c)
    {
        var manifest = Path.Combine(c.projectRoot, "GameBridgeStaging.SHA256SUMS");
        if (GameBridgeGuiVerification.FileHash(manifest) != c.stagingManifestSha256) throw new InvalidOperationException("Staging manifest changed");
        var root = Path.GetFullPath(Path.Combine(c.projectRoot,"Packages/com.gamebridge.sdk")) + Path.DirectorySeparatorChar;
        int count = 0;
        foreach (var line in File.ReadAllLines(manifest))
        {
            if (line.Length < 67 || line.Substring(64,2) != "  ") throw new InvalidOperationException("Package manifest invalid");
            var file = Path.GetFullPath(Path.Combine(c.projectRoot,"Packages",line.Substring(66)));
            if (!file.StartsWith(root,StringComparison.Ordinal) || GameBridgeGuiVerification.FileHash(file) != line.Substring(0,64))
                throw new InvalidOperationException("Package SDK bytes changed");
            count++;
        }
        if (count != 147) throw new InvalidOperationException("Package file count changed"); return count;
    }
    [MenuItem("GameBridge Verification/Export iOS Mock")]
    public static void Export()
    {
        var c = GameBridgeGuiVerification.ReadConfig("ios");
        var output = Path.GetFullPath(c.outputPath);
        var parent = Path.GetFullPath(Path.Combine(c.projectRoot,"..")) + Path.DirectorySeparatorChar;
        if (!CanExport() || !Path.IsPathRooted(c.outputPath) || !output.StartsWith(parent,StringComparison.Ordinal) ||
            Directory.Exists(output) || File.Exists(output) || File.Exists(GameBridgeGuiVerification.ReceiptPath(c)))
            throw new InvalidOperationException("Fresh owned GUI iOS export required");
        var r = new Receipt { status="FAIL",operation="ios",runId=c.runId,sourceHead=c.sourceHead,projectRoot=c.projectRoot,
            unityVersion=Application.unityVersion,isBatchMode=Application.isBatchMode,scriptSha256=c.scriptSha256,
            adapterSha256=c.adapterSha256,buildScriptSha256=c.buildScriptSha256,scenarioSha256=c.scenarioSha256,
            stagingManifestSha256=c.stagingManifestSha256,variant=c.variant,method="GuiIosExport.Export",outputPath=output,
            editorLogPath=Application.consoleLogPath,editorPid=System.Diagnostics.Process.GetCurrentProcess().Id,startedUtc=DateTime.UtcNow.ToString("O") };
        string old = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_IOS_OUTPUT");
        try
        {
            if (GameBridgeGuiVerification.FileHash(Path.Combine(Application.dataPath,"Editor/GuiIosExport.cs")) != c.adapterSha256 ||
                GameBridgeGuiVerification.FileHash(Path.Combine(Application.dataPath,"Editor/BuildMockIosPlayer.cs")) != c.buildScriptSha256 ||
                GameBridgeGuiVerification.FileHash(Path.Combine(Application.dataPath,"MockIosPlayerScenario.cs")) != c.scenarioSha256)
                throw new InvalidOperationException("GUI iOS helper/scenario source changed");
            r.packageFilesVerified = PackageCheck(c);
            Debug.Log("GB_GUI_IOS_STARTED " + c.runId);
            Environment.SetEnvironmentVariable("GAMEBRIDGE_UNITY_IOS_OUTPUT",output);
#if UNITY_IOS
            BuildMockIosPlayer.Build();
#else
            throw new InvalidOperationException("iOS platform compilation required");
#endif
            r.originalBuilderReturned = true;
            r.pbxprojSha256 = GameBridgeGuiVerification.FileHash(Path.Combine(output,"Unity-iPhone.xcodeproj/project.pbxproj"));
            r.artifactSha256 = TreeHash(output,out r.artifactFileCount); r.status="PASS";
        }
        catch (Exception error) { r.errorType=error.GetType().Name; Debug.LogException(error); }
        finally
        {
            Environment.SetEnvironmentVariable("GAMEBRIDGE_UNITY_IOS_OUTPUT",old); r.finishedUtc=DateTime.UtcNow.ToString("O");
            GameBridgeGuiVerification.SaveReceipt(c,JsonUtility.ToJson(r,true));
        }
        if (r.status=="PASS") Debug.Log("GB_GUI_IOS_PASS " + c.runId);
        else Debug.LogError("GB_GUI_IOS_FAIL " + c.runId + " " + r.errorType);
    }
}
