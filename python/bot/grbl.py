# pip install pyserial

import serial,time,math
import serial.tools.list_ports as stlp

def choose_serial_connection():
    l = stlp.comports()
    if len(l) == 0:
        raise Exception('No available serial devices found')

    print('Please choose from the following serial ports.')
    for i,s in enumerate(l):
        print('({}) {}'.format(i,s))

    k = input('Please enter a number [{}-{}]'.format(0, len(l)-1))
    if len(k)==0: k=0
    return l[int(k)].device

class grbl:
    def __init__(self):
        print('(grbl)looking for serial connections.')
        name = choose_serial_connection()

        self.ser = serial.Serial(name,115200,timeout=0.2)
        print('(grbl)serial name: ',self.ser.name)
        self.linenumber = 0

        self.waitready()

    def readline(self):
        b = self.ser.readline()
        return b.decode('ascii')[:-2] # cutoff \r\n

    def command(self,string):
        print('(grbl) SENT: '+string)
        b = (string+'\n').encode('ascii')
        self.ser.write(b)
        self.ser.flush()

        self.linenumber+=1

    def wait(self, string, timeout=None, length=0):
        current = time.time()
        collected_lines = []
        print('(grbl) waiting for "'+ string+'"')
        while 1:
            if timeout is not None:
                if time.time() - current > timeout:
                    raise Exception('(grbl) waited longer than '+str(timeout))

            line = self.readline()
            if len(line)>0:
                current = time.time()
                print('(grbl) RECV: "{}"'.format(line))
                collected_lines.append(line)
                if (length==0 and line == string) or (length>0 and line[0:length] == string):
                    return collected_lines
            else:
                pass

    def waitok(self,timeout=None):
        return self.wait('ok',timeout)

    def waitready(self):
        while 1:
            try:
                self.command('$X') # clear status
                self.wait('ok', timeout=1, length=2)
                print('(grbl) Machine Ready.')
            except Exception as e:
                print(e)
            else:
                return

    # send command and wait for ok.
    def command_ok(self,c,timeout=None):
        self.command(c)
        return self.waitok(timeout)

    # below APIs are for users

    # always do homing on start.
    def home(self):
        self.command('$H') # homing
        print('(grbl) Homing...')
        self.waitok(10) # wait for homing

    def goto(self, x=None, y=None, z=None, f=None):
        # f means feedrate(mm/min)
        # use 50000 for free movement; 2000 for plotting

        # there is no need to limit speed of free movement since that's already limited by settings stored in the microcontroller EEPROM

        cmd = 'G1 '
        if f is not None: cmd += 'f{:1.2f} '.format(f)
        if x is not None: cmd += 'x{:1.2f} '.format(x)
        if y is not None: cmd += 'y{:1.2f} '.format(y)
        if z is not None: cmd += 'z{:1.2f} '.format(z)

        self.command(cmd)
        self.waitok(10)

    # obtain status word from machine
    def status_report(self):
        self.command('?')
        lines = self.wait('<', timeout=10, length=1)
        line = lines[-1]
        import re
        return re.match(r'\<(.*?)\|', line).group(1)

    # wait for all commands in buffer finish execution
    def wait_until_idle(self):
        while self.status_report().lower() != 'idle':
            time.sleep(0.5)
            pass

if __name__ == '__main__':
    g = grbl()
    g.home()
    for i in range(3):
        g.goto(f=50000)
        g.goto(x=100, y=0)
        g.goto(x=170, y=30)

        g.goto(x=200, y=100)
        g.goto(x=170, y=170)

        g.goto(x=100, y=200)
        g.goto(x=30, y=170)

        g.goto(x=0, y=100)
        g.goto(x=30, y=30)

    # don't close the serial connection before all the commands
    # finish execution. otherwise the machine may restart.
    g.wait_until_idle()
