import os
import sys
import time
import RPi.GPIO as GPIO

""" 
Autor: Dihordy Ross Lauschner - dihordyross@gmail.com - Novembro de 2020
Classe: controlador PID
Objetivo: controlar a velocidade de um cooler dado como referência a temperatura do CPU do Raspberry
Uso: para atualizar os valores de controle basta invocar o método .coolerUpdate()
     para parar o cooler basta invocar o método .coolerStop()

"""

class coolerPID:


    def __init__(self, P=10, I=10, D=1, t_atual=None):

        # do PID
        self.Kp = P
        self.Ki = I
        self.Kd = D
        
        self.t_amostra = 0.00
        self.t_atual = t_atual if t_atual is not None else time.time()
        self.t_anterior = self.t_atual
        
        self.clear()


        # do cooler
        self.pino_cooler = 18
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pino_cooler, GPIO.OUT, initial=GPIO.LOW)
        self.cooler = GPIO.PWM(self.pino_cooler, 25000) # GPIO.PWM(pino, frequência)        
        

    def clear(self):
        self.SetPoint = 50.0
        self.temp = 0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_erro = 0.0
        self.output = 0.0

    def update(self, feedback, t_atual=None):
        """Calcula o PID para dado feedback:
               u(t) = Kp * e(t) + Ki * \int_{0}^{t} * e(t)dt + Kd * {de}/{dt}
        """
        
        erro = self.SetPoint - feedback

        self.t_atual = t_atual if t_atual is not None else time.time()
        delta_t = self.t_atual - self.t_anterior
        delta_erro = erro - self.last_erro

        if (delta_t >= self.t_amostra):
            self.PTerm = self.Kp * erro
            self.ITerm += erro * delta_t


            self.DTerm = 0.0
            if delta_t > 0:
                self.DTerm = delta_erro / delta_t

            
            self.t_anterior = self.t_atual
            self.last_erro = erro

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

    def setKp(self, proportional_gain):
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        self.Kd = derivative_gain


    def setSampleTime(self, t_amostra):
        # t_amostra determina a amostragem: se o PID deve atuar ou retornar imediatamente
        self.t_amostra = t_amostra


    def coolerUpdate(self):
        # Caputra temp do CPU
        self.temp = os.popen("vcgencmd measure_temp").readline()
        self.temp = float(self.temp.replace("temp=","")[0:4])

        # atualiza PID
        self.update(self.temp)

        # normaliza valores
        pwm = -(100/1024)*self.output
        
        if pwm<0: pwm=0
        elif pwm>100: pwm=100
        
        print("ação de controle: ", pwm, " %")

        # atuação
        self.cooler.start(pwm)

    def coolerStop(self):
        # para o cooler
        self.cooler.stop()
