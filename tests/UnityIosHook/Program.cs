using System;
using UnityEditor.iOS.Xcode;
class Program {
 static void Main(string[] args) {
  var p = new PBXProject(); p.ReadFromFile(args[0]);
  string target = p.TargetGuidByName("GameBridgeSample");
  string path = "Frameworks/GameBridge/GameBridgeNative.xcframework";
  string guid = p.AddFile(path, path, PBXSourceTree.Source);
  p.AddFileToBuild(target, guid); string once = p.WriteToString();
  p.AddFileToBuild(target, guid); string twice = p.WriteToString();
  if (once != twice) throw new Exception("Duplicate PBX build entry");
  Console.WriteLine("Real PBX API idempotence: PASS");
 }
}
