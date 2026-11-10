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
  var initial = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"><plist version=\"1.0\"><dict><key>Existing</key><string>keep</string></dict></plist>";
  var first = GameBridge.Editor.IosXcodeBuildHook.EnableXcodeStoreKitHistory(initial);
  var second = GameBridge.Editor.IosXcodeBuildHook.EnableXcodeStoreKitHistory(first);
  var plist = new PlistDocument(); plist.ReadFromString(second);
  if (!plist.root["SKIncludeConsumableInAppPurchaseHistory"].AsBoolean() || plist.root["Existing"].AsString() != "keep" || first != second)
   throw new Exception("StoreKit history plist patch failed");
  Console.WriteLine("Xcode development history plist idempotence: PASS");
 }
}
