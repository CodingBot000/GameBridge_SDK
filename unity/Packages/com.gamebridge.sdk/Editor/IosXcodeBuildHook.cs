#if UNITY_IOS
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Callbacks;
using UnityEditor.iOS.Xcode;
using UnityEditor.PackageManager;

namespace GameBridge.Editor
{
    internal static class IosXcodeBuildHook
    {
        [PostProcessBuild(100)]
        internal static void OnPostprocessBuild(BuildTarget target, string path)
        {
            if (target != BuildTarget.iOS) return;
#if GAMEBRIDGE_XCODE_STOREKIT
            if (!EditorUserBuildSettings.development) throw new BuildFailedException("GAMEBRIDGE_XCODE_STOREKIT requires an iOS Development Build.");
            string plistPath = Path.Combine(path, "Info.plist");
            if (!File.Exists(plistPath)) throw new BuildFailedException("Unity iOS Info.plist is missing.");
#endif
            var package = UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(IosXcodeBuildHook).Assembly);
            if (package == null) throw new BuildFailedException("GameBridge package path unavailable.");
            var source = Path.Combine(package.resolvedPath, "Editor", "GameBridgeArtifacts~", "iOS", "GameBridgeNative.xcframework");
            if (!File.Exists(Path.Combine(source, "Info.plist"))) throw new BuildFailedException("GameBridge XCFramework missing. Build and install the staged SDK package.");
            const string relative = "Frameworks/GameBridge/GameBridgeNative.xcframework";
            string destination = Path.Combine(path, relative);
            string projectPath = PBXProject.GetPBXProjectPath(path);
            if (!File.Exists(projectPath)) throw new BuildFailedException("Unity Xcode project is missing.");
            var project = new PBXProject(); project.ReadFromFile(projectPath);
            string guid = project.FindFileGuidByProjectPath(relative);
            ArtifactCopy.CopyOrVerify(source, destination);
            if (string.IsNullOrEmpty(guid)) guid = project.AddFile(relative, relative, PBXSourceTree.Source);
            project.AddFileToBuild(project.GetUnityFrameworkTargetGuid(), guid);
            EnsureGooglePackage(project, path, projectPath);
            EnsureFacebookPackage(project, path, projectPath);
            project.WriteToFile(projectPath);
#if GAMEBRIDGE_XCODE_STOREKIT
            File.WriteAllText(plistPath, EnableXcodeStoreKitHistory(File.ReadAllText(plistPath)));
#endif
        }
        private static void EnsureGooglePackage(PBXProject project, string output, string projectPath)
        {
            const string url = "https://github.com/google/GoogleSignIn-iOS";
            const string version = "9.2.0";
            string marker = Path.Combine(output, "GameBridgeGooglePackage.txt");
            string before = File.ReadAllText(projectPath);
            if (File.Exists(marker))
            {
                string guid = File.ReadAllText(marker).Trim();
                if (guid.Length != 24 || !before.Contains(guid) || !before.Contains(url) || !before.Contains(version))
                    throw new BuildFailedException("GameBridge Google SPM ownership/version mismatch.");
                return;
            }
            if (before.Contains(url)) throw new BuildFailedException("Host already configures GoogleSignIn. Resolve the exact9.2.0 dependency explicitly before running this hook; it will not overwrite Host packages.");
            string packageGuid = project.AddRemotePackageReferenceAtVersion(url, version);
            project.AddRemotePackageFrameworkToProject(project.GetUnityFrameworkTargetGuid(), "GoogleSignIn", packageGuid, false);
            File.WriteAllText(marker, packageGuid);
        }
        private static void EnsureFacebookPackage(PBXProject project, string output, string projectPath)
        {
            const string url = "https://github.com/facebook/facebook-ios-sdk";
            const string version = "18.1.1";
            string marker = Path.Combine(output, "GameBridgeFacebookPackage.txt");
            string before = File.ReadAllText(projectPath);
            if (File.Exists(marker)) {
                string guid = File.ReadAllText(marker).Trim();
                if (guid.Length != 24 || !before.Contains(guid) || !before.Contains(url) || !before.Contains(version)) throw new BuildFailedException("GameBridge Facebook SPM ownership/version mismatch.");
                return;
            }
            if (before.Contains(url)) throw new BuildFailedException("Host Facebook SPM configuration exists; resolve exact18.1.1 explicitly. Host settings are not overwritten.");
            string package = project.AddRemotePackageReferenceAtVersion(url, version);
            project.AddRemotePackageFrameworkToProject(project.GetUnityFrameworkTargetGuid(), "FacebookLogin", package, false);
            File.WriteAllText(marker, package);
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
