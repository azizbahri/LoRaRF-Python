# This example demonstrates how to perform a Channel Activity Detection (CAD) on the SX126x LoRa transceiver
# The CAD function is used to detect the presence of a LoRa signal on the channel

from LoRaRF import SX126x
import time
import argparse


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

def setup_lora(LoRa,cfg):
    # Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
    busId = 0; csId = 0
    resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1
    print("Begin LoRa radio")
    
    modem_cfg = cfg['modem_cfg']
    cad_cfg = cfg['cad_cfg']

    prot = modem_cfg['protocol']
    freq = modem_cfg['frequency']

    # Set the LoRa radio
    if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin, prot=prot) :
        raise Exception("Something wrong, can't begin LoRa radio")
    
    # Set the callback function for receiving messages
    LoRa.onReceive(receive_callback)
    LoRa._irqSetup(LoRa.IRQ_ALL)
    # Set the DIO2 pin to control the RF switch
    LoRa.setDio2RfSwitch()
    # Set frequency
    print(f"Set frequency to {freq} Hz")
    LoRa.setFrequency(freq)

    # Set RX gain to power saving gain
    LoRa.setRxGain(LoRa.RX_GAIN_BOOSTED)

    if prot == LoRa.LORA_MODEM:
        sf = modem_cfg['spreading_factor']
        bw = modem_cfg['bandwidth']
        cr = modem_cfg['coding_rate']
        print(f"Set modulation parameters:\n\tSpreading factor = {sf}\n\tBandwidth = {bw} Hz\n\tCoding rate = {cr}")

        LoRa.setLoRaModulation(sf, bw, cr)


        print("\n-- LoRa Configured --\n")

    cadSymbolNum = cad_cfg['cadSymbolNum']
    cadDetPeak = cad_cfg['cadDetPeak']
    cadDetMin = cad_cfg['cadDetMin']
    cadExitMode = cad_cfg['cadExitMode']
    cadTimeout  = cad_cfg['cadTimeout']
    LoRa.setCadParams(cadSymbolNum, cadDetPeak, cadDetMin, cadExitMode, cadTimeout)
    LoRa.request(LoRa.RX_CONTINUOUS)
    LoRa.setCad()
    
    try:
        print("CAD Mode starting")
        while True:
            pass
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
    finally:
        LoRa.end()


def read_configurations(file_path):
    with open(file_path, 'r') as file:
        configurations = yaml.safe_load(file)
    return configurations


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LoRa Transmitter') 
    parser.add_argument("--cfg", type=str, default="lora_cfg.yaml", help="Configuration file")
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