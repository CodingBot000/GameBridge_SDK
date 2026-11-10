using System;
namespace UnityEditor.Android { public interface IPostGenerateGradleAndroidProject { int callbackOrder { get; } void OnPostGenerateGradleAndroidProject(string path); } }
namespace UnityEditor.Build { public class BuildFailedException : Exception { public BuildFailedException(string message) : base(message) {} } }
namespace UnityEditor.PackageManager { public sealed class PackageInfo { public string resolvedPath; public static PackageInfo Current; public static PackageInfo FindForAssembly(System.Reflection.Assembly assembly) => Current; } }
namespace UnityEditor { public enum BuildTarget { iOS, Android } }
namespace UnityEditor.Callbacks { public class PostProcessBuildAttribute : Attribute { public PostProcessBuildAttribute(int order) {} } }
namespace UnityEditor.iOS.Xcode {
    public enum PBXSourceTree { Source }
    public class PBXProject {
        public static System.Collections.Generic.HashSet<string> Files = new System.Collections.Generic.HashSet<string>();
        public static System.Collections.Generic.HashSet<string> Links = new System.Collections.Generic.HashSet<string>();
        public static string GetPBXProjectPath(string path) => System.IO.Path.Combine(path, "project.pbxproj");
        public void ReadFromFile(string path) {}
        public void WriteToFile(string path) {}
        public string FindFileGuidByProjectPath(string path) => Files.Contains(path) ? path : null;
        public string AddFile(string path, string projectPath, PBXSourceTree tree) { Files.Add(projectPath); return projectPath; }
        public string GetUnityFrameworkTargetGuid() => "framework";
        public void AddFileToBuild(string target, string guid) { Links.Add(target + ":" + guid); }
    }
}
