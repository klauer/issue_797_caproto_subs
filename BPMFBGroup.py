#!/usr/bin/env python
# -*- coding: utf-8 -*-
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run, SubGroup
# from rfac import dfb
from caproto.asyncio.client import Context
import inspect
# import pprint


class BPMFBGroup(PVGroup):
    @SubGroup(prefix="MIRROR:")
    class MIRROR(PVGroup):
        BPM_P_GAIN_DP_CNST = pvproperty(value=0,
                                        dtype=caproto.ChannelType.INT,
                                        read_only=True)
        BPM_P_SHIFT_DP = pvproperty(value=0,
                                    dtype=caproto.ChannelType.INT,
                                    read_only=True)
        BPM_P_GAIN_DR_CNST = pvproperty(value=0,
                                        dtype=caproto.ChannelType.INT,
                                        read_only=True)
        BPM_P_SHIFT_DR = pvproperty(value=0,
                                    dtype=caproto.ChannelType.INT,
                                    read_only=True)
        BPM_I_GAIN_DR_CNST = pvproperty(value=0,
                                        dtype=caproto.ChannelType.INT,
                                        read_only=True)
        BPM_I_SHIFT_DR = pvproperty(value=0,
                                    dtype=caproto.ChannelType.INT,
                                    read_only=True)
        BPM_PERIOD_IACC_DR_SET = pvproperty(value=0,
                                            dtype=caproto.ChannelType.INT,
                                            read_only=True)
        BPM_GAIN_2FS_CNST = pvproperty(value=0,
                                       dtype=caproto.ChannelType.INT,
                                       read_only=True)
        BPM_GN_SHIFT_2FS = pvproperty(value=0,
                                      dtype=caproto.ChannelType.INT,
                                      read_only=True)

        def __init__(self, *args, **kwargs):
            mirror_pvs = ["BPM_P_GAIN_DP_CNST",
                          "BPM_P_SHIFT_DP",
                          "BPM_P_GAIN_DR_CNST",
                          "BPM_P_SHIFT_DR",
                          "BPM_I_GAIN_DR_CNST",
                          "BPM_I_SHIFT_DR",
                          "BPM_PERIOD_IACC_DR_SET",
                          "BPM_GAIN_2FS_CNST",
                          "BPM_GN_SHIFT_2FS"]
            self.target = {}
            for a_name in mirror_pvs:
                dict = {"name": "RBSOM", # dfb.pvname("RB"+":"+a_name),
                        "client_context": None,
                        "pv": None,
                        "subscription": None}

                self.target[a_name] = dict

            super().__init__(*args, **kwargs)

        async def _callback(self, pv, response):
            basename = pv.pv.name.split(":")[-1]
            pvname = self.prefix + basename
            await self.pvdb[pvname].write(response.data)

        async def setup_sbscription(self, targetkey):
            ctx = Context()
            target = self.target[targetkey]
            target["client_context"] = ctx
            target["pv"], = await ctx.get_pvs(target["name"])

            # Subscribe to the target PV and register self._callback.
            sbsc = target["pv"].subscribe()
            target["subscription"] = sbsc
            sbsc.add_callback(self._callback)

        @BPM_P_GAIN_DP_CNST.startup
        async def BPM_P_GAIN_DP_CNST(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_P_GAIN_DP_CNST.putter
        async def BPM_P_GAIN_DP_CNST(self, instance, value):
            gd = value
            bit_shift = self.BPM_P_SHIFT_DP.value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.BPM_P_GAIN_DP_FLOAT.write(ga)
            return value

        @BPM_P_SHIFT_DP.startup
        async def BPM_P_SHIFT_DP(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_P_SHIFT_DP.putter
        async def BPM_P_SHIFT_DP(self, instance, value):
            gd = self.BPM_P_GAIN_DP_CNST.value
            bit_shift = value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.BPM_P_GAIN_DP_FLOAT.write(ga)
            return value

        @BPM_P_GAIN_DR_CNST.startup
        async def BPM_P_GAIN_DR_CNST(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_P_GAIN_DR_CNST.putter
        async def BPM_P_GAIN_DR_CNST(self, instance, value):
            gd = value
            bit_shift = self.BPM_P_SHIFT_DR.value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.BPM_P_GAIN_DR_FLOAT.write(ga)
            return value

        @BPM_P_SHIFT_DR.startup
        async def BPM_P_SHIFT_DR(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_P_SHIFT_DR.putter
        async def BPM_P_SHIFT_DR(self, instance, value):
            gd = self.BPM_P_GAIN_DR_CNST.value
            bit_shift = value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.BPM_P_GAIN_DR_FLOAT.write(ga)
            return value

        @BPM_I_GAIN_DR_CNST.startup
        async def BPM_I_GAIN_DR_CNST(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_I_GAIN_DR_CNST.putter
        async def BPM_I_GAIN_DR_CNST(self, instance, value):
            gd = value
            bit_shift = self.BPM_I_SHIFT_DR.value
            iacc_period_set = self.BPM_PERIOD_IACC_DR_SET.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.BPM_I_GAIN_DR_FLOAT.write(ga)
            return value

        @BPM_I_SHIFT_DR.startup
        async def BPM_I_SHIFT_DR(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_I_SHIFT_DR.putter
        async def BPM_I_SHIFT_DR(self, instance, value):
            gd = self.BPM_I_GAIN_DR_CNST.value
            bit_shift = value
            iacc_period_set = self.BPM_PERIOD_IACC_DR_SET.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.BPM_I_GAIN_DR_FLOAT.write(ga)
            return value

        @BPM_PERIOD_IACC_DR_SET.startup
        async def BPM_PERIOD_IACC_DR_SET(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_PERIOD_IACC_DR_SET.putter
        async def BPM_PERIOD_IACC_DR_SET(self, instance, value):
            bit_shift = self.BPM_I_SHIFT_DR.value
            iacc_period_set = value
            gd = self.BPM_I_GAIN_DR_CNST.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.BPM_I_GAIN_DR_FLOAT.write(ga)
            return value

        @BPM_GAIN_2FS_CNST.startup
        async def BPM_GAIN_2FS_CNST(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_GAIN_2FS_CNST.putter
        async def BPM_GAIN_2FS_CNST(self, instance, value):
            gd = value
            bit_shift = self.BPM_GN_SHIFT_2FS.value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.BPM_GAIN_2FS_FLOAT.write(ga)
            return value

        @BPM_GN_SHIFT_2FS.startup
        async def BPM_GN_SHIFT_2FS(self, instance, async_lib):
            targetkey = inspect.currentframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @BPM_GN_SHIFT_2FS.putter
        async def BPM_GN_SHIFT_2FS(self, instance, value):
            gd = self.BPM_GAIN_2FS_CNST.value
            bit_shift = value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.BPM_GAIN_2FS_FLOAT.write(ga)
            return value

    @SubGroup(prefix="RB:")
    class RB(PVGroup):

        BPM_P_GAIN_DP_FLOAT = pvproperty(value=0,
                                         dtype=caproto.ChannelType.DOUBLE)
        BPM_P_GAIN_DR_FLOAT = pvproperty(value=0,
                                         dtype=caproto.ChannelType.DOUBLE)
        BPM_I_GAIN_DR_FLOAT = pvproperty(value=0,
                                         dtype=caproto.ChannelType.DOUBLE)
        BPM_GAIN_2FS_FLOAT = pvproperty(value=0,
                                        dtype=caproto.ChannelType.DOUBLE)

    @SubGroup(prefix="SET:")
    class SET(PVGroup):
        BPM_P_GAIN_DP_FLOAT = pvproperty(value=0,
                                         dtype=caproto.ChannelType.DOUBLE)
        BPM_P_GAIN_DR_FLOAT = pvproperty(value=0,
                                         dtype=caproto.ChannelType.DOUBLE)
        BPM_I_GAIN_DR_FLOAT = pvproperty(value=0,
                                         dtype=caproto.ChannelType.DOUBLE)
        BPM_GAIN_2FS_FLOAT = pvproperty(value=0,
                                        dtype=caproto.ChannelType.DOUBLE)
        BPM_P_GAIN_DP_FLOAT_CHANGE = pvproperty(value=0,
                                                dtype=caproto.ChannelType.DOUBLE)
        BPM_P_GAIN_DR_FLOAT_CHANGE = pvproperty(value=0,
                                                dtype=caproto.ChannelType.DOUBLE)
        BPM_I_GAIN_DR_FLOAT_CHANGE = pvproperty(value=0,
                                                dtype=caproto.ChannelType.DOUBLE)
        BPM_GAIN_2FS_FLOAT_CHANGE = pvproperty(value=0,
                                               dtype=caproto.ChannelType.DOUBLE)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.mirrorgrp = self.parent.MIRROR

        @BPM_P_GAIN_DP_FLOAT.startup
        async def BPM_P_GAIN_DP_FLOAT(self, instance, async_lib):
            # gd = dfb.ca_get("RB:BPM_P_GAIN_DP_CNST")
            # bit_shift = dfb.ca_get("RB:BPM_P_SHIFT_DP")
            gd = 0.0
            bit_shift = 0
            ga = gd*2.0**(-bit_shift)
            await instance.write(ga)

        def set_BPM_P_GAIN_DP_FLOAT(self, value):
            def _set_value(value):
                bit_shift = self.mirrorgrp.BPM_P_SHIFT_DP.value
                # dfb.set_delP_P_gain(value, bit_shift)

            self.set_BPM_P_GAIN_DP_FLOAT = _set_value

        @BPM_P_GAIN_DP_FLOAT.putter
        async def BPM_P_GAIN_DP_FLOAT(self, instance, value):
            if value is None:
                return instance.value
            self.set_BPM_P_GAIN_DP_FLOAT(value)
            return value

        @BPM_P_GAIN_DP_FLOAT_CHANGE.putter
        async def BPM_P_GAIN_DP_FLOAT_CHANGE(self, instance, value):
            if value == 0:
                return 0
            current_value = self.BPM_P_GAIN_DP_FLOAT.value
            new_value = current_value + value
            await self.BPM_P_GAIN_DP_FLOAT.write(new_value)
            return 0

        @BPM_P_GAIN_DR_FLOAT.startup
        async def BPM_P_GAIN_DR_FLOAT(self, instance, async_lib):
            # gd = dfb.ca_get("RB:BPM_P_GAIN_DR_CNST")
            # bit_shift = dfb.ca_get("RB:BPM_P_SHIFT_DR")
            # ga = gd*2.0**(-bit_shift)
            ga = 0.0
            await instance.write(ga)

        def set_BPM_P_GAIN_DR_FLOAT(self, value):
            def _set_value(value):
                bit_shift = self.mirrorgrp.BPM_P_SHIFT_DR.value
                dfb.set_delR_P_gain(value, bit_shift)

            self.set_BPM_P_GAIN_DR_FLOAT = _set_value

        @BPM_P_GAIN_DR_FLOAT.putter
        async def BPM_P_GAIN_DR_FLOAT(self, instance, value):
            if value is None:
                return instance.value

            self.set_BPM_P_GAIN_DR_FLOAT(value)
            return value

        @BPM_P_GAIN_DR_FLOAT_CHANGE.putter
        async def BPM_P_GAIN_DR_FLOAT_CHANGE(self, instance, value):
            if value == 0:
                return 0

            current_value = self.BPM_P_GAIN_DR_FLOAT.value
            new_value = current_value + value
            await self.BPM_P_GAIN_DR_FLOAT.write(new_value)
            return 0

        @BPM_I_GAIN_DR_FLOAT.startup
        async def BPM_I_GAIN_DR_FLOAT(self, instance, async_lib):
            # gd = dfb.ca_get("RB:BPM_I_GAIN_DR_CNST")
            # bit_shift = dfb.ca_get("RB:BPM_I_SHIFT_DR")
            # iacc_period_set = dfb.ca_get("RB:BPM_PERIOD_IACC_DR_SET")
            # ga = gd*2.0**(-bit_shift)/(iacc_period_set+1)
            ga = 0.0
            await instance.write(ga)

        def set_BPM_I_GAIN_DR_FLOAT(self, value):
            def _set_value(value):
                bit_shift = self.mirrorgrp.BPM_I_SHIFT_DR.value
                iacc_period_set = self.mirrorgrp.BPM_PERIOD_IACC_DR_SET.value
                # iacc_period = dfb.SYSCLOCK/(iacc_period_set+1)
                # ga, gd, bshift = dfb.set_delR_I_gain(value, bit_shift,
                #                                      iacc_period)

            self.set_BPM_I_GAIN_DR_FLOAT = _set_value

        @BPM_I_GAIN_DR_FLOAT.putter
        async def BPM_I_GAIN_DR_FLOAT(self, instance, value):
            if value is None:
                return instance.value

            self.set_BPM_I_GAIN_DR_FLOAT(value)
            return value

        @BPM_I_GAIN_DR_FLOAT_CHANGE.putter
        async def BPM_I_GAIN_DR_FLOAT_CHANGE(self, instance, value):
            if value == 0:
                return 0
            current_value = self.BPM_I_GAIN_DR_FLOAT.value
            new_value = current_value + value
            await self.BPM_I_GAIN_DR_FLOAT.write(new_value)
            return 0

        @BPM_GAIN_2FS_FLOAT.startup
        async def BPM_GAIN_2FS_FLOAT(self, instance, async_lib):
            # gd = dfb.ca_get("RB:BPM_GAIN_2FS_CNST")
            # bit_shift = dfb.ca_get("RB:BPM_GN_SHIFT_2FS")
            # ga = gd*2.0**(-bit_shift)
            ga = 0.0
            await instance.write(ga)

        def set_BPM_GAIN_2FS_FLOAT(self, value):
            def _set_value(value):
                bit_shift = self.mirrorgrp.BPM_GN_SHIFT_2FS.value
                dfb.set_2fs_gain(value, bit_shift)

            self.set_BPM_GAIN_2FS_FLOAT = _set_value

        @BPM_GAIN_2FS_FLOAT.putter
        async def BPM_GAIN_2FS_FLOAT(self, instance, value):
            if value is None:
                return instance.value

            self.set_BPM_GAIN_2FS_FLOAT(value)
            return value

        @BPM_GAIN_2FS_FLOAT_CHANGE.putter
        async def BPM_GAIN_2FS_FLOAT_CHANGE(self, instance, value):
            if value == 0:
                return 0

            current_value = self.BPM_GAIN_2FS_FLOAT.value
            new_value = current_value + value
            await self.BPM_GAIN_2FS_FLOAT.write(new_value)
            return 0
