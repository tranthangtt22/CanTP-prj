import can
from cantp import CANTP


# Tạo bus chung với chế độ loopback
bus = can.Bus('test', interface='virtual', receive_own_messages=True)

# Khởi tạo đối tượng truyền
transmitter = CANTP(bus, 0x727, 0x72F)
can.Notifier(bus, [transmitter])

def send_data(data):
    transmitter.sendData(data)
