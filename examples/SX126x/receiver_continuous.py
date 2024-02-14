from LoRaRF import SX126x
import argparse
def receive_callback(status):
    print(f"Received callback message {status}")

def setup_lora(LoRa, f, sf, bw, cr, power):
    # Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
    busId = 0; csId = 0 
    resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1 
    print("Begin LoRa radio")
    if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin) :
        raise Exception("Something wrong, can't begin LoRa radio")

    LoRa.onReceive(receive_callback)
    LoRa.setDio2RfSwitch()
    # Set frequency
    print(f"Set frequency to {f} Hz")
    LoRa.setFrequency(f)

    # Set RX gain to power saving gain
    print("Set RX gain to power saving gain")
    LoRa.setRxGain(LoRa.RX_GAIN_POWER_SAVING)

    # Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
    print(f"Set modulation parameters:\n\tSpreading factor = {sf}\n\tBandwidth = {bw} Hz\n\tCoding rate = {cr}")
    LoRa.setLoRaModulation(sf, bw, cr)

    # Configure packet parameter including header type, preamble length, payload length, and CRC type
    print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")
    headerType = LoRa.HEADER_EXPLICIT
    preambleLength = 12
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
    print(f"Set transmit power to {power} dBm")
    LoRa.setTxPower(power)

    # Receive message continuously
    while True :
        # Check for incoming LoRa packet
        if LoRa.available() :
            # Put received packet to message and counter variable
            message = ""
            while LoRa.available() > 1 :
                message += chr(LoRa.read())
            counter = LoRa.read()

            # Print received message and counter in serial
            print(f"{message}  {counter}")

            # Print packet/signal status including RSSI, SNR, and signalRSSI
            print("Packet status: RSSI = {0:0.2f} dBm | SNR = {1:0.2f} dB".format(LoRa.packetRssi(), LoRa.snr()))

            # Show received status in case CRC or header error occur
            status = LoRa.status()
            if status == LoRa.STATUS_CRC_ERR : print("CRC error")
            if status == LoRa.STATUS_HEADER_ERR : print("Packet header error")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LoRa Receiver Continuous")
    parser.add_argument("--f", type=int, default=868000000, help="Frequency in Hz")
    parser.add_argument("--sf", type=int, default=7, help="Spreading factor")
    parser.add_argument("--bw", type=int, default=125000, help="Bandwidth in Hz")
    parser.add_argument("--cr", type=int, default=4, help="Coding rate")
    parser.add_argument("--power", type=int, default=22, help="Transmit power in dBm")
    args = parser.parse_args()

    LoRa = SX126x()
    try:
        setup_lora(LoRa,args.f, args.sf, args.bw, args.cr, args.power)
    except:
        LoRa.end()