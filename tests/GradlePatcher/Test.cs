using System;
using GameBridge.Editor;
class Test {
    static void Main() {
        string settings = "pluginManagement { repositories { google() } }\ndependencyResolutionManagement { repositories { google() /* } */ } }\n";
        string first = GradlePatcher.AddRepository(settings);
        if (first != GradlePatcher.AddRepository(first) || !first.Contains("${settingsDir}/gamebridge-maven") || !first.Contains("pluginManagement { repositories { google() } }")) throw new Exception("repository patch");
        string build = "// dependencies { wrong }\ndependencies { implementation 'example:thing:1' }\n";
        string patched = GradlePatcher.AddDependency(build);
        if (patched != GradlePatcher.AddDependency(patched) || !patched.Contains("example:thing:1")) throw new Exception("dependency patch");
        bool rejected = false;
        try { GradlePatcher.AddDependency("dependencies { } // GAMEBRIDGE BEGIN"); } catch (InvalidOperationException) { rejected = true; }
        if (!rejected) throw new Exception("partial marker accepted");
        rejected = false;
        try { GradlePatcher.AddRepository("repositories { google() }"); } catch (InvalidOperationException) { rejected = true; }
        if (!rejected) throw new Exception("unknown layout accepted");
        string temp = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "gamebridge-hook-" + Guid.NewGuid());
        string package = System.IO.Path.Combine(temp, "package"), export = System.IO.Path.Combine(temp, "export"), library = System.IO.Path.Combine(export, "unityLibrary");
        string repo = System.IO.Path.Combine(package, "Editor", "GameBridgeArtifacts~", "Android", "maven-repo", "com", "gamebridge", "sdk-unity-bridge", "0.1.0-dev");
        System.IO.Directory.CreateDirectory(repo); System.IO.Directory.CreateDirectory(library);
        System.IO.File.WriteAllText(System.IO.Path.Combine(repo, "sdk-unity-bridge-0.1.0-dev.pom"), "test-pom");
        System.IO.File.WriteAllText(System.IO.Path.Combine(export, "settings.gradle"), settings);
        System.IO.File.WriteAllText(System.IO.Path.Combine(library, "build.gradle"), build);
        UnityEditor.PackageManager.PackageInfo.Current = new UnityEditor.PackageManager.PackageInfo { resolvedPath = package };
        var hook = new AndroidGradleBuildHook(); hook.OnPostGenerateGradleAndroidProject(library);
        var settingsFirst = System.IO.File.ReadAllText(System.IO.Path.Combine(export, "settings.gradle"));
        var libraryFirst = System.IO.File.ReadAllText(System.IO.Path.Combine(library, "build.gradle"));
        hook.OnPostGenerateGradleAndroidProject(library);
        if (settingsFirst != System.IO.File.ReadAllText(System.IO.Path.Combine(export, "settings.gradle")) || libraryFirst != System.IO.File.ReadAllText(System.IO.Path.Combine(library, "build.gradle"))) throw new Exception("hook not idempotent");
        System.IO.File.WriteAllText(System.IO.Path.Combine(export, "gamebridge-maven", "com", "gamebridge", "sdk-unity-bridge", "0.1.0-dev", "sdk-unity-bridge-0.1.0-dev.pom"), "different");
        rejected = false;
        try { hook.OnPostGenerateGradleAndroidProject(library); } catch (UnityEditor.Build.BuildFailedException) { rejected = true; }
        if (!rejected) throw new Exception("changed repository accepted");
        string ios = System.IO.Path.Combine(package, "Editor", "GameBridgeArtifacts~", "iOS", "GameBridgeNative.xcframework");
        string iosExport = System.IO.Path.Combine(temp, "ios-export");
        System.IO.Directory.CreateDirectory(ios); System.IO.Directory.CreateDirectory(iosExport);
        System.IO.File.WriteAllText(System.IO.Path.Combine(ios, "Info.plist"), "test-plist");
        System.IO.File.WriteAllText(System.IO.Path.Combine(iosExport, "project.pbxproj"), "fixture");
        IosXcodeBuildHook.OnPostprocessBuild(UnityEditor.BuildTarget.iOS, iosExport);
        IosXcodeBuildHook.OnPostprocessBuild(UnityEditor.BuildTarget.iOS, iosExport);
        if (UnityEditor.iOS.Xcode.PBXProject.Files.Count != 1 || UnityEditor.iOS.Xcode.PBXProject.Links.Count != 1) throw new Exception("iOS reference duplicate");
        Console.WriteLine("Gradle patcher and stubbed hooks smoke: PASS");
    }
}
