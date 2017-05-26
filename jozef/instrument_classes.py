import pyvisa
from visa import *
import ctypes
import time

class Parallel_port:
    def __init__(self):
        self.addr='LPT1'
    def send_byte(self,data):
        ctypes.windll.inpout32.Out32(0x37a, 1)
        ctypes.windll.inpout32.Out32(0x378, data)
        time.sleep(0.1)
        ctypes.windll.inpout32.Out32(0x37a, 0)
    def read_byte(self,data):
        read=[]
        read.append(ctypes.windll.inpout32.Inp32(0x378))
        return read
    
class Oven_delta2300:
    def __init__(self):
        self.addr='LPT1'
    def temp(self):
        pass
    
class Supply_6625a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("CLR")
    def iset(self,chan,ival):
        self.write("ISET%i,%f" % (chan,ival))
    def vset(self,chan,vval):
        self.write("VSET%i,%f" % (chan,vval))
    def ovset(self,chan,vval):
        self.write("OVSET%i,%f" % (chan,vval))
    def output(self,chan,val):
        if val=='ON':
            self.write("OUT%i,1" % chan)
        else:
            self.write("OUT%i,0" % chan)
    def meas_iv(self,chan):
        v=self.write("VOUT?%i" % chan)
        i=self.write("IOUT?%i" % chan)
        return [i,v]

class Supply_6633a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("CLR")
    def iset(self,ival):
        self.write("ISET %f" % ival)
    def vset(self,vval):
        self.write("VSET %f" % vval)
    def ovset(self,vval):
        self.write("OVSET %f" % vval)
    def output(self,val): 
        if val=='ON':
            self.write("OUT 1")
        else:
            self.write("OUT 0")
    def meas_iv(self):
        v=self.ask_for_values("VOUT?")[0]
        i=self.ask_for_values("IOUT?")[0]
        return [i,v]
                
class Source_8648c(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("*RST")
    def set_freq(self,freq):
        self.write(":FREQ:CW %fMHz" % freq)
    def set_power(self,ampl):
        self.write(":POWER:AMPLITUDE %f" % ampl)
    def output(self,val):
        self.write(":OUTPUT %s" % val)

class NF_meter_8970b(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("PR")
    def set_rffreq(self,freq):
        self.write("1.3 SP %dEN" % freq)
    def set_lofreq(self,freq):
        self.write("3.1 SP %dEN" % freq)
    def setup(self):
        self.write("IN;IN;IN;IN;") #increase smoothing
        self.write("M2") # measure gain and NF
    def cal(self):
        raw_input("Connect noise source to NF meter input: Press Enter")
        self.write("CA")
        raw_input("Press Enter when calibration is done")
    def meas(self):
        x=self.ask_for_values("T2;T1;H1") #execute;hold;give all data
        return x[1:]

class Spec_an_8562e(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.clear()
    def set_cenfreq(self,freq):
        self.write("CF %fMHz" % freq)
    def set_span(self,span):
        self.write("SP %fMHz" % span)
    def set_reflev(self,reflev):
        self.write("RL %f" % reflev)
    def set_atten(self,atten):
        self.write("AT %f" % atten)
    def set_marker_norm(self,freq):
        self.write("MKN %fMHz" % freq)
    def set_marker_peak(self):
        self.write("MKPK")
    def meas(self,cfreq,span,reflev,atten,navg):
        self.set_cenfreq(cfreq)
        self.set_span(span)
        self.set_reflev(reflev)
        self.set_atten(atten)
        self.set_marker_norm(cfreq)
        return self.meas_navg(navg)
    def meas_navg(self,navg):
        return self.ask_for_values("VAVG %d;SNGLS;TS;MKA?" % navg)[0]
    
class Impedance_an_4192a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.clear()
    def setup(self):
        self.write("A5B2F1N1T3V1D1EX") # esoteric setup commands for dB error and phase error
    def set_freq(self,freq):
        self.write("FR+%fENEX" % freq)
    def meas(self,navg):
        gerr=0
        pha=0
        for i in range(navg):
            self.trigger()
            self.wait_for_srq()
            x=self.ask_for_values('')
            #print x
            gerr=gerr+x[0]
            pha=pha+x[1]
        gerr=gerr/navg
        pha=pha/navg
        return [gerr,pha]

class Multimeter_34401a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.clear()
    def setup(self):
        self.write(":CONF:VOLT:DC")
    def meas(self):
        return self.ask_for_values(":MEAS:VOLT:DC?")[0]
    def setupi(self):
        self.write(":CONF:CURR:DC")
    def measi(self):
        return self.ask_for_values(":MEAS:CURR:DC?")[0]

class ssSupply_3631a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("*RST;*CLS")
    def setp6v(self,vval,ival):
        self.write("APPL P6V, %f, %f" % (vval,ival))
    def setp25v(self,vval,ival): 
        self.write("APPL P25V, %f, %f" % (vval,ival))
    def output(self,val):
        if val=='ON':
            self.write("OUTP ON")
        else:
            self.write("OUTP OFF")
    def meas_iv_p6v(self):
        i=self.ask_for_values("MEAS:CURR? P6V")[0]
        v=self.ask_for_values("MEAS:VOLT? P6V")[0]
        return [i,v]
    def meas_iv_p25v(self):
        i=self.ask_for_values("MEAS:CURR? P25V")[0]
        v=self.ask_for_values("MEAS:VOLT? P25V")[0]
        return [i,v]





class SignalGenerator_MG3633A(pyvisa.visa.Instrument):
    def __init__(self,addr=10):
        pyvisa.visa.Instrument.__init__(self,'GPIB::'+str(addr))
        self.reset()
        self.setFreq()
        self.setOut()
        self.write("RF")
    def reset(self):
        self.write("*RST;*CLS")
    def setFreq(self,Freq=10e6):
        self.write("FR%s" % Freq)
    def setOut(self,Out=-100): 
        self.write("OL%s" % Out)
    def output(self,val):
        if val=='ON':
            self.write("RO")
        else:
            self.write("RF")
    def meas(self,command):
        return self.ask_for_values(str(command)+"OA")[0]
    #meas("FR") or mes("OL")
    def measFreq(self):
        return self.meas("FR")
    def measOut(self): #sign is  not returned
        return self.meas("OL")

#type: SP 62 to set gpib address
#type:SP 63 to read gpib address
# to set frequency send:  FR100KHZ
# to read frequency: FROA
# dis/en able output: RF RO
# to set output level send: OL-30DBM
    



#----------------------------------------
## high-Z output
# OUTPut:LOAD INFinity
# OUTP:LOAD 50
# APPLy: SIN 1e6,1,0
# APPL:DC 2.0
class awg_33250a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("*RST;*CLS")
    def hiz(self):
        self.write("outp:load inf")
    def pulse(self,low,high,period,width,transient):
        self.write("output:state off")
        self.write("volt:low %f" % low)
        self.write("volt:high %f" % high)
        self.write("puls:per %f" % period)
        self.write("puls:widt %f" % width)
        self.write("puls:tran %f" % transient)
        self.write("func puls")
        self.write("output:state on")
    def dc(self,dcvalue):
        self.write("func dc")
        self.write("volt:offs %f" % dcvalue)
        self.write("output:state on")
    def setdc(self,dcvalue):
        self.write("func dc")
        self.write("volt:offs %f" % dcvalue)
    def output(self,val):
        if val=='ON':
            self.write("OUTP ON")
        else:
            self.write("OUTP OFF")
# read function: case of functions
    def readpulse(self):
        low=self.ask_for_values("volt:low?")
        high=self.ask_for_values("volt:high?")
        period=self.ask_for_values("puls:per?")
        width=self.ask_for_values("puls:widt?")
        transient=self.ask_for_values("puls:tran?")
        return [low,high,period,width,transient]
    def readdc(self):
        return self.ask_for_values("volt:offs?")






#----------------------------------------
class Supply_3631a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.write("*RST;*CLS")
    def vset(self,chan,vval):
        self.write("INST:NSEL %i" % chan)
        self.write("VOLT:TRIG %f" % vval)
        self.write("TRIG:SOURCE IMM")
        self.write("INIT")
    def iset(self,chan,vval):
        self.write("INST:NSEL %i" % chan)
        self.write("CURR:TRIG %f" % vval)
        self.write("TRIG:SOURCE IMM")
        self.write("INIT")
    def meas_iv(self,chan):
        self.write("INST:NSEL %i" % chan)
        v=self.ask_for_values("MEAS:VOLT?")[0]
        i=self.ask_for_values("MEAS:CURR?")[0]
        return [i,v]
    def setp6v(self,vval,ival):
        self.write("APPL P6V, %f,%f" % (vval,ival))
    def setp25v(self,vval,ival): 
        self.write("APPL P25V, %f,%f" % (vval,ival))
    def meas_iv_p6v(self):
        i=self.ask_for_values("MEAS:CURR? P6V")[0]
        v=self.ask_for_values("MEAS:VOLT? P6V")[0]
        return [i,v]
    def meas_iv_p25v(self):
        i=self.ask_for_values("MEAS:CURR? P25V")[0]
        v=self.ask_for_values("MEAS:VOLT? P25V")[0]
        return [i,v]
    def output(self,val):
        if val=='ON':
            self.write("OUTP ON")
        else:
            self.write("OUTP OFF")



class Multimeter_3478a(pyvisa.visa.Instrument):
    def __init__(self,addr):
        pyvisa.visa.Instrument.__init__(self,addr)
        self.addr=addr
    def reset(self):
        self.clear()
    def setup(self):
        self.write("H0")
    def meas(self):
        return self.ask_for_values("H1")[0]


#esnb 1 operation complete

#if you make a single measurement like JM
# it will be faster
# use most functions only to generate
# the statements, not actually write them
# this way you can combine multiple statements
# together and send them to the instrument
# at the same time.
# should query be a wrapper?
# default write, if query add question mark and
# ask for values.
class SpectrumAnalyzer_4396B(pyvisa.visa.GpibInstrument):
    def __init__(self, addr=0,send_end=True):
        pyvisa.visa.Instrument.__init__(self,'GPIB::'+str(addr))
        self.write(';'.join([self.reset(),self.setFreqCent(),self.setDisplay(),self.sweep(0)]))
    def joinColon(self,*kwargs):
        return ';'.join(kwargs)
    def writeMany(self,*kwargs):
        self.write(';'.join(kwargs))
    def avme(self,noAvg=1):
        return self.joinColon(":NUMG %s" % noAvg,self.average(noAvg),self.findpeak())
    def avMeasure(self,noAvg=1,timeUnit=1):
        self.writeMany(self.setsrq(),self.avme(noAvg))
        self.wait_for_srq(noAvg*timeUnit) 
        return self.ask_for_values(":MKRVAL?")[0]
    def averagemeas(self,noAvg=1):
        self.write(self.marker("ON"))
        if noAvg>1:
            self.write(self.sweep(1))
        else:
            self.write(self.sweep(0))
        time.sleep(noAvg*self.sweepTime())
        self.write(self.findpeak())
        m=self.markervalue()[0]
        return m
    def reset(self):
        return "*RST;*CLS;:MEAS S"
    def setFreqCent(self,Center=10e6,Span=1e6):
        return ":SENS:FREQ:CENT %s;SPAN %s" % (Center,Span)
    def setFreqBand(self,Start=9e6,Stop=11e6):
        return ":SENS:FREQ:STOP %s;STAR %s" % (Stop,Start)
    def setDisplay(self,ref=0,div=10):
        return ":DISP:TRAC:Y:RLEV %s;PDIV %s" % (ref,div)
    def startquery(self):  #a question mark is a query
        return "SENS:FREQ:STAR?"
    def sweep(self,on=1):
        if (on==1):
            a=":CONT"
        else:
            a=":SING"
        return a
    def findpeak(self):
        return ":MKR ON;SEAM PEAK"
        #:CALC:EVAL:Y:XPOS:PEAK
    def marker(self,statusstring): #ON or OFF
        return "MKR %s" % statusstring
    def average(self,numberstring):
        return ":SENS:AVER:STAT ON;CLE;COUN %s" % numberstring
    def disableaverage(self):
        self.write(":SENS:AVER:STAT OFF")
    def attenuation(self,numberstring): #attenuation programmable only on channel s
        self.write(":SENS:POW:AC:ATT:AUTO OFF;:ATT %s" % numberstring)
    def autoattenuation(self):
        self.write("SENS:POW:AC:ATT:AUTO ON")
    def markervalue(self):
        return self.ask_for_values("MKRVAL?")
    def outputmarker(self):
        return self.ask_for_values("OUTPMKR?")
    def sweepTime(self):
        return float(self.ask(":SENS:SWE:TIME?"))
    def setsrq(self):
        return "CLES;ESNB 1;*SRE 4"



## set up for serial polling
#sa.write("CLES;ESNB 1;*SRE 4")
#sa.write(sa.avme(4))
## the class of the instrument has to be gpib
## you need to handle timeout events 
#sa.wait_for_srq(5)
#sa.ask_for_values("MKRVAL?")
#

# also set the number of group measurements
# because a single sweep will not do for averaging.
#
#        w2=":NUMG 4"
        #trigger->number of groups
        # to measure a number of sweeps
        #numg
        #:NUMG 4
        #:INIT:CONT OFF
        #:SENS:SWE:COUN 4
        #:INIT:IMM   to trigger measurement
