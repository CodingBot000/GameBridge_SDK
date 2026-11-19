using System;
using System.Linq;
using UnityEditor;
using UnityEditor.PackageManager.UI;
using UnityEngine;

public static class GameBridgeSampleImporter
{
    public static void Import()
    {
        var samples = Sample.FindByPackage("com.gamebridge.sdk", "0.1.0-dev").ToArray();
        foreach (var name in new[] { "Editor Offline Demo", "Native Mock and Sandbox Demo" })
        {
            var matches = samples.Where(sample => sample.displayName == name).ToArray();
            if (matches.Length != 1 || !matches[0].Import()) throw new InvalidOperationException("SAMPLE_IMPORT_FAILED: " + name);
            Debug.Log("GB_SAMPLE_IMPORT PASS " + name);
        }
        AssetDatabase.Refresh();
    }
}
