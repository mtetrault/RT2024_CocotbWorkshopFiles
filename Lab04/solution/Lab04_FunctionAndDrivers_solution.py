# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0
# Simple tests for an adder module
import os
import random
import sys
from pathlib import Path

import debugpy

import cocotb
from cocotb.runner import get_runner
from cocotb.triggers import Timer
from cocotb.clock import Clock

from cocotbext.uart import UartSource, UartSink



async def init(dut):
    c = Clock(dut.clk, 100, 'ns')
    await cocotb.start(c.start())


    dut.rx_uart_serial_in.value = 1
    dut.reset.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 10, rising=True)
    dut.reset.value = 0
    await cocotb.triggers.ClockCycles(dut.clk, 10, rising=True)
    return



async def PostTestDelay(dut):
    await cocotb.triggers.ClockCycles(dut.clk, 10, rising=True)
    dut.reset.value = 1
    await cocotb.triggers.ClockCycles(dut.clk, 4, rising=True)
    return

# cocotb decorator indicating a test to run with simulator.
# multiple tests may be included in the same python module (file)
@cocotb.test()
async def sqrt_test(dut):
    #debugpy.listen(5678)
    #debugpy.wait_for_client()
    #debugpy.breakpoint()

    uart_driver = UartSource(dut.rx_uart_serial_in, baud=1000000, bits=8)
    uart_sink   = UartSink(dut.tx_uart_serial_out, baud=1000000, bits=8)


    await init(dut)

    # Send arbitrary value, then wait for transaction to complete
    for TestValue in [4, 9, 16, 50]:
        await uart_driver.write(TestValue.to_bytes(1, "little"))
        await uart_driver.wait()
        result = await uart_sink.read(count=1)
        RecoveredValue = int.from_bytes(result, "little")
        print(RecoveredValue)

    # wait at the end
    await PostTestDelay(dut)


def simulation_runner():
    """Simulate the adder example using the Python runner.

    This file can be run directly or via pytest discovery.
    """
    hdl_toplevel_lang = "vhdl"
    simulator_program = "ghdl"
	
    WaveformOptionVcd = "--vcd=Lab04_waveforms.vcd"

    proj_path = Path(__file__).resolve().parent.parent

    vhdl_sources = []
    vhdl_sources += [proj_path / "hdl" / "uart_rx.vhd"]
    vhdl_sources += [proj_path / "hdl" / "uart_tx.vhd"]
    vhdl_sources += [proj_path / "hdl" / "sqrt_conv.vhd"]
    vhdl_sources += [proj_path / "hdl" / "RT2024MySystemTop.vhd"]

    # equivalent to setting the PYTHONPATH environment variable
    sys.path.append(str(proj_path / "solution"))

    runner = get_runner(simulator_program)
	
    runner.build(
        vhdl_sources=vhdl_sources,
        hdl_toplevel="rt2024mysystemtop",
        always=True,
    )
	
    runner.test(hdl_toplevel="rt2024mysystemtop", 
				test_module="Lab04_FunctionAndDrivers_solution",
				plusargs=[WaveformOptionVcd, "--ieee-asserts=disable"])


if __name__ == "__main__":
    simulation_runner()
