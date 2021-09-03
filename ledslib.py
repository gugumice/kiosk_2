
#!/usr/bin/env python3

from gpiozero import PWMLED, LED, TonalBuzzer, Buzzer, Button
from gpiozero.tones import Tone
from time import sleep, time

class pushButtons(object):
    def __init__(self,button_pins,timeout=10):
        self._buttons=[]
        for pin in button_pins:
            self._buttons.append(Button(pin))
        self.default=0
        self.timeout=timeout
        self._last_pressed=None
    def pressed(self):
        for i,b in enumerate(self._buttons):
           if b.value == 1:
               self._last_pressed=time()
               return(i)
    def timed_out(self):
        ta=False
        if self._last_pressed is None:
            return(ta)
        else:
            ta=(time()>self._last_pressed+self.timeout)
            if ta:
                self._last_pressed=None
        return(ta)
    def reset(self):
       self._last_pressed=time()

class ledButtons(object):
    def __init__(self,led_pins,buz_pin=12):
        self._leds=[]
        self._buzzer=buzzer(buz_pin)
        for pin in led_pins:
            self._leds.append(LED(pin))
    def num_leds(self):
        return(len(self._leds))

    def on(self,led_num=None,s=False):
        if s:
            self._buzzer.beep()
        if led_num is None:
            for led in self._leds:
               led.on()
        else:
            for i,led in enumerate(self._leds):
                if i == led_num:
                    led.on()
    def off(self,led_num=None):
        if led_num is None:
            for led in self._leds:
               led.off()
        else:
            for i,led in enumerate(self._leds):
                if i == led_num:
                    led.off()
    def blink(self,led=None,n=1,t=1,s=False):
        if led==None:
            for l in self._leds:
                l.blink(on_time=t,off_time=t,n=n)
        else:
            for i,l in enumerate(self._leds):
                if i == led:
                    l.blink(on_time=t,off_time=t,n=n)
        if s:
            for i in range(0,n):
                self._buzzer.beep()
                sleep(t)
        else:
            sleep(t*2*n)
    def wave(self,n=1,t=.5):
        for i in range(0,n):
            for led in self._leds:
                led.on()
                sleep(t)
            for led in reversed(self._leds):
                led.off()
                sleep(t)
            sleep(t)

class buzzer(object):
    def __init__(self,pin=12,seq=(70,80)):
        self._buzzer=TonalBuzzer(pin)
        self.seq=seq
    def beep(self,n=1,t=.1):
       for i in range(0,n):
          for tn in self.seq:
              try:
                  self._buzzer.play(Tone(midi=tn))
              except:
                  pass
              sleep(t)
              self._buzzer.stop()
          #sleep(t)

def test_pushButtons():
    BUTTON_PINS=(22,27,17)
    b=pushButtons(BUTTON_PINS)
    while True:
        print('Button {}, timed out {}'.format(b.pressed(),b.timed_out()))
        sleep(1)


def test_ledbuttons():
    LED_PINS=(13,19,26)
    t=3
    print('Testing button LEDs')
    l=ledButtons(LED_PINS)
    l.blink(n=t,t=.5,s=True)
    l.blink(n=t,t=.5,s=False)
    #return
    print(l.num_leds())
    print('all on()')
    l.on()
    sleep(t)
    print('all off')
    l.off()
    #sleep(t)
    #l.on(0)
    sleep(t)
    #return
    for i in range(0,3):
        print(i)
        l.on(i)
        sleep(t)
    for i in range(0,3):
        l.off(i)
        sleep(t)
    print('blink all')
    l.blink(n=t,t=.5)
    print('blink wawe')
    sleep(t)
    l.wave(n=6,t=.5)

def test_buzzer():
    b=buzzer(12)
    b.beep(n=5,t=.1)

def main():
    #test_ledbuttons()
    test_buzzer()
    #test_pushButtons()

if __name__=='__main__':
    main()
