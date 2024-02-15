from LoRaRF import SX126x
import argparse
import yaml

# Bit Masks
# Bit mask for packet status
# 0 TxDone
# 1 RxDone
# 2 PreambleDetected
# 3 SyncWordValid
# 4 HeaderValid
# 5 HeaderErr
# 6 CrcErr
# 7 CadDone
# 8 CadDetected
# 9 Timeout Rx or Tx


def map_bits(int_value):
    # Define the bit mask
    bit_mask = {
        0: "TxDone",
        1: "RxDone",
        2: "PreambleDetected",
        3: "SyncWordValid",
        4: "HeaderValid",
        5: "HeaderErr",
        6: "CrcErr",
        7: "CadDone",
        8: "CadDetected",
        9: "Timeout Rx or Tx"
    }

    # Convert the integer value to binary
    binary_value = bin(int_value)[2:].zfill(10)

    # Map the bits to the bit mask and print the name of the bit
    for i, bit in enumerate(reversed(binary_value)):
        if bit == '1':
            print(f"{bit_mask[i]} : ",end="")
    print("-")

def receive_callback(self):
    # read() and available() method must be called after request() or listen() method
    message = ""
    # available() method return remaining received payload length and will decrement each read() or get() method called
    while self.available() > 1 :
        message += chr(self.read())
    print(f"Received callback message")
    print(f"Message: {message}")

    map_bits(self._statusIrq )

# def setup_lora(LoRa, f, sf, bw, cr, power, prot, preamble,fdev):
def setup_lora(LoRa, cfg):
    # Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
    busId = 0; csId = 0
    resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1
    modem_cfg = cfg['modem_cfg']
    packet_cfg = cfg['packet_cfg']

    prot = modem_cfg['protocol']
    freq = modem_cfg['frequency']

    print("Begin LoRa radio")
    if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin, prot=prot) :
        raise Exception("Something wrong, can't begin LoRa radio")

    LoRa.onReceive(receive_callback)
    LoRa.setDio2RfSwitch()
    # Set frequency
    print(f"Set frequency to {freq} Hz")
    LoRa.setFrequency(freq)

    # Set RX gain to power saving gain
    print("Set RX gain to power saving gain")
    LoRa.setRxGain(LoRa.RX_GAIN_POWER_SAVING)

    if prot == LoRa.FSK_MODEM:
        print("Set FSK modulation parameters:\n\tFrequency deviation = {fdev} kHz\n\tBitrate = 50 kbps")
        # bitrate = 50000
        # LoRa.setFskModulation(bitrate, LoRa.PULSE_NO_FILTER,LoRa.BW_46900,fdev )

        # LoRa.setFskPacket()
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

    print("\n-- LoRa Receiver Continuous --\n")

    # Request for receiving new LoRa packet in RX continuous mode
    LoRa.request(LoRa.RX_CONTINUOUS)

    # Set transmit power
    power = modem_cfg['power']
    print(f"Set transmit power to {power} dBm")
    LoRa.setTxPower(power)



    try:
        print("Waiting for incoming LoRa packet...")
        while True:
            pass
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
    # # Receive message continuously
    # while True :
    #     # Check for incoming LoRa packet
    #     if LoRa.available() :
    #         # Put received packet to message and counter variable
    #         message = ""
    #         while LoRa.available() > 1 :
    #             message += chr(LoRa.read())
    #         counter = LoRa.read()

    #         # Print received message and counter in serial
    #         print(f"{message}  {counter}")

    #         # Print packet/signal status including RSSI, SNR, and signalRSSI
    #         print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(LoRa.packetRssi(), LoRa.snr()))

    #         # Show received status in case CRC or header error occur
    #         status = LoRa.status()
    #         if status == LoRa.STATUS_CRC_ERR : print("CRC error")
    #         if status == LoRa.STATUS_HEADER_ERR : print("Packet header error")


def read_configurations(file_path):
    with open(file_path, 'r') as file:
        configurations = yaml.safe_load(file)
    return configurations


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="LoRa Receiver Continuous")
    parser.add_argument('--cfg', help='Path to the configuration file')
    parser.add_argument("--f", type=int, default=868000000, help="Frequency in Hz")
    parser.add_argument("--sf", type=int, default=7, help="Spreading factor")
    parser.add_argument("--bw", type=int, default=125000, help="Bandwidth in Hz")
    parser.add_argument("--cr", type=int, default=4, help="Coding rate")
    parser.add_argument("--power", type=int, default=22, help="Transmit power in dBm")
    parser.add_argument("--prot", type=int, default=0, help="Protocol 0: LoRa, 1: FSK")
    parser.add_argument("--preamble", type=int, default=12, help="Preamble length")
    parser.add_argument("--fdev", type=int, default=25000, help="Frequency deviation in Hz")
    args = parser.parse_args()

    if args.cfg:
        configurations = read_configurations(args.cfg)
    LoRa = SX126x()
    try:
        setup_lora(LoRa, configurations)
    except:
        LoRa.end()