#if UNITY_ANDROID
using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor.Android;
using UnityEditor.Build;
using UnityEditor.PackageManager;

namespace GameBridge.Editor
{
    internal sealed class AndroidGradleBuildHook : IPostGenerateGradleAndroidProject
    {
        public int callbackOrder => 0;
        public void OnPostGenerateGradleAndroidProject(string path)
        {
            var package = PackageInfo.FindForAssembly(typeof(AndroidGradleBuildHook).Assembly);
            if (package == null) throw new BuildFailedException("GameBridge package path unavailable.");
            var repo = Path.Combine(package.resolvedPath, "Editor", "GameBridgeArtifacts~", "Android", "maven-repo");
            var pom = Path.Combine(repo, "com", "gamebridge", "sdk-unity-bridge", "0.1.0-dev", "sdk-unity-bridge-0.1.0-dev.pom");
            if (!File.Exists(pom)) throw new BuildFailedException("GameBridge Maven repository is missing. Build and install the staged SDK package.");
            var root = Directory.GetParent(path)?.FullName ?? throw new BuildFailedException("Unity Gradle root missing.");
            var settingsPath = Path.Combine(root, "settings.gradle");
            var libraryPath = Path.Combine(path, "build.gradle");
            if (!File.Exists(settingsPath) || !File.Exists(libraryPath)) throw new BuildFailedException("Unity Gradle files missing.");
            string oldSettings = File.ReadAllText(settingsPath), oldLibrary = File.ReadAllText(libraryPath);
            string newSettings, newLibrary;
            try { newSettings = GradlePatcher.AddRepository(oldSettings); newLibrary = GradlePatcher.AddDependency(oldLibrary); }
            catch (InvalidOperationException ex) { throw new BuildFailedException("GameBridge cannot safely patch Gradle: " + ex.Message); }
            var target = Path.Combine(root, "gamebridge-maven");
            CopyOrVerify(repo, target);
            if (newSettings != oldSettings) File.WriteAllText(settingsPath, newSettings);
            if (newLibrary != oldLibrary) File.WriteAllText(libraryPath, newLibrary);
        }
        private static void CopyOrVerify(string source, string target)
        {
            var files = Directory.GetFiles(source, "*", SearchOption.AllDirectories).Where(f => !f.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)).ToArray();
            if (Directory.Exists(target))
            {
                using (var sha = SHA256.Create())
                    foreach (var file in files)
                    {
                        var relative = file.Substring(source.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                        var existing = Path.Combine(target, relative);
                        if (!File.Exists(existing) || !sha.ComputeHash(File.ReadAllBytes(file)).SequenceEqual(sha.ComputeHash(File.ReadAllBytes(existing))))
                            throw new BuildFailedException("Existing gamebridge-maven differs; choose a clean export directory.");
                    }
                return;
            }
            Directory.CreateDirectory(target);
            foreach (var file in files)
            {
                var relative = file.Substring(source.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                var destination = Path.Combine(target, relative);
                Directory.CreateDirectory(Path.GetDirectoryName(destination));
                File.Copy(file, destination, false);
            }
        }
    }
}
#endif
