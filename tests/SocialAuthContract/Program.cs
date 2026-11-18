using System;
using System.Linq;
using System.Threading.Tasks;
using GameBridge;
using GameBridge.Core;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
class Transport:IWireTransport {
 public event Action<string> Message;
 public bool fail; public string lastProvider;
 public void Dispatch(string json) {
  var r=JObject.Parse(json);string op=(string)r["operation"];object result;
  if(op=="sdk.initialize")result=new {state="READY",mode="PLATFORM_SANDBOX",capabilities=new[]{"auth","store","push","config"}.ToDictionary(x=>x,x=>(object)new {supported=true,configured=true,mode="PLATFORM_SANDBOX",reason=(string)null})};
  else if(op=="auth.signIn"){lastProvider=(string)r["payload"]["provider"];result=new {userId="11111111-1111-4111-8111-111111111111",displayName=(string)null,provider=lastProvider,accessToken="synthetic-not-public"};}
  else result=new {};
  Message?.Invoke(JsonConvert.SerializeObject(new {protocolVersion=1,sdkSessionId=(string)r["sdkSessionId"],requestId=(string)r["requestId"],kind="response",operation=op,ok=!(fail&&op=="auth.signIn"),result=fail&&op=="auth.signIn"?null:result,error=fail&&op=="auth.signIn"?(object)new {code="CONFIG_REQUIRED",message="synthetic-not-public",retryable=false,requestId=(string)r["requestId"],nativeCode=(string)null,details=new {}}:null}));
 }
 public void Pump(){} public void Dispose(){Message=null;}
}
class Program {
 static async Task Main(){
  if((int)AuthProvider.MOCK!=0||(int)AuthProvider.GOOGLE!=1||(int)AuthProvider.APPLE!=2||(int)AuthProvider.FACEBOOK!=3)throw new Exception("enum ABI");
  var transport=new Transport();using(var client=new GameBridgeClient(transport)){
   await client.InitializeAsync(new GameBridgeConfig("app",ProviderMode.PlatformSandbox,"https://backend.invalid"));
   foreach(var provider in new[]{AuthProvider.GOOGLE,AuthProvider.APPLE,AuthProvider.FACEBOOK}){
    var profile=await client.SignInAsync(provider);if(profile.provider!=provider.ToString()||transport.lastProvider!=provider.ToString()||JsonConvert.SerializeObject(profile).Contains("synthetic-not-public"))throw new Exception("typed provider/privacy");
   }
   transport.fail=true;try{await client.SignInAsync(AuthProvider.FACEBOOK);throw new Exception("fallback");}catch(SdkException e){if(e.Code!="CONFIG_REQUIRED"||e.Message.Contains("synthetic-not-public"))throw;}
   await client.ShutdownAsync();
  }
  Console.WriteLine("Social Auth C# contract PASS: enum compatibility, explicit routing, typed redaction, no fallback");
 }
}
