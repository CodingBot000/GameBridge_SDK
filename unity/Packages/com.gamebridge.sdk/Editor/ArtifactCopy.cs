using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor.Build;

namespace GameBridge.Editor
{
    internal static class ArtifactCopy
    {
        internal static void CopyOrVerify(string source, string target)
        {
            var files = Directory.GetFiles(source, "*", SearchOption.AllDirectories).Where(f => !f.EndsWith(".meta", StringComparison.OrdinalIgnoreCase)).ToArray();
            if (files.Length == 0) throw new BuildFailedException("GameBridge artifact directory is empty.");
            if (Directory.Exists(target))
            {
                using (var sha = SHA256.Create())
                    foreach (var file in files)
                    {
                        var relative = file.Substring(source.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
                        var existing = Path.Combine(target, relative);
                        if (!File.Exists(existing) || !sha.ComputeHash(File.ReadAllBytes(file)).SequenceEqual(sha.ComputeHash(File.ReadAllBytes(existing))))
                            throw new BuildFailedException("Existing GameBridge artifact differs; choose a clean export directory.");
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
