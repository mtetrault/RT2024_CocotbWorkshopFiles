"""

Code snippets used for the RT2024 cocotb workshop


"""

###################################################
# for remote debugging, with GUI attach command
# place in cocotb test function, not in main
import debugpy
debugpy.listen(port_number)
debugpy.wait_for_client()
debugpy.breakpoint()



###################################################
# Create clock object, than start it in a thread.
from cocotb.clock import Clock
c = Clock(dut.clock_signal  , 25, 'ns')
await cocotb.start(c.start())


###################################################
# Wait for clock cycles
cocotb.triggers.ClockCycles(dut.clockname, nbrClocks, rising=True)

###################################################
# Control signal, either single bit or busses.
dut.signal_name.value = 1
dut.bus_name.value = 10


###################################################
# Python basic assertion. If values are different,
# raises an error.
assert dut.signal_name.value == expected_result

###################################################
# UART extensions. 
from cocotbext.uart import UartSource, UartSink
# create the objects
uart_driver = UartSource(dut.signal_name, baud=9600, bits=16)
uart_sink   = UartSink(dut.signal_name, baud=9600, bits=16)

# change logging level for this component, if you want to reduce messages
import logging
self.uart_driver.log.setLevel(logging.DEBUG)

"""
 use the driver/sink objects to send and receive.
 the functions below are blocking (they wait until
 
 uart_driver.write : takes a bytes array as argument,
                     here, Value contains a number, like 300
                     and the .to_bytes member converts it to
                     a list of bytes indicated by NbrBytes.
 uart_driver.write : waits for the .write member to finish
 uart_sink.read    : waits for the specified number of bytes,
                     and returns a ByteArray object.
"""
await uart_driver.write(Value.to_bytes(NbrBytes, "little")) 
await uart_driver.wait()
# read command
result = await uart_sink.read(count=6)
# print ByteArray as bytes
print(bytes(result))

###################################################
# Convert from bytes to integer
# https://www.geeksforgeeks.org/how-to-convert-bytes-to-int-in-python/
RecoveredValue = int.from_bytes(bytesObject, "little")


###################################################
# Function with time delay elements, use async 
# keyword and pass dut with other parameters
async def my_function(dut, param1, param2):
    pass


###################################################
# cocotb test must be preceded by decorator.
# multiple tests may be included in the same 
# python module (file)
@cocotb.test()
async def my_test(dut):
    pass

###################################################
# Cocotb test with only a wait command. Useful to confirm
# that GHDL compiles all the modules and can start
# without errors
from cocotb.triggers import Timer
@cocotb.test()
async def do_nothing_test():
    # https://docs.cocotb.org/en/stable/triggers.html#cocotb.triggers.Timer
    # Do nothing for 100 ns
    await Timer(100, units='ns')
    pass
    
    
###################################################
# Loop in lockstep through two lists
TestValues = [1, 2, 3, 4]
ExpectedValues = [5, 6, 7, 8]
for Test, Expected in zip(TestValues, ExpectedValues):
    print(Test, Expected)



