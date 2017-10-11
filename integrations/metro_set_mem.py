from serial import Serial, SEVENBITS, STOPBITS_ONE, PARITY_EVEN
from time import sleep

#ser = Serial("/dev/ttyUSB0", 600, SEVENBITS, PARITY_EVEN, STOPBITS_ONE)
ser = Serial("/dev/cu.UC-232AC", 600, SEVENBITS, PARITY_EVEN, STOPBITS_ONE)
STX = chr(2)
ETX = chr(3)
EOT = chr(4)
ENQ = chr(5)
NL = chr(10)
PAD = chr(127)
NULL = chr(0)

addr = "01" # low bit says write
def wr(x):
        oput = [c for c in PAD + PAD + x + PAD + PAD]
        #oput = [c for c in x]
        byten = ser.write(oput)

        print oput
        print byten

slp = 1 # sometimes even smaller works, sometimes need to retry with this

col = "B" # magic numbers
ver = "004"
mempos = "01"

wr(EOT)
sleep(slp)
wr(addr + ENQ)
sleep(slp)

row = "1"
wr(STX + row + col + ver + mempos + "D + Laurin metron" + chr(123) + "ytt" + chr(124) + " +" + ETX + "p")
sleep(slp)
wr(EOT)

wr(EOT)
sleep(slp)
wr(addr + ENQ)
sleep(slp)

row = "2"
wr(STX + row + col + ver + mempos + "D ++ metro display ++" + ETX + "p")
sleep(slp)
wr(EOT)
