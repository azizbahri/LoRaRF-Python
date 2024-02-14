from LoRaRF import SX126x
import time
import argparse
def setup_lora(LoRa,f, sf, bw, cr, power):

    # Print configuration to console
    print("\n-- LoRa Transmitter Configuration --")
    print(f"Frequency = {f} Hz")
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
    LoRa.setFrequency(f)

    # Set TX power, default power for SX1262 and SX1268 are +22 dBm and for SX1261 is +14 dBm
    # This function will set PA config with optimal setting for requested TX power
    LoRa.setTxPower(power, LoRa.TX_POWER_SX1262)                       # TX power +17 dBm using PA boost pin

    # Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
    # Receiver must have same SF and BW setting with transmitter to be able to receive LoRa packet
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
        
        
        # Loop for 1 second
        start_time = time.time()
        while time.time() - start_time < 1:
            # Your code inside the loop goes here
            LoRa.beginPacket()
            # LoRa.write(messageList, len(messageList))
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
    parser = argparse.ArgumentParser(description='LoRa Transmitter') 
    parser.add_argument("--f", type=int, default=868000000, help="Frequency in Hz")
    parser.add_argument("--sf", type=int, default=7, help="Spreading factor")
    parser.add_argument("--bw", type=int, default=125000, help="Bandwidth in Hz")
    parser.add_argument("--cr", type=int, default=4, help="Coding rate")
    parser.add_argument("--power", type=int, default=22, help="Transmit power in dBm")
    args = parser.parse_args() 
    LoRa = SX126x()
    try:
        setup_lora(LoRa,args.f, args.sf, args.bw, args.cr, args.power)
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        LoRa.end()