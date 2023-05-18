import time

from caproto.threading.client import Context, SharedBroadcaster, Subscription, PV


pvnames = """
SUPPORT:DR_PTN:XAXIS_MON
SUPPORT:DR_PTN:REFERENCE_PTN_A
SUPPORT:DR_PTN:EXT
SUPPORT:DR_PTN:GEN_REFERENCE
SUPPORT:BPMFB:RB:BPM_P_GAIN_DP_FLOAT
SUPPORT:BPMFB:SET:BPM_I_GAIN_DR_FLOAT_CHANGE
SUPPORT:DR_PTN:TIMMING_RISE
SUPPORT:BPMFB:SET:BPM_P_GAIN_DR_FLOAT
SUPPORT:BPMFB:SET:BPM_GAIN_2FS_FLOAT_CHANGE
SUPPORT:DR_PTN:FB
SUPPORT:DR_PTN:WAVE_SPAN
SUPPORT:DR_PTN:WAVE_DELAY
SUPPORT:BPMFB:SET:BPM_P_GAIN_DR_FLOAT_CHANGE
SUPPORT:BPMFB:RB:BPM_I_GAIN_DR_FLOAT
SUPPORT:BPMFB:RB:BPM_GAIN_2FS_FLOAT
SUPPORT:BPMFB:SET:BPM_P_GAIN_DP_FLOAT
SUPPORT:BPMFB:SET:BPM_P_GAIN_DP_FLOAT_CHANGE
SUPPORT:BPMFB:SET:BPM_I_GAIN_DR_FLOAT
SUPPORT:BPMFB:SET:BPM_GAIN_2FS_FLOAT
SUPPORT:BPMFB:RB:BPM_P_GAIN_DR_FLOAT
""".split()


def main(pvnames: list[str]):
    shared_broadcaster = SharedBroadcaster()
    ctx = Context(broadcaster=shared_broadcaster)
    saw_subs = {}

    def user_callback(sub: Subscription, command):
        print(f"{sub.pv}: {command}")
        saw_subs.setdefault(sub.pv, 0)
        saw_subs[sub.pv] += 1

    pvs: list[PV] = ctx.get_pvs(*pvnames)
    for pv in pvs:
        pv.wait_for_connection()

    for pv in pvs:
        reading = pv.read()
        print(f'{pv} read back: {reading}')

    for pv in pvs:
        print(f"Subscribing to {pv}")
        sub = pv.subscribe(data_type="time")
        sub.add_callback(user_callback)

    pv = pvs[0]
    assert pv.circuit_manager is not None

    # Mimic what we saw in the log:
    pv.circuit_manager.events_off()
    pv.circuit_manager.events_on()
    pv.circuit_manager.events_off()
    pv.circuit_manager.events_on()

    time.sleep(2.0)
    ctx.disconnect()
    time.sleep(1.0)

    print("Done.\n\n")
    print(f"Total PVs: {len(pvs)}")
    print("Saw this many subscription callbacks:")

    for pv, count in saw_subs.items():
        print(pv.name, count)

    print("Total PVs that had at least one subscription: ", len(saw_subs))
    print("Total subscriptions: ", sum(count for count in saw_subs.values()))


if __name__ == '__main__':
    main(pvnames)
