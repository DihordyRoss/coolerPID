import time

# importa a classe coolerCpu
from CoolerPID import coolerPID

# cria objeto cooler da classe coolerCpu
cooler = coolerPID()

# rotina exemplo
while(True):
    cooler.coolerUpdate()
    print("temperatura atual:", cooler.temp ," °C \n")
    time.sleep(1)