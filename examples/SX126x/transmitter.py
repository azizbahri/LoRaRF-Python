from LoRaRF import SX126x
import time
import argparse

def main(LoRa = None, frequency = 868000000, sf = 7, bw = 125000, power = 22, cr = 5):

    # Print configuration to console
    print("\n-- LoRa Transmitter Configuration --")
    print(f"Frequency = {frequency} Hz")
    print(f"Spreading factor = {sf}")
    print(f"Bandwidth = {bw} Hz")
    print(f"Transmit power = +{power} dBm")
    print(f"Coding rate = {cr}")
    
    
    # Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
    # IRQ pin not used in this example (set to -1). Set txen and rxen pin to -1 if RF module doesn't have one
    busId = 0; csId = 0 
    resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1 
    
    print("Begin LoRa radio")
    if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin) :
        raise Exception("Something wrong, can't begin LoRa radio")

    LoRa.setDio2RfSwitch()
    # Set frequency 
    LoRa.setFrequency(frequency)

    # Set TX power, default power for SX1262 and SX1268 are +22 dBm and for SX1261 is +14 dBm
    # This function will set PA config with optimal setting for requested TX power
    LoRa.setTxPower(power, LoRa.TX_POWER_SX1262)                       # TX power +17 dBm using PA boost pin

    # Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
    # Receiver must have same SF and BW setting with transmitter to be able to receive LoRa packet
    print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")
    LoRa.setLoRaModulation(sf, bw, cr)

    # Configure packet parameter including header type, preamble length, payload length, and CRC type
    # The explicit packet includes header contain CR, number of byte, and CRC type
    # Receiver can receive packet with different CR and packet parameters in explicit header mode
    print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
    headerType = LoRa.HEADER_EXPLICIT                               # Explicit header mode
    preambleLength = 12                                             # Set preamble length to 12
    payloadLength = 15                                              # Initialize payloadLength to 15
    crcType = True                                                  # Set CRC enable
    LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType)

    # Set syncronize word for public network (0x3444)
    print("Set syncronize word to 0x3444")
    LoRa.setSyncWord(0x3444)

    print("\n-- LoRa Transmitter --\n")

    # Message to transmit
    message = "HeLoRa World!\0"
    messageList = list(message)
    for i in range(len(messageList)) : messageList[i] = ord(messageList[i])
    counter = 0

    # Transmit message continuously
    while True :

        # Transmit message and counter
        # write() method must be placed between beginPacket() and endPacket()
        LoRa.beginPacket()
        LoRa.write(messageList, len(messageList))
        LoRa.write([counter], 1)
        LoRa.endPacket()

        # Print message and counter
        print(f"{message}  {counter}")

        # Wait until modulation process for transmitting packet finish
        LoRa.wait()

        # Print transmit time and data rate
        print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(LoRa.transmitTime(), LoRa.dataRate()))

        # Don't load RF module with continous transmit
        time.sleep(5)
        counter = (counter + 1) % 256

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='LoRa Transmitter') 
        parser.add_argument('--frequency', type=int, help='Frequency in Hz')
        parser.add_argument('--spreading_factor', type=int, help='Spreading factor') 
        parser.add_argument('--bandwidth', type=int, help='Bandwidth in Hz') 
        parser.add_argument('--power', type=int, help='Transmit power in dBm') 
        parser.add_argument('--cr', type=int, help='Codeing rate') 
        
        args = parser.parse_args() 
        if args.cr:
            cr = args.cr
        else: cr = 5
        if args.spreading_factor: 
            sf = args.spreading_factor 
        else: sf = 7 
        if args.bandwidth: 
            bw = args.bandwidth 
        else: bw = 125000 
        if args.power: 
            power = args.power 
        else: power = 22
        args = parser.parse_args()
        if args.frequency:
            frequency = args.frequency
        else:
            frequency = 868000000
        LoRa = SX126x()
        main(LoRa, frequency, sf, bw, power, cr)
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        LoRa.end()