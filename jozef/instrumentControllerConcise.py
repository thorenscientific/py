from classrl1009 import *
                                           
class rl2(rl1009):
    def __init__(self,address):
        rl1009.__init__(self)
        self.address=address
    def writeA(self,message):
        self.write(self.address,message)
    def queryA(self,message):
        return self.query(self.address,message)
    def reset(self):
        self.writeA('*RST')
        self.writeA('*CLS')

def get_instruments_list():
    r=rl1009()
    addr=[[i,r.query(i,'*IDN?')] for i in range(32)]
    return [active for active in addr if active[1]!='']

class Supply_3631a(rl2):
    def __init__(self,address):
        rl2.__init__(self,address)
    def setp6v(self,vval,ival):
        self.writeA('APPL P6V, %f,%f' % (vval,ival))
    def setp25v(self,vval,ival):
        self.writeA('APPL P25V, %f,%f' % (vval,ival))
    def meas_iv(self,channel='P6V'):
        return [float(self.queryA(('MEAS:%s? %s' % (iv,channel)))) for iv in ['CURR','VOLT']]
    def meas_iv_p25v(self):
        return self.meas_iv('P25V')
    def meas_iv_n25v(self):
        return self.meas_iv('N25V')
    def meas_iv_p6v(self):
        return self.meas_iv('P6V')
    def output(self,value='OFF'):
        self.writeA('OUTP ON') if value=='ON' else self.writeA('OUTP OFF')



    
class Multimeter_34401a(rl2):
    def __init__(self,address):
        rl2.__init__(self,address)
    def setup(self):
        self.writeA(':CONF:VOLT:DC')
    def meas(self):
        return float(self.queryA(':MEAS:VOLT:DC?'))
    def setupi(self):
        self.writeA(':CONF:CURR:DC')
    def measi(self):
        return float(self.queryA(':MEAS:CURR:DC?'))


class awg_33250a(rl2):
    def __init__(self,address):
        rl2.__init__(self,address)
        self.reset()
        self.hiz()
    def writeA(self,message):
        self.write(self.address,message)
    def queryA(self,message):
        return self.query(self.address,message)
    def hiz(self):
        self.writeA('outp:load inf')
    def pulse(self,low,high,period,width,transient):
        self.writeA('output:state off')
        self.writeA(("volt:low %f" % low))
        self.writeA(("volt:high %f" % high))
        self.writeA(("puls:per %f" % period))
        self.writeA(("puls:widt %f" % width))
        self.writeA(("puls:tran %f" % transient))
        self.writeA(("func puls"))
        self.writeA(("output:state on"))
    def dc(self,dcvalue):
        self.writeA("func dc")
        self.writeA(("volt:offs %f" % dcvalue))
        self.writeA("output:state on")
    def setdc(self,dcvalue):
        self.writeA("func dc")
        self.writeA(("volt:offs %f" % dcvalue))
    def output(self,value):
        self.writeA('OUTP ON') if value=='ON' else self.writeA('OUTP OFF')
    def readpulse(self):
        low=float(self.queryA("volt:low?"))
        high=float(self.queryA("volt:high?"))
        per=float(self.queryA("puls:per?"))
        widt=float(self.queryA("puls:widt?"))
        tran=float(self.queryA("puls:tran?"))
        return [low,high,per,widt,tran]
    def readdc(self):
        return float(self.queryA("volt:offs?"))
