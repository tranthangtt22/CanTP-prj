# receiver.py
import can
import time
from cantp import CANTP

# Set up the ValueCAN interface
bus = can.interface.Bus(interface='neovi', channel=1, bitrate=1000000, receive_own_messages=False)
# bus = can.interface.Bus(interface='neovi', channel=1, bitrate=1000000)

# tp = CANTP(bus, txid=0x72F, rxid=0x727)
tp = CANTP(bus, txid=0x123, rxid=0x123)
# tp = CANTP(bus)

# Start the notifier
# notifier = can.Notifier(bus, [tp])

# # Keep the script running to allow data reception
# try:
#     while not tp.data_complete:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Receiver stopped.")

while 1:
    
    # Start the notifier
    notifier = can.Notifier(bus, [tp])

# Keep the script running to allow data reception
    try:
        while not tp.data_complete:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Receiver stopped.")
