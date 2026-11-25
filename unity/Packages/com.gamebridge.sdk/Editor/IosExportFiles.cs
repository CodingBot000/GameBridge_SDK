#if UNITY_IOS
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor.Build;

namespace GameBridge.Editor
{
    // The pending file is published atomically before the first target changes. Each entry
    // names a fixed slot, not a filesystem path supplied by the journal.
    internal sealed class IosExportFiles : IDisposable
    {
        private const string Format = "GameBridge iOS export 1";
        private readonly string pending;
        private readonly string[] paths;
        private readonly FileStream writerLock;
        private readonly Dictionary<int, string> originals = new Dictionary<int, string>();
        private readonly SortedDictionary<int, byte[]> changes = new SortedDictionary<int, byte[]>();

        internal IosExportFiles(string root, string projectPath)
        {
            paths = new[] { projectPath, Path.Combine(root, "Classes/UnityAppController.mm"),
                Path.Combine(root, "Classes/UI/UnityScene.mm"), Path.Combine(root, "Info.plist"),
                Path.Combine(root, "GameBridgeGooglePackage.txt"), Path.Combine(root, "GameBridgeFacebookPackage.txt") };
            pending = Path.Combine(root, ".gamebridge-ios-export.pending");
            writerLock = new FileStream(Path.Combine(root, ".gamebridge-ios-export.lock"),
                FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.None);
            try { Recover(); }
            catch { writerLock.Dispose(); throw; }
        }

        public void Dispose() => writerLock.Dispose();

        private int Slot(string path)
        {
            int slot = Array.IndexOf(paths, path);
            if (slot < 0) throw new ArgumentException("Unknown iOS export target: " + path);
            return slot;
        }

        private static byte[] Bytes(string path)
        {
            if (Directory.Exists(path)) throw new BuildFailedException("Expected an export file at " + path);
            return File.Exists(path) ? File.ReadAllBytes(path) : null;
        }

        private static string Hash(byte[] bytes)
        {
            if (bytes == null) return "-";
            using (var sha = SHA256.Create())
                return Convert.ToBase64String(sha.ComputeHash(bytes));
        }

        internal string Read(string path)
        {
            int slot = Slot(path);
            byte[] bytes = Bytes(path);
            string hash = Hash(bytes);
            if (originals.TryGetValue(slot, out string original) && original != hash) throw Conflict(path);
            originals[slot] = hash;
            if (bytes == null) return null;
            using (var reader = new StreamReader(new MemoryStream(bytes), Encoding.UTF8, true))
                return reader.ReadToEnd();
        }

        internal void Set(string path, string text)
        {
            if (Read(path) != text) changes[Slot(path)] = Encoding.UTF8.GetBytes(text);
        }

        internal void Commit(Action<string> afterWrite = null)
        {
            foreach (var item in originals)
                if (item.Value != Hash(Bytes(paths[item.Key]))) throw Conflict(paths[item.Key]);
            if (changes.Count == 0) return;
            var lines = new List<string> { Format };
            foreach (var item in changes)
                lines.Add(item.Key.ToString(CultureInfo.InvariantCulture) + " " + originals[item.Key] +
                    " " + Hash(item.Value) + " " + Convert.ToBase64String(item.Value));
            Publish(pending, Encoding.UTF8.GetBytes(string.Join("\n", lines)), false);
            Recover(afterWrite);
        }

        private static BuildFailedException Conflict(string path) =>
            new BuildFailedException("Host file changed during GameBridge export: " + path + ". Resolve the conflict before retrying.");

        private void Recover(Action<string> afterWrite = null)
        {
            if (!File.Exists(pending)) return;
            var lines = File.ReadAllLines(pending);
            if (lines.Length < 2 || lines[0] != Format) throw new BuildFailedException("Invalid GameBridge export journal: " + pending);
            var entries = new List<(int slot, string before, string after, byte[] bytes)>();
            var seen = new HashSet<int>();
            foreach (var line in lines.Skip(1))
            {
                var fields = line.Split(' ');
                if (fields.Length != 4 || !int.TryParse(fields[0], out int slot) || slot < 0 ||
                    slot >= paths.Length || !seen.Add(slot)) throw new BuildFailedException("Invalid GameBridge export entry: " + pending);
                var bytes = Convert.FromBase64String(fields[3]);
                if (Hash(bytes) != fields[2]) throw new BuildFailedException("Damaged GameBridge export content: " + paths[slot]);
                string actual = Hash(Bytes(paths[slot]));
                if (actual != fields[1] && actual != fields[2]) throw Conflict(paths[slot]);
                entries.Add((slot, fields[1], fields[2], bytes));
            }
            foreach (var entry in entries)
            {
                string path = paths[entry.slot];
                string actual = Hash(Bytes(path));
                if (actual == entry.after) continue;
                if (actual != entry.before) throw Conflict(path);
                Publish(path, entry.bytes, actual != "-");
                afterWrite?.Invoke(path);
            }
            File.Delete(pending);
        }

        private static void Publish(string path, byte[] bytes, bool replace)
        {
            string temp = path + ".gamebridge-" + Guid.NewGuid().ToString("N") + ".tmp";
            try
            {
                using (var file = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    file.Write(bytes, 0, bytes.Length);
                    file.Flush(true);
                }
                if (replace) File.Replace(temp, path, null);
                else File.Move(temp, path);
            }
            finally { if (File.Exists(temp)) File.Delete(temp); }
        }
    }
}
#endif
