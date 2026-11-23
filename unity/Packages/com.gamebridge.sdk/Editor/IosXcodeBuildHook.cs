#if UNITY_IOS
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Callbacks;
using UnityEditor.iOS.Xcode;
using UnityEditor.PackageManager;

namespace GameBridge.Editor
{
    internal static class IosXcodeBuildHook
    {
        private const string GoogleCallbackDefine = "GAMEBRIDGE_IOS_GOOGLE_AUTH_CALLBACK";
        private const string AppControllerHeader = "#import <GameBridgeNative/GameBridgeNative.h>";
        private const string CallbackMarker = "// GameBridge Google OAuth callback";
        private const string OpenUrlSelector =
            "- (BOOL)application:(UIApplication*)app openURL:(NSURL*)url options:(NSDictionary<NSString*, id>*)options";
        private const string GoogleCallback = @"    // GameBridge Google OAuth callback
    NSString *googleClientID = [[NSBundle mainBundle] objectForInfoDictionaryKey:@""GIDClientID""];
    if ([googleClientID isKindOfClass:[NSString class]] &&
        [googleClientID hasSuffix:@"".apps.googleusercontent.com""])
    {
        NSArray<NSString *> *parts = [googleClientID componentsSeparatedByString:@"".""];
        NSString *googleScheme = [parts.reverseObjectEnumerator.allObjects componentsJoinedByString:@"".""];
        if (url.scheme != nil && [url.scheme caseInsensitiveCompare:googleScheme] == NSOrderedSame)
        {
            NSData *callback = [url.absoluteString dataUsingEncoding:NSUTF8StringEncoding];
            if (callback.length > 0 && callback.length <= 8192)
                GB_HandleAuthURL(static_cast<const uint8_t *>(callback.bytes), static_cast<int32_t>(callback.length));
            // Never forward a registered Google callback to Unity's managed URL event.
            return YES;
        }
    }
";

        [PostProcessBuild(100)]
        internal static void OnPostprocessBuild(BuildTarget target, string path)
        {
            if (target != BuildTarget.iOS) return;
            bool storeKit = false;
#if GAMEBRIDGE_XCODE_STOREKIT
            if (!EditorUserBuildSettings.development) throw new BuildFailedException("GAMEBRIDGE_XCODE_STOREKIT requires an iOS Development Build.");
            storeKit = true;
#endif
            var package = UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(IosXcodeBuildHook).Assembly);
            if (package == null) throw new BuildFailedException("GameBridge package path unavailable.");
            var source = Path.Combine(package.resolvedPath, "Editor", "GameBridgeArtifacts~", "iOS", "GameBridgeNative.xcframework");
            ApplyExport(path, PBXProject.GetPBXProjectPath(path), source,
                PlayerSettings.GetScriptingDefineSymbols(NamedBuildTarget.iOS).Split(';').Contains(GoogleCallbackDefine), storeKit);
        }

        internal static void ApplyExport(string output, string projectPath, string source, bool googleCallback,
            bool storeKit, Action<string> afterWrite = null)
        {
            if (!File.Exists(Path.Combine(source, "Info.plist")))
                throw new BuildFailedException("GameBridge XCFramework missing: " + source);
            using var files = new IosExportFiles(output, projectPath);
            var project = new PBXProject();
            project.ReadFromString(files.Read(projectPath) ?? throw new BuildFailedException("Unity Xcode project missing: " + projectPath));

            const string relative = "Frameworks/GameBridge/GameBridgeNative.xcframework";
            string guid = project.FindFileGuidByProjectPath(relative);
            if (string.IsNullOrEmpty(guid)) guid = project.AddFile(relative, relative, PBXSourceTree.Source);
            project.AddFileToBuild(project.GetUnityFrameworkTargetGuid(), guid);
            ConfigureAuthPackages(project, output, files);
            if (googleCallback) PlanGoogleCallback(output, files);
            if (storeKit)
            {
                string plist = Path.Combine(output, "Info.plist");
                files.Set(plist, EnableXcodeStoreKitHistory(files.Read(plist) ?? throw new BuildFailedException("Unity Info.plist missing: " + plist)));
            }
            files.Set(projectPath, project.WriteToString());

            // Publish only a complete framework. On retry an already-published copy is verified.
            string destination = Path.Combine(output, relative);
            if (Directory.Exists(destination)) ArtifactCopy.CopyOrVerify(source, destination);
            else
            {
                string stage = destination + ".gamebridge-" + Guid.NewGuid().ToString("N");
                try
                {
                    ArtifactCopy.CopyOrVerify(source, stage);
                    Directory.Move(stage, destination);
                }
                finally { if (Directory.Exists(stage)) Directory.Delete(stage, true); }
            }
            files.Commit(afterWrite);
        }

        internal static void PlanGoogleCallback(string output, IosExportFiles files)
        {
            string path = Path.Combine(output, "Classes", "UnityAppController.mm");
            string source = files.Read(path) ?? throw new BuildFailedException("GameBridge Google callback requires the exported UnityAppController.mm: " + path);
            files.Set(path, WithGoogleAppCallback(source));
            string scenePath = Path.Combine(output, "Classes", "UI", "UnityScene.mm");
            string scene = files.Read(scenePath);
            if (scene != null) files.Set(scenePath, WithGoogleSceneCallback(scene));
            else if (files.Read(Path.Combine(output, "Info.plist"))?.Contains("UnityScene") == true)
                throw new BuildFailedException("GameBridge Google callback requires the exported UnityScene.mm: " + scenePath);
        }
        private static string WithGoogleAppCallback(string source)
        {
            string newline = source.Contains("\r\n") ? "\r\n" : "\n";
            string anchor = OpenUrlSelector + newline + "{" + newline;
            int insert = source.IndexOf(anchor, StringComparison.Ordinal);
            if (insert < 0 || insert != source.LastIndexOf(anchor, StringComparison.Ordinal))
                throw new BuildFailedException("GameBridge Google callback requires one stock Unity openURL handler. For a custom Host, forward the callback explicitly.");
            insert += anchor.Length;

            string callback = GoogleCallback.Replace("\n", newline);
            int header = source.IndexOf(AppControllerHeader + newline, StringComparison.Ordinal);
            if (source.Contains(CallbackMarker) || source.Contains("GB_HandleAuthURL"))
            {
                bool exact = source.IndexOf(callback, StringComparison.Ordinal) == insert &&
                    source.IndexOf(CallbackMarker, StringComparison.Ordinal) == source.LastIndexOf(CallbackMarker, StringComparison.Ordinal) &&
                    source.IndexOf("GB_HandleAuthURL", StringComparison.Ordinal) == source.LastIndexOf("GB_HandleAuthURL", StringComparison.Ordinal) &&
                    header >= 0 && header < insert;
                if (!exact)
                    throw new BuildFailedException("GameBridge Google callback conflicts with existing or modified Host forwarding. Use only one forwarding path.");
                return source;
            }
            string updated = source.Insert(insert, callback);
            return header >= 0 && header < insert ? updated : AppControllerHeader + newline + updated;
        }
        private static string WithGoogleSceneCallback(string source)
        {
            string newline = source.Contains("\r\n") ? "\r\n" : "\n";
            string implementation = "@implementation UnityScene {";
            string coldSelection = "    _pendingURLContext = [self firstValidContextFromContexts: connectionOptions.URLContexts];" + newline;
            string warmHandler = "- (void)applyURL:(NSURL *)url sourceApplication:(NSString *)sourceApplication annotation:(id)annotation {" + newline;
            const string helperName = "GameBridgeConsumeGoogleSceneURL";
            string helper = ("static BOOL " + helperName + "(NSURL *url)\n{\n" + GoogleCallback + "    return NO;\n}\n\n").Replace("\n", newline);
            string cold = "    if (" + helperName + "(_pendingURLContext.URL)) _pendingURLContext = nil;" + newline;
            string warm = "    if (" + helperName + "(url)) return;" + newline;
            int Where(string anchor)
            {
                int position = source.IndexOf(anchor, StringComparison.Ordinal);
                if (position < 0 || position != source.LastIndexOf(anchor, StringComparison.Ordinal))
                    throw new BuildFailedException("GameBridge Google callback requires the stock Unity scene URL handlers. For a custom Host, forward explicitly.");
                return position;
            }
            int implementationStart = Where(implementation);
            int coldStart = Where(coldSelection) + coldSelection.Length;
            int warmStart = Where(warmHandler) + warmHandler.Length;
            if (implementationStart >= coldStart || coldStart >= warmStart)
                throw new BuildFailedException("GameBridge Google callback requires the stock Unity scene URL handlers.");
            int header = source.IndexOf(AppControllerHeader + newline, StringComparison.Ordinal);
            if (source.Contains(CallbackMarker) || source.Contains("GB_HandleAuthURL") || source.Contains(helperName))
            {
                bool exact = source.IndexOf(helper + implementation, StringComparison.Ordinal) == implementationStart - helper.Length &&
                    source.IndexOf(coldSelection + cold, StringComparison.Ordinal) == coldStart - coldSelection.Length &&
                    source.IndexOf(warmHandler + warm, StringComparison.Ordinal) == warmStart - warmHandler.Length &&
                    source.IndexOf("GB_HandleAuthURL", StringComparison.Ordinal) == source.LastIndexOf("GB_HandleAuthURL", StringComparison.Ordinal) &&
                    header >= 0 && header < implementationStart;
                if (!exact) throw new BuildFailedException("GameBridge Google callback conflicts with existing or modified Unity scene forwarding.");
                return source;
            }
            string updated = source.Insert(warmStart, warm).Insert(coldStart, cold).Insert(implementationStart, helper);
            return header >= 0 && header < implementationStart ? updated : AppControllerHeader + newline + updated;
        }
        private static void EnsureGooglePackage(PBXProject project, string output, IosExportFiles files)
        {
            const string url = "https://github.com/google/GoogleSignIn-iOS";
            const string version = "9.2.0";
            string marker = Path.Combine(output, "GameBridgeGooglePackage.txt");
            string before = project.WriteToString();
            string guid = ExistingPackage(files, marker, before, url);
            if (guid != null)
            {
                string body = PbxObject(before, guid);
                if (Field(body, "isa") != "XCRemoteSwiftPackageReference" || Field(body, "repositoryURL") != url ||
                    Field(body, "kind") != "exactVersion" || Field(body, "version") != version ||
                    !HasProductLink(project, project.GetUnityFrameworkTargetGuid(), guid, "GoogleSignIn"))
                    throw new BuildFailedException("GameBridge Google SPM ownership/version mismatch: " + marker);
                return;
            }
            if (before.Contains(url)) throw new BuildFailedException("Host already configures GoogleSignIn: " + marker + ". Resolve the exact 9.2.0 dependency explicitly.");
            string packageGuid = project.AddRemotePackageReferenceAtVersion(url, version);
            project.AddRemotePackageFrameworkToProject(project.GetUnityFrameworkTargetGuid(), "GoogleSignIn", packageGuid, false);
            files.Set(marker, packageGuid);
        }
        // Legacy exports could leave a GUID marker before saving the PBX. It can only
        // be replaced if both the GUID and the package URL are absent from this project.
        private static string ExistingPackage(IosExportFiles files, string marker, string project, string url)
        {
            string guid = files.Read(marker)?.Trim();
            if (guid == null) return null;
            if (!Regex.IsMatch(guid, "^[0-9a-fA-F]{24}$"))
                throw new BuildFailedException("Invalid GameBridge package marker: " + marker);
            return !project.Contains(guid) && !project.Contains(url) ? null : guid;
        }

        private static void ConfigureAuthPackages(PBXProject project, string output, IosExportFiles files)
        {
            if (string.IsNullOrEmpty(project.GetUnityMainTargetGuid()) || string.IsNullOrEmpty(project.GetUnityFrameworkTargetGuid()))
                throw new BuildFailedException("GameBridge requires the Unity app and UnityFramework targets.");
            EnsureGooglePackage(project, output, files);
            EnsureFacebookPackage(project, output, files);
        }
        // Read Unity's canonical PBX serialization. Fail explicitly if an owned
        // object disappears; do not delete or replace Host objects.
        private static string PbxObject(string text, string guid)
        {
            if (!Regex.IsMatch(guid ?? "", "^[0-9a-fA-F]{24}$")) throw new BuildFailedException("Invalid GameBridge PBX object identity.");
            string prefix = @"(?m)^\t\t" + guid + @"(?: /\*[^\r\n]*\*/)? = \{";
            var inline = Regex.Match(text, prefix + @"([^\r\n]*)\};\r?$");
            if (inline.Success) return inline.Groups[1].Value;
            var match = Regex.Match(text, @"(?ms)^\t\t" + guid + @"(?: /\*[^\r\n]*\*/)? = \{\r?\n(.*?)^\t\t\};");
            if (!match.Success) throw new BuildFailedException("GameBridge PBX dependency object is missing.");
            return match.Groups[1].Value;
        }
        private static string Field(string body, string name)
        {
            var match = Regex.Match(body, @"(?:^|[;\r\n])\s*" + Regex.Escape(name) + @" = ([^;\r\n]+);");
            return match.Success ? match.Groups[1].Value.Trim().Trim('"') : "";
        }
        private static string GuidField(string body, string name) => Regex.Match(Field(body, name), "^[0-9a-fA-F]{24}\\b").Value;
        private static string[] ReferenceList(string body, string name)
        {
            var list = Regex.Match(body, @"(?s)\b" + Regex.Escape(name) + @" = \((.*?)\);");
            return Regex.Matches(list.Success ? list.Groups[1].Value : "", @"(?m)^\s*([0-9A-Fa-f]{24})(?: /\*[^\r\n]*\*/)?\s*,")
                .Cast<Match>().Select(x => x.Groups[1].Value).ToArray();
        }
        private static bool HasProductLink(PBXProject project, string target, string package, string product)
        {
            string text = project.WriteToString(), body = PbxObject(text, target);
            var products = ReferenceList(body, "packageProductDependencies")
                .Where(id => Field(PbxObject(text, id), "productName") == product).ToArray();
            if (products.Length == 0) return false;
            if (products.Length != 1 || GuidField(PbxObject(text, products[0]), "package") != package)
                throw new BuildFailedException("Conflicting " + product + " package product on the Host target.");
            string phase = project.GetFrameworksBuildPhaseByTarget(target);
            var links = ReferenceList(PbxObject(text, phase), "files")
                .Select(id => PbxObject(text, id)).Where(x => GuidField(x, "productRef") == products[0]).ToArray();
            if (links.Length != 1 || Regex.IsMatch(links[0], @"\bWeak\b"))
                throw new BuildFailedException(product + " must have exactly one strong framework link.");
            return true;
        }
        private static void EnsureFacebookPackage(PBXProject project, string output, IosExportFiles files)
        {
            const string url = "https://github.com/facebook/facebook-ios-sdk";
            const string version = "18.1.1";
            string marker = Path.Combine(output, "GameBridgeFacebookPackage.txt");
            string package = ExistingPackage(files, marker, project.WriteToString(), url);
            bool existing = package != null;
            if (existing)
            {
                string body = PbxObject(project.WriteToString(), package);
                if (Field(body, "isa") != "XCRemoteSwiftPackageReference" || Field(body, "repositoryURL") != url ||
                    Field(body, "kind") != "exactVersion" || Field(body, "version") != version)
                    throw new BuildFailedException("GameBridge Facebook SPM ownership/version mismatch.");
            }
            else
            {
                if (project.WriteToString().Contains(url)) throw new BuildFailedException("Host Facebook SPM configuration exists; resolve exact18.1.1 explicitly. Host settings are not overwritten.");
                package = project.AddRemotePackageReferenceAtVersion(url, version);
            }
            // The app must own this SPM product as well: Xcode then embeds/signs
            // LoginKit's four transitive dynamic frameworks into app/Frameworks.
            // GameBridgeNative stays static and FacebookLogin remains linked to
            // UnityFramework. Do not copy downloaded SDKs into built apps by hand.
            foreach (string target in new[] { project.GetUnityFrameworkTargetGuid(), project.GetUnityMainTargetGuid() })
            {
                if (!HasProductLink(project, target, package, "FacebookLogin"))
                    project.AddRemotePackageFrameworkToProject(target, "FacebookLogin", package, false);
                if (!HasProductLink(project, target, package, "FacebookLogin")) throw new BuildFailedException("FacebookLogin dependency was not linked.");
            }
            if (!existing) files.Set(marker, package);
        }
        internal static string EnableXcodeStoreKitHistory(string source)
        {
            var plist = new PlistDocument(); plist.ReadFromString(source);
            plist.root.SetBoolean("SKIncludeConsumableInAppPurchaseHistory", true);
            return plist.WriteToString();
        }
    }
}
#endif
