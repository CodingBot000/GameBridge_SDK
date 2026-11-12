using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.Callbacks;
using UnityEditor.SceneManagement;
using UnityEditor.iOS.Xcode;
using UnityEngine;

public static class BuildMockIosPlayer
{
    public static void Build()
    {
        var output = Environment.GetEnvironmentVariable("GAMEBRIDGE_UNITY_IOS_OUTPUT");
        if (string.IsNullOrEmpty(output) || !Path.IsPathRooted(output) || Directory.Exists(output) || File.Exists(output))
            throw new InvalidOperationException("GAMEBRIDGE_UNITY_IOS_OUTPUT must be a new absolute path");
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        new GameObject("GameBridgeMockIosScenario").AddComponent<MockIosPlayerScenario>();
        const string scenePath = "Assets/GameBridgeMockIosScenario.unity";
        if (!EditorSceneManager.SaveScene(scene, scenePath)) throw new InvalidOperationException("scene save failed");
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.iOS, "com.gamebridge.sdk.mockiosconsumer");
        PlayerSettings.iOS.sdkVersion = iOSSdkVersion.SimulatorSDK;
        PlayerSettings.iOS.simulatorSdkArchitecture = AppleMobileArchitectureSimulator.ARM64;
        var result = BuildPipeline.BuildPlayer(new[] { scenePath }, output, BuildTarget.iOS, BuildOptions.Development);
        if (result.summary.result != BuildResult.Succeeded) throw new InvalidOperationException("iOS export failed: " + result.summary.result);
        Debug.Log("GB_IOS_MOCK_EXPORT PASS");
    }
    // Development-only consumer: allow only the loopback HTTP endpoint used by the test.
    [PostProcessBuild(200)]
    public static void ConfigureLocalMockAts(BuildTarget target, string output)
    {
        if (target != BuildTarget.iOS) return;
        var file = Path.Combine(output, "Info.plist"); var plist = new PlistDocument(); plist.ReadFromFile(file);
        var ats = plist.root.CreateDict("NSAppTransportSecurity");
        var domains = ats.CreateDict("NSExceptionDomains");
        domains.CreateDict("127.0.0.1").SetBoolean("NSExceptionAllowsInsecureHTTPLoads", true);
        plist.root.SetBoolean("UnityNotificationRequestAuthorizationOnAppLaunch", false);
        plist.root.SetBoolean("UnityNotificationRequestAuthorizationForRemoteNotificationsOnAppLaunch", false);
        plist.WriteToFile(file);
    }
}
