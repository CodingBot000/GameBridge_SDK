package com.gamebridge.consumer;
import android.app.Activity;
import android.os.Bundle;
import com.gamebridge.bridge.BridgeFacade;
public final class MainActivity extends Activity {
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        BridgeFacade.attachHost(this);
        BridgeFacade.dispatch("{}");
    }
}
