using System;
namespace UnityEditor.Android { public interface IPostGenerateGradleAndroidProject { int callbackOrder { get; } void OnPostGenerateGradleAndroidProject(string path); } }
namespace UnityEditor.Build { public class BuildFailedException : Exception { public BuildFailedException(string message) : base(message) {} } }
namespace UnityEditor.PackageManager { public sealed class PackageInfo { public string resolvedPath; public static PackageInfo Current; public static PackageInfo FindForAssembly(System.Reflection.Assembly assembly) => Current; } }
