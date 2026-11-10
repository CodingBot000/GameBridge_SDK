package com.gamebridge.consumer

import com.gamebridge.android.purchase.GooglePlayStore
import com.gamebridge.android.purchase.GoogleStoreEvent
import kotlinx.coroutines.flow.Flow

/** Compile-only check that the published SDK exposes its public Flow dependency. */
fun observeStore(store: GooglePlayStore): Flow<GoogleStoreEvent> = store.events
