using System;
using System.IO;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEngine;

// Test-only entry points, copied exclusively into an owned disposable consumer.
public static class GameBridgeGuiVerification
{
    [Serializable] public sealed class Config
    {
        public int schemaVersion;
        public string runId, sourceHead, projectRoot, expectedUnityVersion, scriptSha256, operation;
        public string outputPath, buildScriptSha256, adapterSha256, scenarioSha256, stagingManifestSha256, variant;
    }
    [Serializable] public sealed class ProbeReceipt
    {
        public int schemaVersion = 1, checksExecuted, editorPid;
        public string status, operation, runId, sourceHead, projectRoot, unityVersion, scriptSha256;
        public string method, assemblyName, startedUtc, finishedUtc, errorType, engineObjectName;
        public bool isBatchMode, engineObjectCreated, engineObjectDestroyed;
    }
    const string ConfigName = "GameBridgeGuiRun.json";

    public static string FileHash(string path)
    {
        using (var stream = File.OpenRead(path))
        using (var sha = SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
    public static Config ReadConfig(string operation)
    {
        var project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
        var config = JsonUtility.FromJson<Config>(File.ReadAllText(Path.Combine(project, ConfigName)));
        if (config == null || config.schemaVersion != 1 || config.operation != operation ||
            !Regex.IsMatch(config.runId ?? "", "^[0-9a-f]{32}$") ||
            !Regex.IsMatch(config.sourceHead ?? "", "^[0-9a-f]{40}$") ||
            !String.Equals(Path.GetFullPath(config.projectRoot), project, StringComparison.Ordinal) ||
            config.expectedUnityVersion != Application.unityVersion || Application.isBatchMode ||
            FileHash(Path.Combine(Application.dataPath, "Editor/GameBridgeGuiVerification.cs")) != config.scriptSha256)
            throw new InvalidOperationException("GUI verification identity/configuration mismatch");
        return config;
    }
    public static string ReceiptPath(Config config)
    {
        return Path.Combine(config.projectRoot, "GameBridgeGuiResults", config.runId + ".json");
    }
    public static void SaveReceipt(Config config, string json)
    {
        var path = ReceiptPath(config);
        Directory.CreateDirectory(Path.GetDirectoryName(path));
        using (var stream = new FileStream(path, FileMode.CreateNew, FileAccess.Write))
        using (var writer = new StreamWriter(stream)) writer.Write(json);
    }
    static void Check(bool value, ref int count)
    {
        count++;
        if (!value) throw new InvalidOperationException("GUI engine probe condition failed");
    }
    [MenuItem("GameBridge Verification/Run GUI Probe")]
    public static void RunProbe()
    {
        var config = ReadConfig("probe");
        if (File.Exists(ReceiptPath(config))) throw new InvalidOperationException("Receipt already exists; fresh nonce required");
        var result = new ProbeReceipt {
            status = "FAIL", operation = "probe", runId = config.runId, sourceHead = config.sourceHead,
            projectRoot = Path.GetFullPath(Path.Combine(Application.dataPath, "..")),
            unityVersion = Application.unityVersion, isBatchMode = Application.isBatchMode,
            scriptSha256 = FileHash(Path.Combine(Application.dataPath, "Editor/GameBridgeGuiVerification.cs")),
            method = "GameBridgeGuiVerification.RunProbe", assemblyName = typeof(GameBridgeGuiVerification).Assembly.GetName().Name,
            editorPid = System.Diagnostics.Process.GetCurrentProcess().Id, startedUtc = DateTime.UtcNow.ToString("O")
        };
        GameObject temporary = null;
        int checks = 0;
        try
        {
            Check(!Application.isBatchMode, ref checks);
            Check(!EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling, ref checks);
            Check(Application.unityVersion == config.expectedUnityVersion, ref checks);
            Check(!String.IsNullOrEmpty(AssetDatabase.AssetPathToGUID("Assets/Editor/GameBridgeGuiVerification.cs")), ref checks);
            temporary = new GameObject("GameBridgeGuiProbe-" + config.runId) { hideFlags = HideFlags.HideAndDontSave };
            result.engineObjectName = temporary.name;
            Check(result.engineObjectName == "GameBridgeGuiProbe-" + config.runId && temporary.activeSelf, ref checks);
            result.engineObjectCreated = true;
            temporary.transform.position = new Vector3(1, 2, 3);
            Check(temporary.GetComponent<Transform>() != null && temporary.transform.position == new Vector3(1, 2, 3), ref checks);
            UnityEngine.Object.DestroyImmediate(temporary);
            Check(temporary == null, ref checks);
            result.engineObjectDestroyed = true;
            result.status = "PASS";
        }
        catch (Exception error) { result.errorType = error.GetType().Name; }
        finally
        {
            if (temporary != null) UnityEngine.Object.DestroyImmediate(temporary);
            result.checksExecuted = checks; result.finishedUtc = DateTime.UtcNow.ToString("O");
            SaveReceipt(config, JsonUtility.ToJson(result, true));
        }
        if (result.status == "PASS") Debug.Log("GB_GUI_PROBE PASS " + config.runId);
        else Debug.LogError("GB_GUI_PROBE FAIL " + config.runId + " " + result.errorType);
    }
}
