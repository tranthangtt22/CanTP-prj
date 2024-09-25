import can
from cantp import CANTP

# Tạo bus chung với chế độ loopback
bus = can.Bus('test', interface='virtual', receive_own_messages=True)

# Khởi tạo đối tượng nhận
receiver = CANTP(bus, 0x72F, 0x727)
can.Notifier(bus, [receiver])
