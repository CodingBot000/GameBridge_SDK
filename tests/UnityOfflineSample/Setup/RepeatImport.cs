using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEditor;
using UnityEditor.PackageManager.UI;
using UnityEngine;

// Runs only in a newly created isolated consumer project.
public static class GameBridgeSampleRepeatImport
{
    private static string GuidFor(string path)
    {
        if (!File.Exists(path)) throw new InvalidOperationException("META_MISSING");
        var match = Regex.Match(File.ReadAllText(path), @"(?m)^guid: ([0-9a-f]{32})$");
        if (!match.Success) throw new InvalidOperationException("GUID_MISSING");
        return match.Groups[1].Value;
    }
    public static void Run()
    {
        var samples = Sample.FindByPackage("com.gamebridge.sdk", "0.1.0-dev").ToArray();
        foreach (var name in new[] { "Editor Offline Demo", "Native Mock and Sandbox Demo" })
        {
            var sample = samples.Single(item => item.displayName == name);
            if (!sample.isImported || !Directory.Exists(sample.importPath)) throw new InvalidOperationException("SAMPLE_NOT_IMPORTED");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var rootBefore = GuidFor(sample.importPath + ".meta");
            var paths = Directory.GetFiles(sample.importPath, "*.meta", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray();
            if (paths.Length == 0) throw new InvalidOperationException("SAMPLE_ASSETS_MISSING");
            var before = paths.Select(GuidFor).ToArray();
            if (!sample.Import(Sample.ImportOptions.OverridePreviousImports)) throw new InvalidOperationException("REIMPORT_FAILED");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var rootAfter = GuidFor(sample.importPath + ".meta");
            var afterPaths = Directory.GetFiles(sample.importPath, "*.meta", SearchOption.AllDirectories).OrderBy(path => path, StringComparer.Ordinal).ToArray();
            var internalStable = paths.SequenceEqual(afterPaths) && before.SequenceEqual(afterPaths.Select(GuidFor));
            Debug.Log("GB_SAMPLE_REIMPORT " + name + " ROOT=" + (rootBefore == rootAfter ? "STABLE" : "CHANGED") + " INTERNAL=" + (internalStable ? "STABLE" : "CHANGED"));
            if (rootBefore != rootAfter || !internalStable) throw new InvalidOperationException("REIMPORT_GUID_CHANGED");
        }
        Debug.Log("GB_SAMPLE_REIMPORT_COMPLETE");
    }
}
