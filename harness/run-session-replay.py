#!/usr/bin/env python3
"""Opt-in local-only refresh replay test; logs no tokens and creates only new sessions."""
import json
import os
import sys
import urllib.error
import urllib.request

BASE='http://127.0.0.1:18080'

def main():
    key=os.environ.get('GAMEBRIDGE_DEV_AUTH_KEY','')
    if os.environ.get('GAMEBRIDGE_RUN_LOCAL_CLIENT_TEST') != 'true' or len(key) < 32:
        print('CONFIG_REQUIRED: explicit isolated local server opt-in and development key',file=sys.stderr); return 2
    def call(method,path,body=None,token=None):
        headers={'Content-Type':'application/json'}
        if path == '/v1/dev/auth': headers['X-Development-Key']=key
        if token is not None: headers['Authorization']='Bearer '+token
        request=urllib.request.Request(BASE+path,method=method,headers=headers,data=None if body is None else json.dumps(body).encode())
        try:
            with urllib.request.urlopen(request,timeout=5) as response: return response.status,json.load(response)
        except urllib.error.HTTPError as error: return error.code,json.load(error)
    def check(condition):
        if not condition: raise AssertionError("session invariant")
    try:
        status,first=call('POST','/v1/dev/auth',{'subject':'A'}); check(status==200)
        status,other=call('POST','/v1/dev/auth',{'subject':'A'}); check(status==200 and other['userId']==first['userId'])
        status,rotated=call('POST','/v1/auth/refresh',{'refreshToken':first['refreshToken']}); check(status==200 and rotated['refreshToken']!=first['refreshToken'])
        status,_=call('POST','/v1/auth/refresh',{'refreshToken':first['refreshToken']}); check(status==401)
        status,_=call('GET','/v1/me',token=rotated['accessToken']); check(status==401)
        status,_=call('POST','/v1/auth/refresh',{'refreshToken':rotated['refreshToken']}); check(status==401)
        status,_=call('GET','/v1/me',token=other['accessToken']); check(status==200)
        status,fresh=call('POST','/v1/dev/auth',{'subject':'A'}); check(status==200 and fresh['userId']==first['userId'])
        status,_=call('GET','/v1/me',token=fresh['accessToken']); check(status==200)
        for session in (other,fresh):
            status,_=call('POST','/v1/auth/logout',token=session['accessToken']); check(status==200)
    except (AssertionError,OSError,ValueError,KeyError,TypeError) as error:
        print(f'Local session replay test failed: {type(error).__name__}',file=sys.stderr); return 1
    print('Local session replay PASS: prior token revokes its family; another family and fresh login remain valid.')
    return 0

if __name__=='__main__': raise SystemExit(main())
