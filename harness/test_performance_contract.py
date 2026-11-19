import copy,unittest
from performance_contract import distribution,managed_summary,is_exact_coin_grant,validate_player_summary

class PerformanceContractTests(unittest.TestCase):
    def fixture(self):
        scope=dict(distribution(list(range(100))),samplesMilliseconds=list(range(100)))
        return dict(status='PASS',sourceHead='head',clock='Stopwatch monotonic',clockFrequency=1_000_000_000,build='Release/Optimize=true',warmup=20,samples=100,timings={x:copy.deepcopy(scope) for x in ('createInitialize','callbackProductQuery','shutdownDispose','registryEightInflightDuplicateCancelLate')},measuredWorkload=dict(inFlightPerCycle=8,successfulResponses=800,expectedCancellations=100,ignoredDuplicateResponses=100,ignoredLateResponses=100,finalPending=0,liveClients=0,liveTransports=0))
    def test_nearest_rank_quantiles_and_max_are_derived_from_actual_sample_values(self):
        self.assertEqual(distribution(list(range(100))),dict(samples=100,unit='milliseconds',p50=49,p95=94,max=99))
    def test_missing_nonfinite_negative_boolean_and_insufficient_samples_rejected(self):
        for value in ([],[0]*99,[True]*100,[float('nan')]*100,[float('inf')]*100,[-1]*100):
            with self.assertRaises(ValueError):distribution(value)
    def test_scoped_release_metadata_and_cleanup_are_required(self):
        value=self.fixture();self.assertIn('timings',managed_summary(value,'head'))
        for key,bad in [('sourceHead','stale'),('status','NOT_RUN'),('warmup',0),('samples',316),('clock','wall clock'),('build','Debug')]:
            changed=copy.deepcopy(value);changed[key]=bad
            with self.assertRaises(ValueError):managed_summary(changed,'head')
        value['measuredWorkload']['finalPending']=1
        with self.assertRaises(ValueError):managed_summary(value,'head')
    def test_wallet_contract_uses_exact_decimal_string_and_same_purchase(self):
        self.assertTrue(is_exact_coin_grant({'serverPurchaseId':'fixture','entitlements':{'coinBalance':'100'}},'fixture'))
        for value in (100,100.0,True,'100.0','0',None):self.assertFalse(is_exact_coin_grant({'serverPurchaseId':'fixture','entitlements':{'coinBalance':value}},'fixture'))
        self.assertFalse(is_exact_coin_grant({'serverPurchaseId':'other','entitlements':{'coinBalance':'100'}},'fixture'))

    def test_declarations_helpers_and_forged_percentiles_cannot_replace_samples(self):
        for kind in ('missing','count','p95','live'):
            value=self.fixture()
            if kind=='missing':value['timings'].pop('callbackProductQuery')
            elif kind=='count':value['timings']['callbackProductQuery']['samplesMilliseconds']=[316]
            elif kind=='p95':value['timings']['callbackProductQuery']['p95']=90
            else:value['measuredWorkload']['liveTransports']=1
            with self.assertRaises(ValueError):managed_summary(value,'head')
    def test_actual_player_summary_preserves_retention_observation_and_rejects_bad_counts(self):
        value=dict(warmup=20,samples=100,unityVersion='6000.5.8f1',platform='IPhonePlayer',unityAllocatedBeforeBytes=1,unityAllocatedAfterBytes=2,managedUsedBeforeBytes=1,managedUsedAfterBytes=2,managedWeakClientsRetained=1,pendingAfterCompletedCallsMax=0)
        for name in ('initialize','nativeDiagnosticsRoundtripToMainThread','shutdown','sceneTransition','frameIntervals'):
            value[name]=dict(samples=100,p50Ms=1.0,p95Ms=2.0,maxMs=3.0)
        self.assertEqual(validate_player_summary(value)['observedWeakClientsRetained'],1)
        for key,bad in [('samples',316),('pendingAfterCompletedCallsMax',1),('managedUsedAfterBytes',True)]:
            changed=copy.deepcopy(value);changed[key]=bad
            with self.assertRaises(ValueError):validate_player_summary(changed)
        value['sceneTransition']['p95Ms']=float('nan')
        with self.assertRaises(ValueError):validate_player_summary(value)
if __name__=='__main__':unittest.main()
