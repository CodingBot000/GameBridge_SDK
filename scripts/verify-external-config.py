#!/usr/bin/env python3
"""Check presence/shape only. Never print configuration values or contact providers."""
import base64
import json
import os
from pathlib import Path


def valid_json(name, fields, paths=()):
    try:
        value = json.loads(os.environ.get(name, ''))
        if not isinstance(value, dict) or not value:
            return False
        for app, config in value.items():
            if not isinstance(app, str) or not app.strip() or not isinstance(config, dict) or not config:
                return False
            if name == 'GAMEBRIDGE_AUTH_AUDIENCES_JSON' and not any(isinstance(config.get(k), list) and config[k] and all(isinstance(v, str) and v.strip() for v in config[k]) for k in ('GOOGLE', 'APPLE')):
                return False
            for key in fields:
                item = config.get(key)
                if not item or not isinstance(item, (str, list)):
                    return False
            for key in paths:
                item = config.get(key)
                values = item if isinstance(item, list) else [item]
                if not values or any(not isinstance(p, str) or not Path(p).is_file() or not os.access(p, os.R_OK) for p in values):
                    return False
        return True
    except (ValueError, OSError, TypeError):
        return False


def valid_key(name):
    try:
        return len(base64.b64decode(os.environ.get(name, ''), validate=True)) == 32
    except (ValueError, TypeError):
        return False


def main():
    checks = {
        'auth audiences JSON': valid_json('GAMEBRIDGE_AUTH_AUDIENCES_JSON', ()),
        'Google purchase JSON and credential files': valid_json('GAMEBRIDGE_GOOGLE_PURCHASE_CONFIG_JSON', ('packageName', 'productIds', 'credentialPath'), ('credentialPath',)),
        'Apple purchase JSON and certificate files': valid_json('GAMEBRIDGE_APPLE_PURCHASE_CONFIG_JSON', ('bundleId', 'productIds', 'rootCertificatePaths'), ('rootCertificatePaths',)),
        'FCM JSON and credential files': valid_json('GAMEBRIDGE_FCM_CONFIG_JSON', ('projectId', 'credentialPath'), ('credentialPath',)),
        'APNs JSON and private key files': valid_json('GAMEBRIDGE_APNS_CONFIG_JSON', ('teamId', 'keyId', 'topic', 'privateKeyPath'), ('privateKeyPath',)),
        'purchase encryption key': valid_key('SERVER_PURCHASE_ENCRYPTION_KEY'),
        'push token encryption key': valid_key('SERVER_TOKEN_ENCRYPTION_KEY'),
    }
    for name, passed in checks.items():
        print(f"{name}: {'PRESENT_SHAPE_ONLY' if passed else 'MISSING_OR_INVALID'}")
    print('Shape checks do not validate identities, permissions, app settings, network access, or actual provider behavior. Live tests: NOT_RUN.')
    return 0 if all(checks.values()) else 2


if __name__ == '__main__':
    raise SystemExit(main())
