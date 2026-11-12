# Editor Offline Demo

Import this sample from the package manager, install Unity uGUI (`com.unity.ugui`), and add the `OfflineDemo` component to an empty GameObject in a scene. The scene must have one EventSystem with an input module compatible with the project's active input system. Enter Play mode in the Editor.

The Home and Store panels use only the in-memory `EDITOR_OFFLINE` fake. Mock balances and purchases are not stored on the Backend and never represent real money. Player builds are intentionally disabled. Existing canvases and EventSystems are not replaced or removed.

An isolated Unity Editor test has run the sample initialization, mock sign-in, product listing, and mock purchase through programmatic UI callbacks. Package Manager UI import, visual rendering and pointer interaction have not been verified by that test. Actual device, store and network flows are not covered.
