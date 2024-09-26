# transmitter.py
import can
import time
from cantp import CANTP

# Set up the ValueCAN interface
# bus = can.interface.Bus(interface='neovi', channel=1, bitrate=1000000)
bus = can.interface.Bus(interface='neovi', channel=1, bitrate=1000000, receive_own_messages=False)

# tp = CANTP(bus, txid=0x727, rxid=0x72F)
tp = CANTP(bus, txid=0x123, rxid=0x123)
# tp = CANTP(bus)


notifier = can.Notifier(bus, [tp])

while 1:
        # Start the notifier
    
    # Data to send
    # data = "Hello from the transmitter on ValueCAN!"
    # data ="hello"
    print("Nhap data = ")
    data = input()

    # Send data
    tp.sendData(data)
    time.sleep(2)  # Allow time to transmit



