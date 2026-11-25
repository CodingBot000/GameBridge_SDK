using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using UnityEditor.Build;
using UnityEditor.iOS.Xcode;

class Program
{
    const string FacebookUrl = "https://github.com/facebook/facebook-ios-sdk";
    const string GoogleUrl = "https://github.com/google/GoogleSignIn-iOS";
    const string AppTarget = "000000000000000000000003", Framework = "000000000000000000000004";
    static int checks;
    static void Check(bool value, string message) { checks++; if (!value) throw new Exception(message); }
    static PBXProject Fixture()
    {
        var p = new PBXProject();
        p.ReadFromString(@"// !$*UTF8*$!
{
 archiveVersion = 1; classes = {}; objectVersion = 56;
 objects = {
  000000000000000000000001 = { isa = PBXProject; mainGroup = 000000000000000000000002; productRefGroup = 000000000000000000000002; buildConfigurationList = 000000000000000000000007; targets = (000000000000000000000003,000000000000000000000004,); };
  000000000000000000000002 = { isa = PBXGroup; children = (); sourceTree = ""<group>""; };
  000000000000000000000003 = { isa = PBXNativeTarget; name = ""Unity-iPhone""; productName = project; productType = ""com.apple.product-type.application""; buildConfigurationList = 000000000000000000000007; buildPhases = (000000000000000000000005,); dependencies = (); };
  000000000000000000000004 = { isa = PBXNativeTarget; name = UnityFramework; productName = UnityFramework; productType = ""com.apple.product-type.framework""; buildConfigurationList = 000000000000000000000007; buildPhases = (000000000000000000000006,); dependencies = (); };
  000000000000000000000005 = { isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0; };
  000000000000000000000006 = { isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0; };
  000000000000000000000007 = { isa = XCConfigurationList; buildConfigurations = (000000000000000000000008,); defaultConfigurationName = Debug; };
  000000000000000000000008 = { isa = XCBuildConfiguration; name = Debug; buildSettings = { HOST_SETTING = keep; LD_RUNPATH_SEARCH_PATHS = ""$(inherited) @executable_path/Frameworks""; }; };
 }; rootObject = 000000000000000000000001;
}");
        return p;
    }
    static void Apply(string directory, string path, bool callback, Action<string> afterWrite = null)
    {
        string source = Directory.CreateDirectory(Path.Combine(directory, "fixture.xcframework")).FullName;
        File.WriteAllText(Path.Combine(source, "Info.plist"), "<plist/>");
        GameBridge.Editor.IosXcodeBuildHook.ApplyExport(directory, path, source, callback, false, afterWrite);
    }
    static void ApplyCallback(string directory)
    {
        using var files = new GameBridge.Editor.IosExportFiles(directory, Path.Combine(directory, "project.pbxproj"));
        GameBridge.Editor.IosXcodeBuildHook.PlanGoogleCallback(directory, files);
        files.Commit();
    }
    static string Configure(PBXProject p, string directory)
    {
        string path = Path.Combine(directory, "project.pbxproj"); p.WriteToFile(path);
        Apply(directory, path, false);
        p.ReadFromFile(path); return p.WriteToString();
    }
    // Independent oracle: Apple's OpenStep parser, not the hook's text reader.
    static JsonDocument Graph(string text, string directory)
    {
        string path = Path.Combine(directory, "inspect.pbxproj"); File.WriteAllText(path, text);
        var info = new ProcessStartInfo("/usr/bin/plutil") { RedirectStandardOutput = true, RedirectStandardError = true };
        foreach (var arg in new[] { "-convert", "json", "-o", "-", path }) info.ArgumentList.Add(arg);
        using (var process = Process.Start(info))
        {
            string json = process.StandardOutput.ReadToEnd(), error = process.StandardError.ReadToEnd(); process.WaitForExit();
            Check(process.ExitCode == 0, "Apple PBX parser: " + error); return JsonDocument.Parse(json);
        }
    }
    static void AssertProduct(JsonElement objects, string target, string name, string package)
    {
        var products = objects.GetProperty(target).GetProperty("packageProductDependencies").EnumerateArray()
            .Select(x => x.GetString()).Where(id => objects.GetProperty(id).GetProperty("productName").GetString() == name).ToArray();
        Check(products.Length == 1, target + " must own exactly one " + name);
        Check(objects.GetProperty(products[0]).GetProperty("package").GetString() == package, "package identity");
        var phase = objects.GetProperty(target).GetProperty("buildPhases").EnumerateArray().Select(x => objects.GetProperty(x.GetString()))
            .Single(x => x.GetProperty("isa").GetString() == "PBXFrameworksBuildPhase");
        var links = phase.GetProperty("files").EnumerateArray().Select(x => objects.GetProperty(x.GetString()))
            .Where(x => x.TryGetProperty("productRef", out var id) && id.GetString() == products[0]).ToArray();
        Check(links.Length == 1 && !links[0].ToString().Contains("Weak"), name + " must be strongly linked once");
    }
    static void MustFail(Action action, string label, string expected)
    {
        bool failed = false; try { action(); } catch (BuildFailedException e) { Check(e.Message.Contains(expected), "wrong failure: " + label + " / " + e.Message); failed = true; }
        Check(failed, "explicit failure required: " + label);
    }
    static void TestNewExport(string dir)
    {
        var p = Fixture(); string relative = "Frameworks/GameBridge/GameBridgeNative.xcframework";
        string native = p.AddFile(relative, relative, PBXSourceTree.Source); p.AddFileToBuild(Framework, native);
        p.AddFrameworkToProject(AppTarget, "StoreKit.framework", false);
        string once = Configure(p, dir), twice = Configure(p, dir); Check(once == twice, "second hook invocation changed project");
        var reopened = new PBXProject(); reopened.ReadFromString(twice); Check(twice == Configure(reopened, dir), "reload idempotence");
        using (var doc = Graph(twice, dir))
        {
            var objects = doc.RootElement.GetProperty("objects");
            string fb = File.ReadAllText(Path.Combine(dir, "GameBridgeFacebookPackage.txt")).Trim();
            string google = File.ReadAllText(Path.Combine(dir, "GameBridgeGooglePackage.txt")).Trim();
            AssertProduct(objects, Framework, "FacebookLogin", fb); AssertProduct(objects, AppTarget, "FacebookLogin", fb);
            AssertProduct(objects, Framework, "GoogleSignIn", google);
            Check(objects.GetProperty(fb).GetProperty("requirement").GetProperty("version").GetString() == "18.1.1", "Meta pin");
            Check(objects.GetProperty(google).GetProperty("requirement").GetProperty("version").GetString() == "9.2.0", "Google pin");
            Check(objects.EnumerateObject().Count(x => x.Value.GetProperty("isa").GetString() == "XCRemoteSwiftPackageReference") == 2, "duplicate package reference");
            Check(objects.EnumerateObject().Count(x => x.Value.GetProperty("isa").GetString() == "PBXBuildFile" && x.Value.TryGetProperty("fileRef", out var f) && f.GetString() == native) == 1, "static Native link changed");
            Check(!objects.EnumerateObject().Any(x => x.Value.GetProperty("isa").GetString() == "PBXCopyFilesBuildPhase"), "static Native must not be embedded");
        }
        Check(p.ContainsFramework(AppTarget, "StoreKit.framework"), "Host framework lost");
        Check(p.GetBuildPropertyForAnyConfig(AppTarget, "HOST_SETTING") == "keep", "Host build setting lost");
        Check(p.GetBuildPropertyForAnyConfig(AppTarget, "LD_RUNPATH_SEARCH_PATHS").Contains("@executable_path/Frameworks"), "Host runpath lost");
    }
    static void TestUpgradeAndErrors(string dir)
    {
        var p = Fixture();
        string fb = p.AddRemotePackageReferenceAtVersion(FacebookUrl, "18.1.1");
        string google = p.AddRemotePackageReferenceAtVersion(GoogleUrl, "9.2.0");
        p.AddRemotePackageFrameworkToProject(Framework, "FacebookLogin", fb, false);
        p.AddRemotePackageFrameworkToProject(Framework, "GoogleSignIn", google, false);
        File.WriteAllText(Path.Combine(dir, "GameBridgeFacebookPackage.txt"), fb); File.WriteAllText(Path.Combine(dir, "GameBridgeGooglePackage.txt"), google);
        string upgraded = Configure(p, dir); Check(upgraded == Configure(p, dir), "legacy export upgrade must stabilize");
        using (var doc = Graph(upgraded, dir)) AssertProduct(doc.RootElement.GetProperty("objects"), AppTarget, "FacebookLogin", fb);
        string valid = upgraded;
        foreach (string version in new[] { "18.2.0", "9.3.0" })
        {
            var bad = new PBXProject(); bad.ReadFromString(valid.Replace(version == "18.2.0" ? "18.1.1" : "9.2.0", version));
            MustFail(() => Configure(bad, dir), "wrong version " + version, version == "18.2.0" ? "Facebook SPM ownership/version" : "Google SPM ownership/version");
        }
        File.WriteAllText(Path.Combine(dir, "GameBridgeFacebookPackage.txt"), "FFFFFFFFFFFFFFFFFFFFFFFF");
        MustFail(() => Configure(p, dir), "missing owned package", "dependency object is missing"); File.WriteAllText(Path.Combine(dir, "GameBridgeFacebookPackage.txt"), fb);
        var weak = Fixture(); string wf = weak.AddRemotePackageReferenceAtVersion(FacebookUrl, "18.1.1");
        weak.AddRemotePackageFrameworkToProject(AppTarget, "FacebookLogin", wf, true);
        File.WriteAllText(Path.Combine(dir, "GameBridgeFacebookPackage.txt"), wf); File.Delete(Path.Combine(dir, "GameBridgeGooglePackage.txt"));
        MustFail(() => Configure(weak, dir), "weak dependency", "strong framework link");
        var missingTarget = new PBXProject(); missingTarget.ReadFromString(Fixture().WriteToString().Replace("name = \"Unity-iPhone\";", "name = AnotherApp;"));
        Check(string.IsNullOrEmpty(missingTarget.GetUnityMainTargetGuid()), "missing-target fixture");
        MustFail(() => Configure(missingTarget, dir), "missing Unity app target", "requires the Unity app");
        string foreign = Path.Combine(dir, "foreign"); Directory.CreateDirectory(foreign);
        var host = Fixture(); host.AddRemotePackageReferenceAtVersion(FacebookUrl, "18.1.1");
        MustFail(() => Configure(host, foreign), "Host-owned Facebook package", "Host Facebook SPM configuration exists");
        Check(!File.Exists(Path.Combine(foreign, "GameBridgeFacebookPackage.txt")), "foreign Host package must not be claimed");

    }
    static void TestRetryAfterInvalidHost(string dir)
    {
        var classes = Directory.CreateDirectory(Path.Combine(dir, "Classes")).FullName;
        string pbx = Path.Combine(dir, "project.pbxproj"), host = Path.Combine(classes, "UnityAppController.mm");
        Fixture().WriteToFile(pbx);
        string original = File.ReadAllText(pbx);
        File.WriteAllText(host, "invalid host");
        MustFail(() => Apply(dir, pbx, true), "invalid host", "requires one stock Unity openURL handler");
        Check(original == File.ReadAllText(pbx), "invalid host changed PBX");
        Check(Directory.GetFiles(dir, "GameBridge*Package.txt").Length == 0, "invalid host left orphan package markers");
        File.WriteAllText(host, StockHost);
        Apply(dir, pbx, true);
        AssertConfiguredExport(dir);
    }
    static void AssertConfiguredExport(string dir)
    {
        string pbx = File.ReadAllText(Path.Combine(dir, "project.pbxproj"));
        using var graph = Graph(pbx, dir);
        var objects = graph.RootElement.GetProperty("objects");
        string google = File.ReadAllText(Path.Combine(dir, "GameBridgeGooglePackage.txt"));
        string facebook = File.ReadAllText(Path.Combine(dir, "GameBridgeFacebookPackage.txt"));
        AssertProduct(objects, Framework, "GoogleSignIn", google);
        AssertProduct(objects, AppTarget, "FacebookLogin", facebook);
        AssertProduct(objects, Framework, "FacebookLogin", facebook);
    }
    private const string StockHost = "- (BOOL)application:(UIApplication*)app openURL:(NSURL*)url options:(NSDictionary<NSString*, id>*)options\n{\n    return YES;\n}\n";
    private static string PrepareExport(string dir)
    {
        Directory.CreateDirectory(Path.Combine(dir, "Classes"));
        File.WriteAllText(Path.Combine(dir, "Classes/UnityAppController.mm"), StockHost);
        string pbx = Path.Combine(dir, "project.pbxproj");
        Fixture().WriteToFile(pbx);
        return pbx;
    }
    private static void TestInterruptedExports(string root)
    {
        string clean = Path.Combine(root, "clean"), cleanPbx = PrepareExport(clean);
        Apply(clean, cleanPbx, true);
        AssertConfiguredExport(clean);
        string expectedHost = File.ReadAllText(Path.Combine(clean, "Classes/UnityAppController.mm"));
        // PBX, AppController, Google marker and Facebook marker are all changed.
        for (int stopAfter = 1; stopAfter <= 4; stopAfter++)
        {
            string dir = Path.Combine(root, "interrupt-" + stopAfter);
            string pbx = PrepareExport(dir), host = Path.Combine(dir, "Classes/UnityAppController.mm");
            int writes = 0;
            try
            {
                Apply(dir, pbx, true, path => { if (++writes == stopAfter) throw new IOException("simulated interruption"); });
                throw new Exception("fault injection did not reach the target write");
            }
            catch (IOException e) when (e.Message == "simulated interruption") { }
            if (stopAfter == 1)
            {
                string partialPBX = File.ReadAllText(pbx);
                File.WriteAllText(host, StockHost + "// host edit after interruption");
                MustFail(() => Apply(dir, pbx, true), "preserve concurrent Host edit", host);
                Check(File.ReadAllText(host).EndsWith("// host edit after interruption"), "Host edit overwritten");
                Check(File.ReadAllText(pbx) == partialPBX && !File.Exists(Path.Combine(dir, "GameBridgeGooglePackage.txt")), "conflict caused further writes");
                File.WriteAllText(host, StockHost);
            }
            Apply(dir, pbx, true);
            AssertConfiguredExport(dir);
            Check(File.ReadAllText(host) == expectedHost, "recovery differs from clean export");
            string saved = File.ReadAllText(pbx);
            Apply(dir, pbx, true, _ => throw new Exception("idempotent run wrote a file"));
            Check(File.ReadAllText(pbx) == saved, "repeat changed recovered PBX");
        }

        string legacy = Path.Combine(root, "legacy-orphans"), legacyPbx = PrepareExport(legacy);
        File.WriteAllText(Path.Combine(legacy, "GameBridgeGooglePackage.txt"), "DEADBEEFDEADBEEFDEADBEEF");
        File.WriteAllText(Path.Combine(legacy, "GameBridgeFacebookPackage.txt"), "CAFEBABECAFEBABECAFEBABE");
        Apply(legacy, legacyPbx, true);
        AssertConfiguredExport(legacy);
    }

    static void TestGoogleCallback(string dir)
    {
        string classes = Path.Combine(dir, "Classes");
        Directory.CreateDirectory(classes);
        string path = Path.Combine(classes, "UnityAppController.mm");
        Action apply = () => ApplyCallback(dir);
        MustFail(apply, "missing controller", "requires the exported UnityAppController.mm");
        const string selector = "- (BOOL)application:(UIApplication*)app openURL:(NSURL*)url options:(NSDictionary<NSString*, id>*)options";
        const string host = "    UnitySetAbsoluteURL(url.absoluteString.UTF8String);\n    return YES;\n}\n";
        string unmodified = selector + "\n{\n" + host;
        File.WriteAllText(path, "custom controller");
        MustFail(apply, "unsupported callback", "requires one stock Unity openURL handler");
        File.WriteAllText(path, unmodified + unmodified);
        MustFail(apply, "duplicate callback", "requires one stock Unity openURL handler");
        File.WriteAllText(path, unmodified.Replace(host, "    GB_HandleAuthURL(bytes, length);\n" + host));
        MustFail(apply, "existing host forwarding", "conflicts with existing or modified Host forwarding");

        foreach (string newline in new[] { "\n", "\r\n" })
        {
            string source = ("// Existing Host settings\n" + unmodified).Replace("\n", newline);
            File.WriteAllText(path, source);
            apply();
            string once = File.ReadAllText(path);
            int bridge = once.IndexOf("GB_HandleAuthURL(", StringComparison.Ordinal);
            int unity = once.IndexOf("UnitySetAbsoluteURL(", StringComparison.Ordinal);
            Check(bridge >= 0 && unity > bridge && bridge == once.LastIndexOf("GB_HandleAuthURL(", StringComparison.Ordinal), "native forwarding must precede Unity exactly once");
            Check(once.EndsWith(host.Replace("\n", newline), StringComparison.Ordinal), "unrecognized URL must retain original host path");
            string between = once.Substring(bridge, unity - bridge);
            Check(between.Contains("return YES;"), "Google callback must return before the Unity URL event");
            apply();
            Check(once == File.ReadAllText(path), "repeat must preserve controller bytes");
            string damaged = once.Replace("GB_HandleAuthURL(", "RemovedCallback(");
            File.WriteAllText(path, damaged);
            MustFail(apply, "damaged forwarding", "conflicts with existing or modified Host forwarding");
            Check(File.ReadAllText(path) == damaged, "conflict must preserve host source");
        }
    }
    static void Main(string[] args)
    {
        string root = Path.Combine(Path.GetTempPath(), "gamebridge-ios-hook-" + Guid.NewGuid().ToString("N")); Directory.CreateDirectory(root);
        string fresh = Path.Combine(root, "fresh"), upgrade = Path.Combine(root, "upgrade"); Directory.CreateDirectory(fresh); Directory.CreateDirectory(upgrade);
        TestRetryAfterInvalidHost(Path.Combine(root, "retry"));
        TestInterruptedExports(root);
        TestNewExport(fresh); TestUpgradeAndErrors(upgrade); TestGoogleCallback(fresh); TestGoogleSceneCallback(fresh);
        string initial = "<?xml version=\"1.0\"?><plist version=\"1.0\"><dict><key>Existing</key><string>keep</string></dict></plist>";
        string first = GameBridge.Editor.IosXcodeBuildHook.EnableXcodeStoreKitHistory(initial), second = GameBridge.Editor.IosXcodeBuildHook.EnableXcodeStoreKitHistory(first);
        Check(first == second && second.Contains("keep"), "StoreKit plist idempotence/Host preservation");
        Console.WriteLine("Unity iOS Hook PASS: " + checks + " PBX and URL callback checks; fixtures " + root);
    }
    static void TestGoogleSceneCallback(string directory)
    {
        string classes = Path.Combine(directory, "Classes");
        string controller = Path.Combine(classes, "UnityAppController.mm");
        File.WriteAllText(controller, "- (BOOL)application:(UIApplication*)app openURL:(NSURL*)url options:(NSDictionary<NSString*, id>*)options\n{\n    return YES;\n}\n");
        string ui = Path.Combine(classes, "UI");
        Directory.CreateDirectory(ui);
        string scene = Path.Combine(ui, "UnityScene.mm");
        File.WriteAllText(Path.Combine(directory, "Info.plist"), "<string>UnityScene</string>");
        Action apply = () => ApplyCallback(directory);
        MustFail(apply, "missing Unity scene", "requires the exported UnityScene.mm");
        const string original = @"@implementation UnityScene {
}
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session options:(UISceneConnectionOptions *)connectionOptions {
    _pendingURLContext = [self firstValidContextFromContexts: connectionOptions.URLContexts];
    NSURL *url = [self pendingURL];
    UnitySetAbsoluteURL(url.absoluteString.UTF8String);
}
- (void)applyURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation {
    UnitySetAbsoluteURL(url.absoluteString.UTF8String);
}
@end";
        File.WriteAllText(scene, original);
        apply();
        string once = File.ReadAllText(scene);
        Check(once.IndexOf("GameBridgeConsumeGoogleSceneURL(_pendingURLContext.URL)", StringComparison.Ordinal) <
            once.IndexOf("NSURL *url = [self pendingURL]", StringComparison.Ordinal) &&
            once.Contains("if (GameBridgeConsumeGoogleSceneURL(_pendingURLContext.URL)) _pendingURLContext = nil;"),
            "discard the owned cold URL before Unity reads it");
        Check(once.Contains("if (GameBridgeConsumeGoogleSceneURL(url)) return;\n    UnitySetAbsoluteURL"),
            "discard the owned warm URL before the Unity URL setter");
        apply();
        Check(File.ReadAllText(scene) == once, "scene repeat must preserve source bytes");
        File.WriteAllText(scene, once.Replace("if (GameBridgeConsumeGoogleSceneURL(url)) return;", ""));
        MustFail(apply, "damaged scene forwarding", "conflicts with existing or modified Unity scene forwarding");
        File.WriteAllText(scene, original.Replace("firstValidContextFromContexts:", "customContext:"));
        MustFail(apply, "different scene handler", "requires the stock Unity scene URL handlers");
    }
}
