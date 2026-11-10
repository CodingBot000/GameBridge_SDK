.PHONY: doctor verify-progress android-mock ios-simulator unity-smoke

doctor:
	bash scripts/doctor.sh
verify-progress:
	python3 scripts/verify-progress.py
android-mock:
	bash scripts/build-android.sh --mock
ios-simulator:
	bash scripts/build-ios.sh --simulator
unity-smoke:
	bash scripts/build-unity.sh --editor-smoke
