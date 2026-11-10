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
        Console.WriteLine("Gradle patcher smoke: PASS");
    }
}
