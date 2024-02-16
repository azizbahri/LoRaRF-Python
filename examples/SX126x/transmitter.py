from LoRaRF import SX126x
import time
import argparse
import yaml

def setup_lora(LoRa,cfg):
    # Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
    # IRQ pin not used in this example (set to -1). Set txen and rxen pin to -1 if RF module doesn't have one
    busId = 0; csId = 0 
    resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1 
    
    modem_cfg = cfg['modem_cfg']
    packet_cfg = cfg['packet_cfg']

    prot = modem_cfg['protocol']
    freq = modem_cfg['frequency']

    print("Begin LoRa radio")
    if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin,prot=prot) :
        raise Exception("Something wrong, can't begin LoRa radio")

    LoRa.setDio2RfSwitch()
    # Set frequency 
    LoRa.setFrequency(freq)

    # Set TX power, default power for SX1262 and SX1268 are +22 dBm and for SX1261 is +14 dBm
    # This function will set PA config with optimal setting for requested TX power
    power = modem_cfg['power']
    LoRa.setTxPower(power, LoRa.TX_POWER_SX1262)                       # TX power +17 dBm using PA boost pin

    if prot == LoRa.FSK_MODEM:
        bitrate = modem_cfg['bitrate']
        fdev = modem_cfg['frequency_deviation']
        bw = modem_cfg['bandwidth']
        pulse_shape = modem_cfg['pulse_shape']
        print(f"Set modulation parameters:\n\tBitrate = {bitrate} bps\n\tFrequency deviation = {fdev} Hz\n\tBandwidth = {bw} Hz\n\tPulse shape = {pulse_shape}")
        LoRa.setFskModulation(bitrate, pulse_shape,bw,fdev )

        preambleLength = packet_cfg['preamble_length']
        preambleDetector = packet_cfg['preamble_detector']
        syncWordLength = packet_cfg['sync_word_length']
        addrComp = packet_cfg['address_comparator']
        packetType = packet_cfg['packet_type']
        payloadLength = packet_cfg['payload_length']
        crcType = packet_cfg['crc_type']
        whitening = packet_cfg['whitening']
        print(f"Set packet parameters:\n\tPreamble length = {preambleLength}\n\tPreamble detector = {preambleDetector}\n\tSync word length = {syncWordLength}\n\tAddress comparator = {addrComp}\n\tPacket type = {packetType}\n\tPayload length = {payloadLength}\n\tCRC type = {crcType}\n\tWhitening = {whitening}")
        LoRa.setFskPacket(preambleLength, preambleDetector, syncWordLength, addrComp, packetType, payloadLength, crcType, whitening)
    elif prot == LoRa.LORA_MODEM:
        sf = modem_cfg['spreading_factor']
        bw = modem_cfg['bandwidth']
        cr = modem_cfg['coding_rate']
        print(f"Set modulation parameters:\n\tSpreading factor = {sf}\n\tBandwidth = {bw} Hz\n\tCoding rate = {cr}")

        LoRa.setLoRaModulation(sf, bw, cr)

        # Configure packet parameter including header type, preamble length, payload length, and CRC type
        print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
        headerType = LoRa.HEADER_EXPLICIT
        preambleLength = packet_cfg['preamble_length']
        payloadLength = 15
        crcType = True
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

def read_configurations(file_path):
    with open(file_path, 'r') as file:
        configurations = yaml.safe_load(file)
    return configurations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LoRa Transmitter') 
    parser.add_argument('--cfg', help='Path to the configuration file')
    parser.add_argument("--f", type=int, default=868000000, help="Frequency in Hz")
    parser.add_argument("--sf", type=int, default=7, help="Spreading factor")
    parser.add_argument("--bw", type=int, default=125000, help="Bandwidth in Hz")
    parser.add_argument("--cr", type=int, default=4, help="Coding rate")
    parser.add_argument("--power", type=int, default=22, help="Transmit power in dBm")
    parser.add_argument("--prot", type=int, default=0, help="Protocol 0: LoRa, 1: FSK")
    args = parser.parse_args() 
    
    if args.cfg:
        configurations = read_configurations(args.cfg)
    LoRa = SX126x()
    try:
        setup_lora(LoRa, configurations)
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        LoRa.end()