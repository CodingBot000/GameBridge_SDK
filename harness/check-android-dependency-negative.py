#!/usr/bin/env python3
"""Build a new consumer, then remove only its copied transitive SDK dependency."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent

def main():
    raw=os.environ.get('GAMEBRIDGE_MAVEN_REPO','')
    source=Path(raw).resolve() if raw else None
    if source is None or not (source/'com/gamebridge/sdk-core/0.1.0-dev/sdk-core-0.1.0-dev.jar').is_file():
        print('CONFIG_REQUIRED: GAMEBRIDGE_MAVEN_REPO with built SDK',file=sys.stderr); return 2
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True); work=Path(tempfile.mkdtemp(prefix='android-dependency-negative-',dir=artifacts))
    repo=work/'maven'; consumer=work/'consumer'; shutil.copytree(source,repo)
    shutil.copytree(ROOT/'android/consumer-check',consumer,ignore=shutil.ignore_patterns('.gradle','build','.kotlin'))
    # No network fallback for the SDK group, even when Gradle is used outside offline mode.
    (consumer/'settings.gradle.kts').write_text('''pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
  repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
  repositories {
    exclusiveContent { forRepository { maven { url = uri(System.getenv("GAMEBRIDGE_MAVEN_REPO")) } }; filter { includeGroup("com.gamebridge") } }
    google(); mavenCentral()
  }
}
rootProject.name = "GameBridgeDependencyNegative"
include(":app")
''')
    env=os.environ.copy(); env['GAMEBRIDGE_MAVEN_REPO']=str(repo); env.setdefault('ANDROID_HOME',str(Path.home()/'Library/Android/sdk'))
    command=[str(ROOT/'android/gradlew'),'-p',str(consumer),':app:assembleRelease','--offline','--rerun-tasks']
    try:
        baseline=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
        (work/'baseline.log').write_text(baseline.stdout)
        if baseline.returncode != 0: print(f'Consumer baseline failed; evidence: {work.relative_to(ROOT)}',file=sys.stderr); return 1
        (repo/'com/gamebridge/sdk-core/0.1.0-dev/sdk-core-0.1.0-dev.jar').unlink()
        mutated=subprocess.run(command+['--refresh-dependencies'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
        (work/'missing-dependency.log').write_text(mutated.stdout)
        if mutated.returncode == 0 or 'sdk-core-0.1.0-dev.jar' not in mutated.stdout or 'Could not find' not in mutated.stdout:
            print(f'Missing dependency was not rejected for the expected reason; evidence: {work.relative_to(ROOT)}',file=sys.stderr); return 1
    except (OSError,subprocess.TimeoutExpired): print('Consumer verification unavailable',file=sys.stderr); return 2
    print(f'Android dependency negative PASS: baseline built and missing core artifact rejected; evidence directory: {work.relative_to(ROOT)}'); return 0

if __name__=='__main__': raise SystemExit(main())
