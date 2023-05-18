#!/usr/bin/env python
# -*- coding: utf-8 -*-
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run, SubGroup
# from rfac import dfb
from caproto.asyncio.client import Context
import sys
#import pprint


class CAVFBGroup(PVGroup):
    @SubGroup(prefix="MIRROR:")
    class MIRROR(PVGroup):
        CAV_P_GAIN_HN1_CNST = pvproperty(value=0,
                                         dtype=caproto.ChannelType.INT,
                                         read_only=True)
        CAV_P_GAIN_HN2_CNST = pvproperty(value=0,
                                         dtype=caproto.ChannelType.INT,
                                         read_only=True)
        CAV_P_SHIFT = pvproperty(value=0,
                                 dtype=caproto.ChannelType.INT,
                                 read_only=True)
        CAV_I_GAIN_HN1_CNST = pvproperty(value=0,
                                         dtype=caproto.ChannelType.INT,
                                         read_only=True)
        CAV_I_GAIN_HN2_CNST = pvproperty(value=0,
                                         dtype=caproto.ChannelType.INT,
                                         read_only=True)
        CAV_I_SHIFT = pvproperty(value=0,
                                 dtype=caproto.ChannelType.INT,
                                 read_only=True)
        CAV_PERIOD_IACC_SET = pvproperty(value=0,
                                         dtype=caproto.ChannelType.INT,
                                         read_only=True)

        def __init__(self, *args, **kwargs):
            mirror_pvs = ["CAV_P_GAIN_HN1_CNST",
                          "CAV_P_GAIN_HN2_CNST",
                          "CAV_P_SHIFT",
                          "CAV_I_GAIN_HN1_CNST",
                          "CAV_I_GAIN_HN2_CNST",
                          "CAV_I_SHIFT",
                          "CAV_PERIOD_IACC_SET"]
            self.target = {}
            for a_name in mirror_pvs:
                dict = {"name": "RBSOMETHING", # dfb.pvname("RB"+":"+a_name),
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

        @CAV_P_SHIFT.startup
        async def CAV_P_SHIFT(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_P_SHIFT.putter
        async def CAV_P_SHIFT(self, instance, value):
            bit_shift = value
            gd = self.CAV_P_GAIN_HN1_CNST.value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.CAV_P_GAIN_HN1_FLOAT.write(ga)
            gd = self.CAV_P_GAIN_HN2_CNST.value
            ga = gd*2.0**(-bit_shift)
            await self.parent.RB.CAV_P_GAIN_HN2_FLOAT.write(ga)
            return value

        @CAV_P_GAIN_HN1_CNST.startup
        async def CAV_P_GAIN_HN1_CNST(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_P_GAIN_HN1_CNST.putter
        async def CAV_P_GAIN_HN1_CNST(self, instance, value):
            bit_shift = self.CAV_P_SHIFT.value
            ga = value*2.0**(-bit_shift)
            await self.parent.RB.CAV_P_GAIN_HN1_FLOAT.write(ga)
            return value

        @CAV_P_GAIN_HN2_CNST.startup
        async def CAV_P_GAIN_HN2_CNST(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_P_GAIN_HN2_CNST.putter
        async def CAV_P_GAIN_HN2_CNST(self, instance, value):
            bit_shift = self.CAV_P_SHIFT.value
            ga = value*2.0**(-bit_shift)
            await self.parent.RB.CAV_P_GAIN_HN2_FLOAT.write(ga)
            return value

        @CAV_I_GAIN_HN1_CNST.startup
        async def CAV_I_GAIN_HN1_CNST(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_I_GAIN_HN1_CNST.putter
        async def CAV_I_GAIN_HN1_CNST(self, instance, value):
            bit_shift = self.CAV_I_SHIFT.value
            iacc_period_set = self.CAV_PERIOD_IACC_SET.value
            ga = (value*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.CAV_I_GAIN_HN1_FLOAT.write(ga)
            return value

        @CAV_I_GAIN_HN2_CNST.startup
        async def CAV_I_GAIN_HN2_CNST(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_I_GAIN_HN2_CNST.putter
        async def CAV_I_GAIN_HN2_CNST(self, instance, value):
            bit_shift = self.CAV_I_SHIFT.value
            iacc_period_set = self.CAV_PERIOD_IACC_SET.value
            ga = (value*2.0**(-bit_shift))/(iacc_period_set+1)
            # print(value, bit_shift, iacc_period_set)
            await self.parent.RB.CAV_I_GAIN_HN2_FLOAT.write(ga)
            return value

        @CAV_I_SHIFT.startup
        async def CAV_I_SHIFT(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_I_SHIFT.putter
        async def CAV_I_SHIFT(self, instance, value):
            bit_shift = value
            iacc_period_set = self.CAV_PERIOD_IACC_SET.value
            gd = self.CAV_I_GAIN_HN1_CNST.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.CAV_I_GAIN_HN1_FLOAT.write(ga)

            gd = self.CAV_I_GAIN_HN2_CNST.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.CAV_I_GAIN_HN2_FLOAT.write(ga)
            return value

        @CAV_PERIOD_IACC_SET.startup
        async def CAV_PERIOD_IACC_SET(self, instance, async_lib):
            targetkey = sys._getframe().f_code.co_name
            await self.setup_sbscription(targetkey)

        @CAV_PERIOD_IACC_SET.putter
        async def CAV_PERIOD_IACC_SET(self, instance, value):
            bit_shift = self.CAV_I_SHIFT.value
            iacc_period_set = value
            gd = self.CAV_I_GAIN_HN1_CNST.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.CAV_I_GAIN_HN1_FLOAT.write(ga)

            gd = self.CAV_I_GAIN_HN2_CNST.value
            ga = (gd*2.0**(-bit_shift))/(iacc_period_set+1)
            await self.parent.RB.CAV_I_GAIN_HN2_FLOAT.write(ga)
            return value

    @SubGroup(prefix="RB:")
    class RB(PVGroup):
        CAV_P_GAIN_HN1_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)
        CAV_I_GAIN_HN1_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)
        CAV_P_GAIN_HN2_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)
        CAV_I_GAIN_HN2_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)

    @SubGroup(prefix="SET:")
    class SET(PVGroup):
        CAV_P_GAIN_HN1_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)
        CAV_I_GAIN_HN1_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)
        CAV_P_GAIN_HN2_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)
        CAV_I_GAIN_HN2_FLOAT = pvproperty(value=0,
                                          dtype=caproto.ChannelType.DOUBLE)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.mirrorgrp = self.parent.MIRROR

        @CAV_P_GAIN_HN1_FLOAT.putter
        async def CAV_P_GAIN_HN1_FLOAT(self, instance, value):
            bit_shift = self.mirrorgrp.CAV_P_SHIFT.value
            # dfb.set_cav_P_gain(value, bit_shift, hn=1)
            return value

        @CAV_I_GAIN_HN1_FLOAT.putter
        async def CAV_I_GAIN_HN1_FLOAT(self, instance, value):
            bit_shift = self.mirrorgrp.CAV_I_SHIFT.value
            iacc_period = self.mirrorgrp.CAV_PERIOD_IACC_SET.value
            # iacc_period = dfb.SYSCLOCK/(iacc_period+1)
            # ga, gd, bshift = dfb.set_cav_I_gain(value, bit_shift, hn=1,
            #                                     IACC_PERIOD=iacc_period)
            return value

        @CAV_P_GAIN_HN2_FLOAT.putter
        async def CAV_P_GAIN_HN2_FLOAT(self, instance, value):
            bit_shift = self.mirrorgrp.CAV_P_SHIFT.value
            # dfb.set_cav_P_gain(value, bit_shift, hn=2)
            return value

        @CAV_I_GAIN_HN2_FLOAT.putter
        async def CAV_I_GAIN_HN2_FLOAT(self, instance, value):
            bit_shift = self.mirrorgrp.CAV_I_SHIFT.value
            iacc_period = self.mirrorgrp.CAV_PERIOD_IACC_SET.value
            # iacc_period = dfb.SYSCLOCK/(iacc_period+1)
            # ga, gd, bshift = dfb.set_cav_I_gain(value, bit_shift, hn=2,
            #                                     IACC_PERIOD=iacc_period)
            return value
