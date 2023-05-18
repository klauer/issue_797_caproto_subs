#!/usr/bin/env python
# -*- coding: utf-8 -*-
import caproto
from caproto.server import pvproperty, PVGroup, ioc_arg_parser, run, SubGroup
# from rfac import BClockControl
# import rfac.setting_file as setting_file
# from rfac import dfb
from CAVFBGroup import CAVFBGroup
from BPMFBGroup import BPMFBGroup
from DelRPatternGroup import DelRPatternGroup

from caproto import config_caproto_logging
import caproto.server.common


class SupportIOC(PVGroup):
    CAVFBGroup = SubGroup(CAVFBGroup, prefix="CAVFB:")
    BPMFBGroup = SubGroup(BPMFBGroup, prefix="BPMFB:")
    DelRPatternGroup = SubGroup(DelRPatternGroup, prefix="DR_PTN:")

    @pvproperty(value=1, dtype=caproto.ChannelType.INT)
    async def IS_ALIVE(self, instance):
        return instance.value

    @pvproperty(value=0, dtype=caproto.ChannelType.DOUBLE)
    async def FREQ_BASE_CHANGE(self, instance):
        return instance.value

    @FREQ_BASE_CHANGE.putter
    async def FREQ_BASE_CHANGE(self, instance, value):
        # print("start FREQ_BASE_CHANGE %d " % (value))
        current_value = instance.group.RB.FREQ_BASE.value
        await instance.group.SET.FREQ_BASE.write(current_value + value)
        return 0  # なぜか複数回呼ばれることがあることへの対応

    @SubGroup(prefix='RB:')
    class RB(PVGroup):
        @pvproperty(value=0, dtype=caproto.ChannelType.DOUBLE)
        async def FREQ_BASE(self, instance):
            return instance.value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def CONFIG_FILE(self, instance):
            return instance.value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def LUT_FILE(self, instance):
            return instance.value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def IQ_PATTERN_FILE(self, instance):
            return instance.value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def FREQ_PATTERN_B_FILE(self, instance):
            return instance.value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def FREQ_PATTERN_T_FILE(self, instance):
            return instance.value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def DR_PATTERN_FILE(self, instance):
            return instance.value

    @SubGroup(prefix='SET:')
    class SET(PVGroup):
        @pvproperty(value=0, dtype=caproto.ChannelType.DOUBLE)
        async def FREQ_BASE(self, instance):
            return instance.value

        @FREQ_BASE.startup
        async def FREQ_BASE(self, instance, async_lib):
            # value = dfb.ca_get("SET:FREQ_VALUE")
            value = 0.0
            ioc = instance.group.parent
            #print("ioc.SET.FREQ_BASE.write :%f" % (value))
            #await ioc.RB.FREQ_BASE.write(value)
            await ioc.SET.FREQ_BASE.write(value)

        @FREQ_BASE.putter
        async def FREQ_BASE(self, instance, value):
            fmode = 0  # dfb.ca_get("SET:FREQ_SELECT")
            if 0 == fmode:
                # self.bclock_control.put_fbase(value)
                ...
            elif 1 == fmode:
                # #print("SET:FREQ_VALUE :%f" % (value))
                # dfb.ca_put("SET:FREQ_VALUE", value)
                ...

            ioc = instance.group.parent
            await ioc.RB.FREQ_BASE.write(value)
            return value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def CONFIG_FILE(self, instance):
            return instance.value

        @CONFIG_FILE.putter
        async def CONFIG_FILE(self, instance, value):
            ioc = instance.group.parent
            await ioc.RB.CONFIG_FILE.write(value)
            return value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def LUT_FILE(self, instance):
            return instance.value

        @LUT_FILE.putter
        async def LUT_FILE(self, instance, value):
            ioc = instance.group.parent
            await ioc.RB.LUT_FILE.write(value)
            return value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def IQ_PATTERN_FILE(self, instance):
            return instance.value

        @IQ_PATTERN_FILE.putter
        async def IQ_PATTERN_FILE(self, instance, value):
            ioc = instance.group.parent
            await ioc.RB.IQ_PATTERN_FILE.write(value)
            return value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def FREQ_PATTERN_B_FILE(self, instance):
            return instance.value

        @FREQ_PATTERN_B_FILE.putter
        async def FREQ_PATTERN_B_FILE(self, instance, value):
            file_dict = setting_file.load()
            # self.bclock_control = BClockControl.new_with_file(
            #     file_dict["FREQ_PATTERN_B_FILE"])

            ioc = instance.group.parent
            await ioc.RB.FREQ_PATTERN_B_FILE.write(value)
            return value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def FREQ_PATTERN_T_FILE(self, instance):
            return instance.value

        @FREQ_PATTERN_T_FILE.putter
        async def FREQ_PATTERN_T_FILE(self, instance, value):
            ioc = instance.group.parent
            await ioc.RB.FREQ_PATTERN_T_FILE.write(value)
            return value

        @pvproperty(value='', dtype=caproto.ChannelType.STRING)
        async def DR_PATTERN_FILE(self, instance):
            return instance.value

        @DR_PATTERN_FILE.putter
        async def DR_PATTERN_FILE(self, instance, value):
            ioc = instance.group.parent
            await ioc.RB.DR_PATTERN_FILE.write(value)
            return value


if __name__ == '__main__':

    # To avoid "High load. Dropped n responses."
    # デフォルト値は 0.01
    # 値を大きくしても改善しない。小さくしたほうが良いケースもある模様
    # caproto.server.common.HIGH_LOAD_TIMEOUT = 1000

    config_caproto_logging(level='INFO')
    ioc_options, run_options = ioc_arg_parser(
        default_prefix='SUPPORT:',
        desc='Run an Support IOC.',
        supported_async_libs=('asyncio',)
    )
    ioc = SupportIOC(**ioc_options)
    run_options["log_pv_names"] = True
    run(ioc.pvdb, **run_options)
