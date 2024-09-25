import time
import can
from threading import Event
from enum import Enum

#Can type CAN 2.0 and CAN FD
class CAN_TYPE(Enum):
    CAN_2_0_MAX_PAYLOAD = 8  # CAN 2.0
    CAN_FD_MAX_PAYLOAD = 64  #CAN FD

# PCI types
class PCI_types(Enum):
    PCI_SF = 0x00  # Single Frame
    PCI_FF = 0x01  # First Frame
    PCI_CF = 0x02  # Consecutive Frame
    PCI_FC = 0x03  # Flow Control

class FS_types(Enum):
    FC_ERROR        = 0x00
    FC_OVERFLOW     = 0x01
    FC_WAIT         = 0x02
    FC_CONTINOUS    = 0x03


class CANTP(can.Listener):
    def __init__(self, bus, txid, rxid):
        self.bus = bus
        self.txid = txid
        self.rxid = rxid
        self.st_min_for_tx = 0x14  # 20ms
        self.blk_size_for_rx = 3   # Block size
        self.flow_ctrl_ok = Event()
        self.seq = 0
        self.received_blocks = 0
        self.data_complete = False

    def sendMessage(self, msg):
        message = can.Message(arbitration_id=self.txid, data=msg, is_extended_id=False)
        self.bus.send(message)

    def writeSingleFrame(self, data):
        data_len = len(data)
        msg = [data_len] + data + [0x00] * (8 - len(data) - 1)
        print(f"Sending Single Frame: {msg}")
        self.sendMessage(msg)

    def writeFirstFrame(self, data):
        data_len = len(data)
        msg = [0x10 | ((data_len & 0xF00) >> 8), data_len & 0xFF] + data[:6]
        print(f"Sending FF: {msg}")
        self.sendMessage(msg)
        return data[6:]

    def writeConsecutiveFrame(self, data):
        self.seq = (self.seq + 1) % 16
        frame_data = data[:7]
        msg = [0x20 | self.seq] + frame_data
        msg += [0x00] * (8 - len(msg))
        print(f"Sending CF: {msg}")
        self.sendMessage(msg)
        return data[7:]

    def writeFlowControlFrame(self):
        if self.data_complete:
            return
        msg = [0x30, self.blk_size_for_rx, self.st_min_for_tx, 0x55, 0x55, 0x55, 0x55, 0x55]
        print(f"Sending Flow Control: {msg}")
        self.sendMessage(msg)

    def writeMultiFrame(self, data):
        self.flow_ctrl_ok.clear()
        data = self.writeFirstFrame(data)
        data_len = len(data)

        while data_len:
            if not self.flow_ctrl_ok.wait(1):
                print("Flow Control timeout")
                break

            for _ in range(self.blk_size_for_rx):
                if not data_len:
                    break
                data = self.writeConsecutiveFrame(data)
                data_len = len(data)
                time.sleep(self.st_min_for_tx / 1000)

            self.flow_ctrl_ok.clear()

    def sendData(self, data):
        if isinstance(data, str):
            data = list(data.encode('utf-8'))

        if len(data) <= 7:
            self.writeSingleFrame(data)
        else:
            self.writeMultiFrame(data)

    def on_message_received(self, msg):
        can_id = msg.arbitration_id
        data = list(msg.data)

        if can_id == self.rxid:
            if self.data_complete:
                return

            if data[0] & 0xF0 == 0x00:
                self.rx_data_size = data[0]
                self.rx_data = data[1:self.rx_data_size + 1]

                try:
                    complete_message = bytes(self.rx_data).decode('utf-8')
                    print(f"Complete message received: {complete_message}")
                except UnicodeDecodeError:
                    print(f"Complete message received: {self.rx_data}")

                self.data_complete = True
                return

            if data[0] & 0xF0 == 0x10:
                self.rx_data_size = ((data[0] & 0x0F) << 8) | data[1]
                self.rx_data = data[2:8]
                self.received_blocks = 0
                self.writeFlowControlFrame()
                return

            if data[0] & 0xF0 == 0x20:
                self.rx_data += data[1:8]
                self.received_blocks += 1

                if len(self.rx_data) >= self.rx_data_size:
                    self.rx_data = self.rx_data[:self.rx_data_size]
                    try:
                        complete_message = bytes(self.rx_data).decode('utf-8')
                        print(f"Complete message received: {complete_message}")
                    except UnicodeDecodeError:
                        print(f"Complete message received: {self.rx_data}")

                    self.data_complete = True
                    return

                if self.received_blocks % self.blk_size_for_rx == 0:
                    time.sleep(0.05)
                    self.writeFlowControlFrame()

            if data[0] & 0xF0 == 0x30 and not self.data_complete:
                print(f"Received Flow Control Frame: {data}")
                self.flow_ctrl_ok.set()
