#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import caproto
from caproto.server import pvproperty, PVGroup
from scipy import interpolate
# from rfac import dfb
# from rfac import PatternChannels
# from rfac import MonitorSet
# import pattern_builder

PTN_LENGTH = 65536
MON_LENGTH = 40960


class DelRPatternGroup(PVGroup):
    GEN_REFERENCE = pvproperty(value=0,
                               dtype=caproto.ChannelType.INT)
    FB = pvproperty(value=0,
                    dtype=caproto.ChannelType.DOUBLE)
    EXT = pvproperty(value=20,
                     dtype=caproto.ChannelType.DOUBLE)
    TIMMING_RISE = pvproperty(value=400.0,
                              dtype=caproto.ChannelType.DOUBLE)
    REFERENCE_PTN = pvproperty(value=np.zeros(PTN_LENGTH),  # length 65536
                               dtype=caproto.ChannelType.INT)  # short
    REFERENCE_PTN_A = pvproperty(value=np.zeros(MON_LENGTH),
                                 dtype=caproto.ChannelType.DOUBLE)
    WAVE_SPAN = pvproperty(value=2000.0,
                           dtype=caproto.ChannelType.DOUBLE)
    WAVE_DELAY = pvproperty(value=0.0,
                            dtype=caproto.ChannelType.DOUBLE)
    XAXIS_MON = pvproperty(value=np.arange(0, MON_LENGTH),
                           dtype=caproto.ChannelType.DOUBLE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        monitor_names = {
            'cav': {'name': 'CAV_A', 'len': 40960},
            'bunch': {'name': 'BPM_BUNCH_A', 'len': 40960},
            "delR": {"name": "BPM_FB_DR_A", "len": 40960},
            "delPhi": {"name": "BPM_FB_DP_A", "len": 40960},
            "2fs": {"name": "BPM_FB_2FS_A", "len": 40960}
        }
        # self.monitorset = MonitorSet(monitor_names, nowave=True)
        # self.monitorset.set_region(self.WAVE_SPAN.value, self.WAVE_DELAY.value)

    @XAXIS_MON.startup
    async def XAXIS_MON(self, instance, async_lib):
        # await instance.write(self.monitorset.xdata_for('delR'))
        await self.XAXIS_MON.write([0.] * MON_LENGTH)

    @WAVE_SPAN.putter
    async def WAVE_SPAN(self, instance, value):
        # self.monitorset.set_region(value, None)
        # await self.XAXIS_MON.write(self.monitorset.xdata_for('delR'))
        await self.XAXIS_MON.write([0.] * MON_LENGTH)
        return value

    @WAVE_DELAY.putter
    async def WAVE_DELAY(self, instance, value):
        # self.monitorset.set_region(None, value)
        # await self.XAXIS_MON.write(self.monitorset.xdata_for('delR'))
        await self.XAXIS_MON.write([0.] * MON_LENGTH)
        return value

    def resample_reference(self, value):
        f = interpolate.interp1d(self.xs, value)
        ynew = f(self.XAXIS_MON.value)
        return ynew

    @REFERENCE_PTN.putter
    async def REFERENCE_PTN(self, instance, value):
        resampled_data = self.resample_reference(value)
        # dR_ratio = dfb.ca_get('SET:MMON_BPM_FB_DR_RATIO')
        dR_ratio = 1.0
        # await self.REFERENCE_PTN_A.write(resampled_data*dR_ratio)
        await self.REFERENCE_PTN_A.write([0.] * PTN_LENGTH)
        return value

    @GEN_REFERENCE.startup
    async def GEN_REFERENCE(self, instance, async_lib):
        ptndata = self.REFERENCE_PTN.value
        # self.ptnch = PatternChannels(["BPM_REFERENCE_DR_PTN"], [ptndata])

    @GEN_REFERENCE.putter
    async def GEN_REFERENCE(self, instance, value):
        # dR_ratio = dfb.ca_get('SET:MMON_BPM_FB_DR_RATIO')
        # dR_at_FB = self.FB.value/dR_ratio
        # dR_at_EXT = self.EXT.value/dR_ratio
        # t_rise = self.TIMMING_RISE.value
        # t_ext = dfb.ca_get("SET:BPM_FB_END_A")
        # t_ext_end = dfb.ca_get("SET:BPM_FB_START_B")
        # self.period_update = dfb.ca_get("SET:PERIOD_UPDATE")
        # t_ptn = [0, t_rise, t_ext, t_ext_end, t_ext_end + (t_ext - t_rise), 2000.0]
        # dR_ptn = [dR_at_FB, dR_at_FB, dR_at_EXT, dR_at_EXT, dR_at_FB, dR_at_FB]
        # self.span_list = pattern_builder.LinearSpanList(t_ptn, dR_ptn)
        # self.xs = np.arange(0, PTN_LENGTH)*1000.0/self.period_update
        # ptndata = self.span_list.y_at_x(self.xs).astype('int16')
        # self.ptnch.set_data(0, ptndata)
        # self.ptnch.put_all()
        ptndata = [0.0] * PTN_LENGTH
        await self.REFERENCE_PTN.write(ptndata)

