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

def receive_callback(status, payload):
    print(f"Received callback message {payload}")
    map_bits(status)

def setup_lora(LoRa,f, sf, bw, cr, power, prot):
    # Begin LoRa radio and set NSS, reset, busy, IRQ, txen, and rxen pin with connected Raspberry Pi gpio pins
    busId = 0; csId = 0
    resetPin = 18; busyPin = 20; irqPin = 16; txenPin = 6; rxenPin = -1
    print("Begin LoRa radio")
    
    # Set the LoRa radio
    if not LoRa.begin(busId, csId, resetPin, busyPin, irqPin, txenPin, rxenPin, prot=prot) :
        raise Exception("Something wrong, can't begin LoRa radio")
    
    # Set the callback function for receiving messages
    LoRa.onReceive(receive_callback)
    
    # Set the DIO2 pin to control the RF switch
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
    
    LoRa.setCadParams(LoRa.CAD_ON_1_SYMB, 22, 10, LoRa.CAD_EXIT_RX, 2000)
    LoRa.setCad()
    
    try:
        print("CAD Mode starting")
        while True:
            pass
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='LoRa Transmitter') 
    parser.add_argument("--f", type=int, default=868000000, help="Frequency in Hz")
    parser.add_argument("--sf", type=int, default=7, help="Spreading factor")
    parser.add_argument("--bw", type=int, default=125000, help="Bandwidth in Hz")
    parser.add_argument("--cr", type=int, default=4, help="Coding rate")
    parser.add_argument("--power", type=int, default=22, help="Transmit power in dBm")
    parser.add_argument("--prot", type=int, default=0, help="Protocol 0: LoRa, 1: FSK")
    args = parser.parse_args() 
    LoRa = SX126x()
    try:
        setup_lora(LoRa,args.f, args.sf, args.bw, args.cr, args.power, args.prot)
    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        LoRa.end()