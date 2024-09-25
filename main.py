import time
import transmitter
import receiver

# Dữ liệu cần truyền
# data1 = "Hello my python project of CanTP this is the project about cantp"
data1 = "abcde abcde abcde abcde abcde abcde abcde "

# Truyền dữ liệu từ transmitter
transmitter.send_data(data1)

# Duy trì chương trình
while True:
    time.sleep(1)
