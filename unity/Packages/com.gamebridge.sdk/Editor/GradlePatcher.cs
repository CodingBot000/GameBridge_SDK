using System;
using System.Text;
using System.Text.RegularExpressions;

namespace GameBridge.Editor
{
    /// <summary>Pure text patcher: refuse unfamiliar or partially patched files instead of overwriting them.</summary>
    internal static class GradlePatcher
    {
        private const string Begin = "// GAMEBRIDGE BEGIN";
        private const string End = "// GAMEBRIDGE END";

        internal static string AddRepository(string settings)
        {
            return Insert(settings, "repositories", "    maven { url = uri(\"${settingsDir}/gamebridge-maven\") }", "dependencyResolutionManagement");
        }
        internal static string AddDependency(string library)
        {
            return Insert(library, "dependencies", "    implementation 'com.gamebridge:sdk-unity-bridge:0.1.0-dev'", null);
        }
        private static string Insert(string source, string block, string statement, string parent)
        {
            if (source == null) throw new ArgumentNullException(nameof(source));
            int start = source.IndexOf(Begin, StringComparison.Ordinal);
            int end = source.IndexOf(End, StringComparison.Ordinal);
            if ((start >= 0) != (end >= 0) || (start >= 0 && (end < start || source.IndexOf(Begin, start + Begin.Length, StringComparison.Ordinal) >= 0 || source.IndexOf(End, end + End.Length, StringComparison.Ordinal) >= 0)))
                throw new InvalidOperationException("Invalid GameBridge marker block");
            if (start >= 0)
            {
                var existing = source.Substring(start, end + End.Length - start);
                if (!existing.Contains(statement.Trim())) throw new InvalidOperationException("Unexpected GameBridge marker block");
                return source;
            }
            string sanitized = MaskStringsAndComments(source);
            int rangeStart = 0, rangeEnd = sanitized.Length;
            if (parent != null)
            {
                int parentOpen = FindBlock(sanitized, parent, 0, sanitized.Length);
                rangeStart = parentOpen + 1; rangeEnd = ClosingBrace(sanitized, parentOpen);
            }
            int open = FindBlock(sanitized, block, rangeStart, rangeEnd);
            string newline = source.Contains("\r\n") ? "\r\n" : "\n";
            string insertion = newline + "    " + Begin + newline + statement + newline + "    " + End;
            return source.Insert(open + 1, insertion);
        }
        private static int FindBlock(string source, string name, int start, int end)
        {
            var regex = new Regex(@"\b" + Regex.Escape(name) + @"\s*\{");
            var matches = regex.Matches(source.Substring(start, end - start));
            if (matches.Count != 1) throw new InvalidOperationException("Expected exactly one " + name + " block");
            return start + matches[0].Index + matches[0].Length - 1;
        }
        private static int ClosingBrace(string source, int open)
        {
            int depth = 0;
            for (int i = open; i < source.Length; i++)
            {
                if (source[i] == '{') depth++;
                else if (source[i] == '}' && --depth == 0) return i;
            }
            throw new InvalidOperationException("Unbalanced Gradle braces");
        }
        private static string MaskStringsAndComments(string source)
        {
            var result = new StringBuilder(source);
            for (int i = 0; i < source.Length; i++)
            {
                char c = source[i];
                if (c == '\'' || c == '"')
                {
                    char quote = c; result[i] = ' '; bool closed = false;
                    while (++i < source.Length)
                    {
                        char next = source[i]; result[i] = next == '\n' ? '\n' : ' ';
                        if (next == '\\' && i + 1 < source.Length) { result[++i] = ' '; continue; }
                        if (next == quote) { closed = true; break; }
                    }
                    if (!closed) throw new InvalidOperationException("Unterminated Gradle string");
                }
                else if (c == '/' && i + 1 < source.Length && source[i + 1] == '/')
                {
                    while (i < source.Length && source[i] != '\n') result[i++] = ' ';
                }
                else if (c == '/' && i + 1 < source.Length && source[i + 1] == '*')
                {
                    result[i++] = ' '; result[i] = ' '; bool closed = false;
                    while (++i < source.Length)
                    {
                        if (source[i] == '*' && i + 1 < source.Length && source[i + 1] == '/') { result[i++] = ' '; result[i] = ' '; closed = true; break; }
                        if (source[i] != '\n') result[i] = ' ';
                    }
                    if (!closed) throw new InvalidOperationException("Unterminated Gradle comment");
                }
            }
            return result.ToString();
        }
    }
}
