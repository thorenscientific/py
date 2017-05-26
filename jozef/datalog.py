#! c:\Python26\python.exe
# -*- coding: cp1252 -*-

#order dcCorrelation to minimize the number of hookups.
# J. Adut 5/21/2010

import math
import csv
import pyvisa
from visa import *
from numpy import arange,array
from instrument_classes import *
import operator
import itertools

#test: increase global test counter by 1, reset sub-test number to 0,
#      increase sub-test number for each dlog statement
#
# connect to instruments ###########

awg= awg_33250a('GPIB::11')
awg.reset()
awg.hiz()

# def vcm_vcc_supply:
#       def __init__(self,adress=7):
#               pyvisa.visa.Instreument.__init__(self,'GPIB::'+str(address))
#               self.reset()
#               self.setp6v(1.5,0.05)
#               self.setp25v(5.0,0.2)
#               self.output('OFF')
#       def __update__(self):
#               self.i25=self.meas_iv_p25v()[0]
                
#short pwradj to vcc
vcm_vcc_supply = Supply_3631a('GPIB0::7')
vcm_vcc_supply.reset()
vcm_vcc_supply.setp6v(1.5,0.05)
vcm_vcc_supply.setp25v(5.0,0.2)
vcm_vcc_supply.output("ON")
vcm_vcc_supply.output("OFF")

inp_inm_supply = Supply_3631a('GPIB0::5')
inp_inm_supply.reset()
inp_inm_supply.setp6v(0.1,0.2)
inp_inm_supply.setp25v(2.4,0.2)
inp_inm_supply.output("ON")
inp_inm_supply.output("OFF")

inpA=Multimeter_34401a('GPIB0::25') #current meter
inmA=Multimeter_34401a('GPIB0::26')
inpA.reset()
inpA.setupi()
inmA.reset()
inmA.setupi()

outp_mm=Multimeter_3478a('GPIB0::23') 
outm_mm=Multimeter_3478a('GPIB0::24') 


##################### open file
basedir='c:/Characterization/test'
todaysDate='/20101223'
##DC board 1, part number 5
dutName='/LTC6417revB_dcCor1'


testName='/DCcorrelation'
##########################################
def testEsdDiode(terminal,forceVoltage,currentLimit):
        inp_inm_supply.output("OFF")
        if forceVoltage>0:
                potential=terminal+"and Vcc=0"
        else:
                potential="Vcc=0 and "+terminal
     
        raw_input("Test 1.0 or 2.0: Connect inp_inm p6v between" +potential +":")
        print "Applying ",forceVoltage
        inp_inm_supply.setp6v(abs(forceVoltage),currentLimit)
        inp_inm_supply.output("ON")
        inp_inm_supply.meas_iv_p6v()
        a=inp_inm_supply.meas_iv_p6v()
        inp_inm_supply.output("OFF")
        return a


def power(status='OFF'):
        if status!='OFF':
                status='ON'
        vcm_vcc_supply.output(status)                
        inp_inm_supply.output(status)
        awg.output(status)

def setControlsPwr(Vcc,Vcm,inp,inm,pwr):
        vcm_vcc_supply.setp25v(Vcc,0.250)
        vcm_vcc_supply.setp6v(Vcm,0.02)
        inp_inm_supply.setp6v(inp,0.2)
        inp_inm_supply.setp25v(inm,0.2)

        awg.hiz()
        awg.setdc(pwr) #output is not turned on by default
                            
def defaultPowerup(Vcc=5.0,Vcm=1.25):
        power('OFF')
        vcm_vcc_supply.reset()
        inp_inm_supply.reset()
        awg.reset()
        setControlsPwr(Vcc,Vcm,Vcm,Vcm,Vcc)                  
        power('ON')         
        #supply current
        return supplyCurrent()

def printDefaultHookup():
        d=dlog(10)
        d.Comment("Default power up.")
        d.Comment("Inst: hookup vcm_vcc")
        d.Comment("Inst: hookup inp_inm")
        d.Comment("Inst: hookup awg->pwradj")
        d.Comment("Inst: short hi->cc")
        d.Comment("Inst: float shdn")                  


def supplyCurrent():
        time.sleep(0.25)
        return vcm_vcc_supply.meas_iv_p25v()[0]

def pmdiffavg(p,m):
        return [p,m,p-m,0.5*(p+m)]

#belongs in class?
def measureInputs(type):
        time.sleep(1)  #wait for it to settle?
        if type=="v":
                [na,inpV]=inp_inm_supply.meas_iv_p6v()
                [na,inmV]=inp_inm_supply.meas_iv_p25v()
                return pmdiffavg(inpV,inmV)
        elif type=='i':
                inpI=inpA.measi()
                inmI=inmA.measi()
                return pmdiffavg(inpI,inmI)
        else: #for setup1, measure voltage on GPIB 25 and 26
                inpV=inpA.meas()
                inmV=inmA.meas()
                return pmdiffavg(inpV,inmV)
                 
def measureOutputs():
        time.sleep(1) #wait for settling?
        op=outp_mm.meas()
        om=outm_mm.meas()
        return pmdiffavg(op,om)


def fileprint(f,astring):
        print astring
        f.write(str(astring))
        f.write("\n")
##########################################
class dlog:
        def __init__(self,testNo=0):
                self.lineNo=0
                self.testNo=testNo
                print "TEST %d" % self.testNo
        def Print(self,*args):
                print self.testNo,self.lineNo,",".join(args)
                self.lineNo=self.lineNo+1
        #def Print2(self,result,unit,format='5.3',message='CHAN 1 VOH'):
        def Print2(self,result,line='DLOG A MA 5.2 "PADJ @5V +/-IN=VCM=1.25V POST TRIM"'):
                message=line.split('"')[1]
                unit=line.split()[2]
                format=line.split()[3]
                if unit=='MV' or unit=='MA' or unit=='MOHMS':
                        result=result*1e3
                elif unit=='KV' or unit=='KA' or unit=='KOHMS':
                        result=result/1e3
                elif unit=='UV' or unit=='UA' or unit=='UOHMS':
                        result=result*1e6
                elif unit=='NV' or unit=='NA' or unit=='NOHMS':
                        result=result*1e9
                else: #'V','A','OHMS','V/V','DB'
                        result
                #unit: (m,k,u,n)(V,A,Ohm)
                formatString="\t%d.%d\t%"+format+"f\t%s\t%s"
                print formatString % (self.testNo,self.lineNo,result,unit,message)
                self.lineNo=self.lineNo+1
        def Comment(self,*args):
                print self.testNo,self.lineNo,",".join(args)

                

##define another class to store voltages and currents at each test
##  then test statements simplify to applying formulas          
##########################################
#### dcTest1516
def test10():
    power('OFF')                  
    printDefaultHookup()
    raw_input("Press enter to measure supply current:")
    d=dlog(10)
    d.Print2(defaultPowerup(),'DLOG A MA 5.2 "+IS @5V +/-IN=VCM=1.25V VCL=3.3"')
    power('OFF')

def test12():
    d=dlog(12)
    d.Comment("Shutdown current")
    d.Comment("Inst: shdn->vcc")
    raw_input("Press enter to measure supply current:")
    d.Print2(defaultPowerup(),'DLOG X MA 5.1  "ISY IN SDN @5V SDN @ 5V"')
    power('OFF')
    raw_input("Float shdn")

def test15():
    #print "Test 15: Post Trim, Measure pwradj current: Cannot do!! not from awg!"
    d=dlog(15)
    a=defaultPowerup()
    d.Print2(0,'DLOG A MA 5.2 "PADJ  @5V +/-IN=VCM=1.25V POST TRIM"') 
    d.Print2(0,'DLOG A MA 5.2 "VCC1  @5V +/-IN=VCM=1.25V POST TRIM"') 
    a=defaultPowerup(5.5,1.25)
    d.Print2(a,'DLOG A MA 5.2 "+IS @5.5V +/-IN=VCM=1.25V POST TRIM"')
    a=defaultPowerup()
    d.Print2(a,'DLOG A MA 5.2 "+IS @5V +/-IN=VCM=1.25V POST TRIM"')

def test16():
    d=dlog(16)#testNumber=0
    power('OFF')
    for pwrsweep in arange(5,-0.001,-0.5):
        setControlsPwr(5.0,1.25,1.25,1.25,pwrsweep)
        power('ON')
        a=supplyCurrent()
        d.Print2(pwrsweep,'DLOG X V 5.1 "POWER ADJ PIN VOLTAGE"')
        d.Print2(a,'DLOG X1 MA 5.1 "ISY @ POWER ADJ VOLTAGE"')
    d.Print2(a,'DLOG X1 MA 5.1 "ISY @ POWER ADJ VOLTAGE"')


def test20(inp=1.85,inm=0.65,dlogNo=20):
    setControlsPwr(5.0,1.25,inp,inm,5.0)
    power('ON')
    [inpV,inmV,v1,na]=measureInputs('v')
    [inpI,inmI,i1,na]=measureInputs('i')
    #? false statement ?
    i1=0.5*i1
    d=dlog(dlogNo)
    d.Print2(inpI,'DLOG D1 MA 5.3 "IIN+ @5V +IN=1.85V -IN=0.65V VCM=1.25"')
    d.Print2(inpV,'DLOG E1 V 5.3 "VIN+ @5V +IN=1.85V -IN=0.65V VCM=1.25"')
    d.Print2(inmV,'DLOG E2 V 5.3 "VIN- @5V +IN=1.85V -IN=0.65V VCM=1.25"')
    d.Print2(inmI,'DLOG D2 MA 5.3 "IIN- @5V +IN=1.85V -IN=0.65V VCM=1.25"')
    d.Print2(v1,'DLOG E3 V 5.3 "V1=VIN+ - VIN-"')
    d.Print2(i1,'DLOG D3 MA 5.3 "I1=AVERAGE IIN+ / IIN-"')
    return [v1,i1]


def test21(inp=0.65,inm=1.85,dlogNo=21):
    setControlsPwr(5.0,1.25,inp,inm,5.0)
    power('ON')
    [inpV,inmV,v1,na]=measureInputs('v')
    [inpI,inmI,i1,na]=measureInputs('i')
    i1=0.5*i1
    d=dlog(dlogNo)
    d.Print2(inpI,'DLOG D4 MA 5.3 "IIN- @5V +IN=0.65V -IN=1.85V VCM=1.25"')
    d.Print2(inpV,'DLOG E4 V 5.3 "VIN+ @5V +IN=0.65V -IN=1.85V VCM=1.25"')
    d.Print2(inmV,'DLOG E5 V 5.3 "VIN- @5V +IN=0.65V -IN=1.85V VCM=1.25"')
    d.Print2(inmI,'DLOG D5 MA 5.3 "IIN+ @5V +IN=0.65V -IN=1.85V VCM=1.25"')
    d.Print2(v1,'DLOG E6 V 5.3 "V2=VIN+ - VIN-"')
    d.Print2(i1,'DLOG D6 MA 5.3 "I2=AVERAGE IIN+ / IIN-"')
    return [v1,i1]



def test22():
    rindiff=(v1-v2)/(i1-i2)
    d=dlog(22)
    #default currents are in mA, therefore default resistance is in kOhm.
    d.Print2(rindiff,'DLOG R2 KOHMS 5.3 "RIN DIFF @5V DIFFIN=+/-1.2V VCM=1.25V"')
    power('OFF')

#check your setup, outputs  are not symmetric.
def test30():
    printDefaultHookup()
    setControlsPwr(5.0,1.25,5,0.0,5.0)
    power('ON')
    [inpI,inmI,na,na]=measureInputs('i')
    [outp,outm,na,na]=measureOutputs()
    d=dlog(30)
    d.Print2(inpI,'DLOG A MA 5.2 "IIN+ -IN=0V +IN=5V @5V VCM=1.25V"')
    d.Print2(outp,'DLOG B1 V 5.3 "FUNCT SWING IN+ @5V IN+=5V IN-=0V"')
    d.Print2(inmI,'DLOG A MA 5.2 "IIN- +IN=5V -IN=0V @5V VCM=1.25"')
    d.Print2(outm,'DLOG B2 V 5.3 "FUNCT SWING IN- @5V IN+=5V IN-=0V"')
    setControlsPwr(5.0,1.25,0.0,5.0,5.0)
    [outp,outm,na,na]=measureOutputs()
    power('OFF')
    d.Print2(outm,'DLOG B4 V 5.3 "FUNCT SWING IN- @5V IN+=0V IN-=5V"')
    d.Print2(outp,'DLOG B3 V 5.3 "FUNCT SWING IN+ @5V IN+=0V IN-=5V"')


def test33():
    setControlsPwr(5.0,1.25,2.4,0.1,5.0)
    power('ON')
    #setControlsPwr(5.0,1.45,2.4,0.1,5.0)
    #average output measurements?
    [op,om,na,na]=measureOutputs()
    d=dlog(33)
    d.Print2(op,'DLOG A V 5.3 "+OUT 0MA    @5V IN=2.4V/0.1V VCM=1.25V"')
    d.Print2(om,'DLOG A V 5.3 "-OUT 0MA    @5V IN=2.4V/0.1V VCM=1.25V"')
    d.Print2(0,'DLOG A V 5.3 "-OUT -100MA @5V IN=2.4V/0.1V VCM=1.25V"')
    d.Print2(0,'DLOG A V 5.3 "+OUT +100MA @5V IN=2.4V/0.1V VCM=1.25V"')
    d.Print2(0,'DLOG A V 5.3 "+OUT -100MA @5V IN=0.1V/2.4V VCM=1.25V"')
    d.Print2(0,'DLOG A V 5.3 "-OUT +100MA @5V IN=0.1V/2.4V VCM=1.25V"')


def test36(inp=1.85,inm=0.65,dlogNo=36):
    setControlsPwr(5.0,1.25,inp,inm,5.0)
    power('ON')
    [inpV,inmV,diffIn1,cmIn1]=measureInputs("v")
    [op,om,diffOut1,cmOut1]=measureOutputs()
    d=dlog(dlogNo)
    d.Print2(diffIn1 ,'DLOG B1 V 5.3 "@5V IN=1.85V/0.65V VCM=1.25V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT @5V DIFFIN=+1.2V"')
    d.Print2(op ,'DLOG A V 5.3 "+OUT @5V DIFFIN=+1.2V"')
    d.Print2(0 ,'DLOG B2 V 5.3 "DIFF_OUT @5V DIFFIN=+1.2V 1167"')
    d.Print2(diffOut1 ,'DLOG A V 5.3 "DIFF_OUT @5V DIFFIN=+1.2V MMDIFF"')
    return [diffOut1,diffIn1]

def test37(inp=0.65,inm=1.85,dlogNo=37):
    setControlsPwr(5.0,1.25,inp,inm,5.0)
    power('ON')
    [inpV,inmV,diffIn1,cmIn1]=measureInputs("v")
    [op,om,diffOut1,cmOut1]=measureOutputs()
    d=dlog(dlogNo)
    d.Print2(diffOut1,'DLOG A V 5.3 "DIFF_OUT @5V DIFFIN=-1.2V MMDIFF"')
    d.Print2(0 ,'DLOG B4 V 5.3 "DIFF_OUT @5V DIFFIN=-1.2V 1167"')
    d.Print2(op ,'DLOG A V 5.3 "+OUT @5V DIFFIN=-1.2V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT @5V DIFFIN=-1.2V"')
    d.Print2(diffIn1 ,'DLOG B3 V 5.3 "@5V IN 0.65V/1.85V VCM=1.25V"')
    return [diffOut1,diffIn1]

def test38():
    diffGain=(diffOut1-diffOut2)/(diffIn1-diffIn2)
    diffGain_dB=20*math.log10(abs(diffGain))
    d=dlog(38)
    d.Print2(diffGain ,'DLOG C V/V 5.3 "GDIFF @5V DIFFIN=+/-1.2V"')
    d.Print2(diffGain_dB ,'DLOG A DB 5.2 "GDIFF @5V VCM=1.25V"')

def test50():
    a=defaultPowerup()
    d=dlog(50)
    setControlsPwr(5.0,1.25,1.25,1.25,5.0)
    [inpI,inmI,na,na]=measureInputs('i')
    d.Print2(inpI ,'DLOG A UA 5.2 "IB IN+=IN-=VCM=1.25V @5V"')
    d.Print2(inmI ,'DLOG A UA 5.2 "IB IN-=IN+=VCM=1.25V @5V"')

def test80(Vcc=4.75,Vcm=1.35,dlogNo=80):
    raw_input("Short inp(from::5) and inm with a cable\n")
    setControlsPwr(Vcc,Vcm,Vcm,Vcm,Vcc)
    power('ON')
    [op,om,offset1,oCM]=measureOutputs()
    [na,cc1]=vcm_vcc_supply.meas_iv_p25v()
    d=dlog(dlogNo)
    d.Print2(op ,'DLOG A V 5.3 "+OUT @4.75V +IN=-IN=VCM=1.35V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT @4.75V +IN=-IN=VCM=1.35V"')
    d.Print2(offset1 ,'DLOG A2 MV 5.3 "VOS @4.75V +IN=-IN=VCM=1.35V"')
    return [cc1,offset1]

def test81(Vcc=5.5,Vcm=1.8,dlogNo=81):
    raw_input("Short inp(from::5) and inm with a cable")
    setControlsPwr(Vcc,Vcm,Vcm,Vcm,Vcc)
    power('ON')
    [op,om,offset2,oCM]=measureOutputs()
    [na,cc2]=vcm_vcc_supply.meas_iv_p25v()
    d=dlog(dlogNo)
    d.Print2(op ,'DLOG A V 5.3 "+OUT @5.5V +IN=-IN=VCM=1.8V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT @5.5V +IN=-IN=VCM=1.8V"')
    d.Print2(offset2 ,'DLOG A3 MV 5.3 "VOS @5.5V +IN=-IN=VCM=1.8V"')
    offsetDiff=abs(offset2-offset1)
    if offsetDiff<1e-6:
        offsetDiff=1e-12
    psrr=20*math.log10((cc2-cc1)/offsetDiff)
    d.Print2(offsetDiff ,'DLOG A UV 5.1 "DELTA VOS @4.75V TO 5.5V"')
    d.Print2(psrr ,'DLOG A DB 5.2 "PSRR @4.75V/5.5V CLAMP=3.3V/0V"')
    return [cc2,offset2]

def test90(inpm=0.65,dlogNo=90):
    #(should you short inputs physically?)
    #raw_input("short inp and inm with a cable")
    setControlsPwr(5.0,1.25,inpm,inpm,5.0)
    power('ON')
    [inpV,inmV,na,inV1]=measureInputs('v')
    [inpA,inmA,na,inI1]=measureInputs('i')
    inI1=2*inI1  #multiply by two  suspicious?
    [op,om,offset1,oCM]=measureOutputs()
    d=dlog(dlogNo)
    d.Print2(op ,'DLOG A V 5.3 "+OUT +IN=-IN=0.65V VCM=1.25V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT +IN=-IN=0.65V VCM=1.25V"')
    d.Print2(inV1 ,'DLOG E1 V 5.3 "VIN @5V +IN=-IN=0.65V VCM=1.25"')
    d.Print2(inI1 ,'DLOG D1 UA 5.2 "IIN @5V +IN=-IN=0.65V VCM=1.25"')
    d.Print2(offset1 ,'DLOG A MV 5.3 "VOS @5V IN=0.65V VCM=1.25V MMDIFF"')
    d.Print2(0 ,'DLOG A1 MV 5.3 "VOS @5V +IN=-IN=0.65V VCM=1.25V 1167"')
    return [inI1,inV1,offset1]


def test91(inpm=1.85,dlogNo=91):
    #(should you short inputs physically?)
    #raw_input("short inp and inm with a cable")
    setControlsPwr(5.0,1.25,inpm,inpm,5.0)
    power('ON')
    [inpV,inmV,na,inV1]=measureInputs('v')
    [inpA,inmA,na,inI1]=measureInputs('i')
    inI1=2*inI1 #convert from mA to uA
    #multiply by two above suspicious?
    [op,om,offset1,oCM]=measureOutputs()
    d=dlog(dlogNo)
    d.Print2(0 ,'DLOG A3 MV 5.3 "VOS @5V +IN=-IN=1.85V VCM=1.25V 1167"')
    d.Print2(op ,'DLOG A V 5.3 "+OUT +IN=-IN=1.85V VCM=1.25V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT +IN=-IN=1.85V VCM=1.25V"')
    d.Print2(inV1 ,'DLOG E2 V 5.3 "VIN @5V +IN=-IN=1.85V VCM=1.25"')
    d.Print2(inI1 ,'DLOG D2 UA 5.2 "IIN @5V +IN=-IN=1.85V VCM=1.25"')
    d.Print2(offset1 ,'DLOG A MV 5.3 "VOS @5V IN=1.85V VCM=1.25V MMDIFF"')
    return [inI1,inV1,offset1]
              
def test92():
    offsetDiff=abs(offset1-offset2)
    inVdiff=abs(inV1-inV2)
    if offsetDiff<1e-6:
        offsetDiff=1e-12
    cmrr=20*math.log10(inVdiff/offsetDiff)
    inIdiff=inI2-inI1
    rincm=(1.85-0.65)/(inIdiff/2)
    d=dlog(92)
    d.Print2(offsetDiff,'DLOG A UV 5.1 "DELTA VOS +/-IN=0.65V TO 1.85V VCM=1.25V"')
    d.Print2(cmrr ,'DLOG A DB 5.2 "CMRR @5V IN=0.65V TO 1.85V VCM=1.25V"')
    d.Print2(inIdiff ,'DLOG D3 UA 5.2 "DELTA IIN +/-IN=0.65V TO 1.85V VCM=1.25V"')
    d.Print2(rincm ,'DLOG A KOHMS 5.3 "RINCM @5V IN=0.65V TO 1.85V VCM=1.25V"')
    raw_input("Remove the cable shorting inp and inm.")
    
def test95(inpm=0.1,dlogNo=95):
    setControlsPwr(5.0,1.25,inpm,inpm,5.0)
    power('ON')
    [inpV1,inmV1,dontcare,inAvg1]=measureInputs("v")
    [op1,om1,dontcare,outAvg1]=measureOutputs()
    d=dlog(dlogNo)
    d.Print2(op1 ,'DLOG A V 5.3 "+OUT +/-IN=0.1V VCM=1.25V CLAMPS=3.3V/0V"')
    d.Print2(om1 ,'DLOG A V 5.3 "-OUT +/-IN=0.1V VCM=1.25V CLAMPS=3.3V/0V"')
    d.Print2(outAvg1 ,'DLOG A V 5.3 "IVRMIN @5V +/-IN=0.1V VCM=1.25V"')
    return [inAvg1,outAvg1]

def test96(inpm=2.4,dlogNo=96):
    setControlsPwr(5.0,1.25,inpm,inpm,5.0)
    power('ON')
    [inpV1,inmV1,dontcare,inAvg1]=measureInputs("v")
    [op1,om1,dontcare,outAvg1]=measureOutputs()
    d=dlog(dlogNo)
    d.Print2(op1 ,'DLOG A V 5.3 "+OUT +/-IN=2.4V VCM=1.25V CLAMPS=3.3V/0V"')
    d.Print2(om1 ,'DLOG A V 5.3 "-OUT +/-IN=2.4V VCM=1.25V CLAMPS=3.3V/0V"')
    d.Print2(outAvg1 ,'DLOG A V 5.3 "IVRMAX @5V +/-IN=2.4V VCM=1.25V"')
    return [inAvg1,outAvg1]

def test100():
    setControlsPwr(5.0,1.25,2.4,0.1,5.0)
    [inpV,inmV,inDM,inCM]=measureInputs("v")
    [om1,op1,na,na]=measureOutputs()
    d=dlog(100)
    d.Print2(inDM ,'DLOG A1 V 5.3 "VDIFFIN @5V IN=2.4V/0.1V VCM=1.25V"')
    d.Print2(op1 ,'DLOG E V 5.3 "VSWINGMAX +OUT @5V DIFFIN=+2.3V NOLOAD"')
    d=dlog(101)
    d.Print2(0 ,'DLOG A V 5.3 "+OUT SRC 50MA IN=+2.3V -OUT SINK 50MA"')
    d.Print2(0 ,'DLOG A V 5.3 "-OUT SINK 50MA IN=+2.3V +OUT SRC 50MA"')
    dlog(102).Print2(om1 ,'DLOG A V 5.3 "VSWINGMIN -OUT @5V DIFFIN=+2.3V NOLOAD"')
    dlog(104).Print2(0 ,'DLOG H1 V 5.3 "DIFFOUT @5V IN=+2.3V NO LOAD 1167"')

    setControlsPwr(5.0,1.25,0.1,2.4,5.0)
    [inpV,inmV,inDM,inCM]=measureInputs("v")
    [om2,op2,na,na]=measureOutputs()
    d=dlog(110)
    d.Print2(inDM ,'DLOG A2 V 5.3 "VDIFFIN @5V IN=0.1V/2.4V VCM=1.25V"')
    d.Print2(op2 ,'DLOG A V 5.3 "VSWINGMIN +OUT @5V DIFFIN=-2.3V NOLOAD"')
    d=dlog(111)
    d.Print2(0 ,'DLOG A V 5.3 "+OUT SINK 50MA IN=-2.3V -OUT SRC 50MA"')
    d.Print2(0 ,'DLOG A V 5.3 "-OUT SRC 50MA IN=-2.3V +OUT SINK 50MA"')
    d.Print2(om2 ,'DLOG A V 5.3 "VSWINGMAX -OUT @5V DIFFIN=-2.3V NOLOAD"')
    dlog(114).Print2(0 ,'DLOG H2 V 5.3 "DIFFOUT @5V IN=-2.3V NO LOAD 1167"')
    dlog(115).Print2(op1-om2 ,'DLOG A V 5.3 "DIFFOUT @5V IN=-2.3V NO LOAD MM DIFF"')


    
##############################################################
def test120():
    power('OFF')
    d=dlog(120)
    d.Comment("\nTest 120: Awg->clhi")
    raw_input("pwradj shorted to vcc")
    setControlsPwr(5.0,1.25,0.1,2.4,2.0)
    power('ON')
    [inpV1,inmV1,dontcare,inAvg1]=measureInputs("v")
    [op,om,oDM,oCM]=measureOutputs()
    d.Print2(op ,'DLOG A V 5.3 "+OUT +/-IN=0.1V/2.4V CLHI=2V CLLO=0.5V"')
    d.Print2(op-0.5 ,'DLOG A MV 5.3 "OFFSET CLLO TO +OUT CLAMPS=2V/0.5V"')
    d.Print2(om ,'DLOG A V 5.3 "-OUT +/-IN=0.1V/2.4V CLHI=2V CLLO=0.5V"')
    d.Print2(om-2.0 ,'DLOG A MV 5.3 "OFFSET CLHI TO -OUT CLAMPS=2V/0.5V"')

    #new tests
    #d.Print2(0 ,'DLOG A V 5.3 "+OUT +/-IN=0.1V/2.4V CLHI=1.5V CLLO=1V"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLLO TO +OUT CLAMPS=1.5V/1.0V"')
    #d.Print2(0 ,'DLOG A V 5.3 "-OUT +/-IN=0.1V/2.4V CLHI=1.5V CLLO=1V"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLHI TO -OUT CLAMPS=1.5V/0.5V"')
    #d.Print2(0 ,'DLOG A V 5.3 "+OUT +/-IN=0.1/2.4V CLHI=2.25V CLLO=0.25"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLLO TO +OUT CLAMPS=2.25V/0.25V"')
    #d.Print2(0 ,'DLOG A V 5.3 "-OUT +/-IN=0.1/2.4V CLHI=2.25V CLLO=0.25"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLHI TO -OUT CLAMPS=2.25V/0.25V"')

def test121():
    setControlsPwr(5.0,1.25,2.4,0.1,2.0)
    [inpV1,inmV1,dontcare,inAvg1]=measureInputs("v")
    [op,om,oDM,oCM]=measureOutputs()
    d=dlog(121)
    
    d.Print2(om ,'DLOG A V 5.3 "-OUT +/-IN=2.4V/0.1V CLHI=2V CLLO=0.5V"')
    d.Print2(om-0.5 ,'DLOG A MV 5.3 "OFFSET CLLO TO -OUT CLAMPS=2V/0.5V"')
    d.Print2(op ,'DLOG A V 5.3 "+OUT +/-IN=2.4V/0.1V CLHI=2V CLLO=0.5V"')
    d.Print2(op-2.0 ,'DLOG A MV 5.3 "OFFSET CLHI TO +OUT CLAMPS=2V/0.5V"')
    #new tests
    #d.Print2(0 ,'DLOG A V 5.3 "-OUT +/-IN=2.4V/0.1V CLHI=1.5V CLLO=1V"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLLO TO -OUT CLAMPS=1.5V/1V"')
    #d.Print2(0 ,'DLOG A V 5.3 "+OUT +/-IN=2.4V/0.1V CLHI=2V CLLO=0.5V"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLHI TO +OUT CLAMPS=2V/0.5V"')
    #d.Print2(0 ,'DLOG A V 5.3 "-OUT +/-IN=2.4V/0.1V CLHI=2V CLLO=0.5V"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLLO TO -OUT CLAMPS=2V/0.5V"')
    #d.Print2(0 ,'DLOG A V 5.3 "+OUT +/-IN=2.4V/0.1V CLHI=2V CLLO=0.5V"')
    #d.Print2(0 ,'DLOG A MV 5.3 "OFFSET CLHI TO +OUT CLAMPS=2V/0.5V"')

    
##############################################################
#### DCSetup1    
##############################################################    
                  
def test65(Vcm=0.65,dlogNo=65):
    power('OFF')
    d=dlog(dlogNo)
    d.Comment("\nSetup1: Connect GPIB::25 voltmeter on inp.")
    d.Comment("\nSetup1: Connect GPIB::26 voltmeter on inm.")
    d.Comment("\nSetup1: Connect GPIB::7 p6v on pin vcm,")
    d.Comment("\nSetup1: GBIB::5, GPIB::11 are floating.")
    raw_input("\nSetup1: Connect pwradj->vcc")
    setControlsPwr(5.0,Vcm,1.25,1.25,5.0)
    power('ON')
    [na,cmV1]=vcm_vcc_supply.meas_iv_p6v()
    [op1,om1,diffOut1,avgOut1]=measureOutputs()
    [inp1,inm1,na,na]=measureInputs('vava')
    d.Print2(op1 ,'DLOG A2 V 5.3 "+OUT INPUT FLOAT VCM=0.65V"')
    d.Print2(cmV1 ,'DLOG A V 5.3 "MEAS VCM VOLTAGE"')
    d.Print2(inp1 ,'DLOG A V 5.3 "+IN=-IN=FLOAT VCM=0.65V"')
    d.Print2(inm1 ,'DLOG A V 5.3 "-IN=+IN=FLOAT VCM=0.65V"')
    d.Print2(om1 ,'DLOG A1 V 5.3 "-OUT INPUT FLOAT VCM=0.65V"')
    d.Print2(avgOut1 ,'DLOG A3 V 5.3 "AVG +/-OUT @5V INPUT FLOAT VCM=0.65V"')
    return [cmV1,avgOut1]    

def test66(Vcm=1.85,dlogNo=66):
    power('OFF')
    raw_input("\nSetup1: Connect pwradj->vcc")
    setControlsPwr(5.0,Vcm,1.25,1.25,5.0)
    power('ON')
    [na,cmV1]=vcm_vcc_supply.meas_iv_p6v()
    [op1,om1,diffOut1,avgOut1]=measureOutputs()
    [inp1,inm1,na,na]=measureInputs('vava')
    d=dlog(dlogNo)
    d.Print2(om1 ,'DLOG A1 V 5.3 "-OUT INPUT FLOAT VCM=1.85V"')
    d.Print2(cmV1 ,'DLOG A V 5.3 "MEAS VCM VOLTAGE"')
    d.Print2(inp1 ,'DLOG A V 5.3 "+IN=-IN=FLOAT VCM=1.85V"')
    d.Print2(inm1 ,'DLOG A V 5.3 "-IN=+IN=FLOAT VCM=1.85V"')
    d.Print2(op1 ,'DLOG A2 V 5.3 "+OUT INPUT FLOAT VCM=1.85V"')
    d.Print2(avgOut1 ,'DLOG A4 V 5.3 "AVG +/-OUT @5V VCM=1.85V"')
    return [cmV1,avgOut1]    

def test67():
    deltaOut=avgOut2-avgOut1
    deltaCm=cmV2-cmV1
    cmGain=deltaOut/deltaCm
    cmGain_dB=20*math.log10(cmGain)
    d=dlog(67)
    d.Print2(deltaOut ,'DLOG A V 5.3 "DELTA AVG +/-OUT VCM=0.65V TO 1.85V"')
    d.Print2(deltaCm ,'DLOG B V 5.3 "DELTA VCM"')
    d.Print2(cmGain ,'DLOG A V/V 5.3 "GCM @5V IN+=IN-FLOAT VCM=0.65V TO 1.85"')
    d.Print2(cmGain_dB ,'DLOG A DB 5.3 "GCM @5V +/-IN FLOAT VCM=0.65V TO 1.85"')

def test68n69():
    power('OFF')
    d=dlog(68)
    raw_input("\nTest 68: Float VCM.")
    setControlsPwr(5.0,1.25,1.25,1.25,5.0)
    power('ON')
    [inpV,inmV,na,inCM]=measureInputs('v')
    [op,om,diffOut,oCM]=measureOutputs()
    raw_input("\nTest 68: Take GPIB::23 from outp to cm")
    [cmV,na,na1,na2]=measureOutputs()
    raw_input("\nTest 68: Take GPIB::23 from cm to outp")
    power('OFF')
    #cmV not measured right now. need to connect
    #one of the voltmeters by hand
    d.Print2(cmV ,'DLOG A1 V 5.3 "VCM DEFAULT IN VCM FLOAT"')
    d.Print2(inpV ,'DLOG A2 V 5.3 "V+IN IN VCM FLOAT"')
    d.Print2(inmV ,'DLOG A3 V 5.3 "V-IN IN VCM FLOAT"')
    d.Print2(op ,'DLOG A4 V 5.3 "V+OUT IN VCM FLOAT"')
    d.Print2(om ,'DLOG A5 V 5.3 "V-OUT IN VCM FLOAT"')
    d=dlog(69)
    d.Print2(inCM ,'DLOG C1 V 5.3 "VINCM DEFAULT @5V IN VCM FLOAT"')
    d.Print2(oCM ,'DLOG C2 V 5.3 "VOUTCM DEFAULT @5V IN VCM FLOAT"')
    
#inputs float, but cm is connected.
def test70(cm=0.1,dlogNo=70):
    power('OFF')
    d=dlog(dlogNo)
    raw_input("\nTest 70: Connect GPIB::7 p6v to pin vcm")
    setControlsPwr(5.0,cm,1.25,1.25,5.0)
    power('ON')
    [op,om,oDM,oCM]=measureOutputs()
    d.Print2(op ,'DLOG A1 V 5.3 "+OUT IN FLOAT @5V VCM=0.1V"')
    d.Print2(om ,'DLOG A2 V 5.3 "-OUT IN FLOAT @5V VCM=0.1V"')
    d.Print2(oCM ,'DLOG C2 V 5.3 "VOUTCMMIN @5V IN FLOAT VCM=0.1V"')


def test71(cm=2.4,dlogNo=71):
    power('OFF')
    d=dlog(dlogNo)
    raw_input("\nTest 71: Connect GPIB::7 p6v to pin vcm")
    setControlsPwr(5.0,cm,1.25,1.25,5.0)
    power('ON')
    [op,om,oDM,oCM]=measureOutputs()
    d.Print2(op ,'DLOG A1 V 5.3 "+OUT IN FLOAT VCM=2.4V"')
    d.Print2(om ,'DLOG A2 V 5.3 "-OUT IN FLOAT VCM=2.4V"')
    d.Print2(oCM,'DLOG C2 V 5.3 "VOUTCMMAX @5V IN FLOAT VCM=2.4V"')

def test72():
    #have to connect voltage sources to inputs.
    #when inputs are floated, should you convert the
    #current meters into voltage meters?
    setControlsPwr(5.0,1.25,1.25,1.25,5.0)
    [inpV,inmV,na,inCM]=measureInputs('v')
    [op,om,oDM,oCM]=measureOutputs()
    d=dlog(72)
    d.Print2(inpV ,'DLOG A1 V 5.3 "V+IN IN=FLOAT VCM=1.25V"')
    d.Print2(inmV ,'DLOG A2 V 5.3 "V-IN IN=FLOAT VCM=1.25V"')
    d.Print2(op ,'DLOG A3 V 5.3 "+OUT IN FLOAT VCM=1.25V"')
    d.Print2(om ,'DLOG A4 V 5.3 "-OUT IN FLOAT VCM=1.25V"')
    d.Print2(inCM ,'DLOG C1 V 5.3 "VINCM @5V IN FLOAT VCM=1.25V"')
    d.Print2(oCM ,'DLOG C2 V 5.3 "VOUTCM @5V IN FLOAT VCM=1.25V"')
    return [inCM,oCM]
    

def test73():
    [na,cmV]=vcm_vcc_supply.meas_iv_p6v()
    d=dlog(73)
    #d.Print("cm,V,",cmV)
    #d.Print("vos(cm out),mV,",1e3*(cmV-oCM))
    #d.Print("vos(cm in),mV,",1e3*(cmV-inCM))
    d.Print2(cmV ,'DLOG A V 5.3 "VCM=1.25V @5V IN FLOAT"')
    d.Print2(cmV-oCM ,'DLOG A MV 5.2 "VOS VCM-VOUTCM VCM=1.25V @5V IN FLOAT"')
    d.Print2(cmV-inCM ,'DLOG A MV 5.2 "VOS VCM-VINCM VCM=1.25V @5V IN FLOAT"')
    d.Print2(oCM-inCM ,'DLOG A MV 5.2 "VIOCM VCM=1.25V @5V IN FLOAT"')

def test75():
    power('OFF')
    raw_input("\nTest 75: Short inp and inm to vcm")
    setControlsPwr(5.0,1.25,1.25,1.25,5.0)
    power('ON')
    [inpV,inmV,offset,na2]=measureInputs("v")
    [op,om,oDM,oCM]=measureOutputs()
    #d.Print("\n75.x,vos(in),mV,",1e3*offset
    dlog(75).Print2(oDM,'DLOG A1 MV 5.3 "VOS @5V IN=VCM=1.25V CLAMPS=3.3V/0V"')

#test101: loading outputs with 50mA, skip it, skip it.
#test 102,104,110,111,112,115 (come back tomorrow)
########################################
#### DCSetup2
########################################    

def test25():
    power('OFF')
    d=dlog(25)
    d.Comment("Setup 2:")
    raw_input("\nTest 25:Float all pins except Vcc (and gnd), tie pwradj->vcc")
    vccsweep=0.0
    a=0
    vcm_vcc_supply.setp25v(vccsweep,0.2)
    vcm_vcc_supply.output("ON")
    #for vccsweep in arange(0,5.001,0.1):
    while (a<60.0e-3 and vccsweep<5.0):
        vccsweep=vccsweep+0.1
        vcm_vcc_supply.setp25v(vccsweep,0.2)
        a=supplyCurrent()
        #d.Print("\n225.1,start-up current,mA,",a
    d.Print2(vccsweep,'DLOG V1 V 5.3 "START-UP THRESH @0.2V STEP 100MV"')
    #d.Print("\n25.1,start-up current,mA,",a
    power('OFF')


def test125():
    #clhi pin
    power('OFF')
    d=dlog(125)
    d.Comment("\nSetup2: Connect GPIB::25 as current meter between avg and pwradj.")
    d.Comment("\nSetup2: Connect GPIB::23 voltmeter on clhi.")
    d.Comment("\nSetup2: GBIB::5, GPIB::24, and GPIB::26 are floating.")
    d.Comment("\nSetup2: Disconnect pin CM")
    
    raw_input("\nTest 125: joker connects to clhi, pwradj->vcc")
    #Vcc,sdn,pwradj,clhi,float
    #clhi is p25v
    setControlsPwr(5.0,1.25,1.25,1.25,2.25)
    power('ON')
    time.sleep(1) #before current measurements
    [clhiI1,na,na,na]=measureInputs('i')
    [clhiV1,na,na,na]=measureOutputs()
    setControlsPwr(5.0,1.25,1.25,1.25,1.5)
    time.sleep(1) #before current measurements
    [clhiI2,na,na,na]=measureInputs('i')
    [clhiV2,na,na,na]=measureOutputs()
    #float current meter
    awg.output("OFF")
    [clhi,na,na,na]=measureOutputs()
    power('OFF')
    #test 125.3 floating clhi voltage (default) manually
    d.Print2(clhiI1 ,'DLOG A UA 5.2 "ICLHI CLHI=2.25V @5V CLLO=0V"')
    d.Print2(clhiI2 ,'DLOG A UA 5.2 "I CLHI=1.5V @5V CLLO=0V"')
    d.Print2((clhiV1-clhiV2)/(clhiI1-clhiI2) ,'DLOG A KOHMS 5.2 "RCLHI"')
    d.Print2(clhi ,'DLOG A V 5.3 "VCLHI DEFAULT @5V CLHI=FLOAT"')
    
def test126():
    power('OFF')
    d=dlog(126)
    d.Comment("Disconnect pwradj from vcc")
    raw_input("\nTest 126: joker connects to pwradj")
    defaultPowerup()
    [pwrI1,na,na,na]=measureInputs('i')
    [pwrV1,na,na,na]=measureOutputs()
    setControlsPwr(5.0,1.25,1.25,1.25,2.5)
    [pwrI2,na,na,na]=measureInputs('i')
    [pwrV2,na,na,na]=measureOutputs()
    #float pwr
    awg.output("OFF")
    [pwr,na,na,na]=measureOutputs()
    power('OFF')
    #Vcc,sdn,pwradj,clhi,float
    #pwradj is in:p6v
    #test 126.3 floating pwradj voltage (default) manually
    d.Print2(pwrI1 ,'DLOG A UA 5.1 "IPWR IPWR=5V @5V VCL=3.3V"')
    d.Print2(pwrI2 ,'DLOG A UA 5.1 "IPWR IPWR=2.5V @5V VCL=3.3V"')
    d.Print2((5.0-2.5)/(pwrI1-pwrI2) ,'DLOG A KOHMS 5.1 "PWR ADJ"')
    d.Print2(pwr ,'DLOG A V 5.3 "PWR ADJ DEFAULT @5V PWR ADJ=FLOAT"')
    
def test127():
    power('OFF')
    d=dlog(127)
    d.Comment("\nTest 127: Connect pwradj->vcc")
    raw_input("\nTest 127: joker connetcs to sdn")
    defaultPowerup()
    [sdnI1,na,na,na]=measureInputs('i')
    [sdnV1,na,na,na]=measureOutputs()
    setControlsPwr(5.0,1.25,1.25,1.25,0.0)
    [sdnI2,na,na,na]=measureInputs('i')
    [sdnV2,na,na,na]=measureOutputs()
    #float current meter
    awg.output("OFF")
    sdn=outp_mm.meas()
    power('OFF')
    
    #test 127.3 floating sdn voltage (default) manually
    d.Print2(sdnI1 ,'DLOG A UA 5.1 "SDN=5V @5V VCL=3.3V"')
    d.Print2(sdnI2 ,'DLOG A UA 5.2 "SDN=0V @5V VCL=3.3V"')
    d.Print2((sdnV1-sdnV2)/(sdnI1-sdnI2) ,'DLOG A OHMS 5.2 "SDN/ENABLE"')
    d.Print2(sdn ,'DLOG A V 5.3 "SDN DEFAULT @5V SDN=FLOAT"')


def test60():
    power('OFF')
    raw_input("Test 60: joker connetcs to cm")   
    setControlsPwr(5.0,1.25,1.25,1.25,0.65)
    power('ON')
    [cmI1,na,na,na]=measureInputs('i')
    [cmV1,na,na,na]=measureOutputs()    
    setControlsPwr(5.0,1.25,1.25,1.25,1.25)
    power('ON')
    [cmI0,na,na,na]=measureInputs('i')
    [cmV0,na,na,na]=measureOutputs()    
    setControlsPwr(5.0,1.25,1.25,1.25,1.85)
    [cmI2,na,na,na]=measureInputs('i')
    [cmV2,na,na,na]=measureOutputs()    
    #float current meter
    awg.output("OFF")
    cm=outp_mm.meas()
    
    d=dlog(60)
    d.Print2(cmI1 ,'DLOG A1 UA 5.2 "IBVCM VCM=0.65V V+=5V IN FLOAT"')
    d.Print2(cmI0 ,'DLOG A2 UA 5.2 "IBVCM VCM=1.25V V+=5V IN FLOAT"')
    d.Print2(cmI2 ,'DLOG A3 UA 5.2 "IBVCM VCM=1.85V V+=5V IN FLOAT"')
    d.Print2(cmI2-cmI1 ,'DLOG A UA 5.3 "DELTA IIN VCM=0.65V TO 1.85V"')
    d.Print2((cmV1-cmV2)/(cmI1-cmI2) ,'DLOG A KOHMS 5.2 "RVCM VCM 0.65V TO 1.85V IN FLOAT"')
    
##########################################
#### dcTest1516


fileroot=basedir+todaysDate+dutName+testName

filename=fileroot+'.txt'
#f=open(filename,'wb')
##################### open file

#3631A:vcm(6V),vcc(25v)
#3631A:inm(6V),inp(25v)
#AWG: joker(hi or pwradj) DC
#one more prog. power supply: inp, inm
#shutdown: by hand.

#dcCorrelationHookup


########################################################################
unitNo=raw_input("Enter dc correlation unit number:")
#fileprint(f,filename+" unit number:"+str(unitNo))
#f.close()


# test10()
# a=raw_input("press any key to continue")
# test12()
# test15()
# test16()
# [v1,i1]=test20()
# [v2,i2]=test21()
# test22()

# #test30()

# test33() #to be verified after outp-gpib cable.

# print "\n skip 33.1-2,34"
# print "test 33, 34: skipping output loading measurements"


# [diffOut1,diffIn1]=test36()
# [diffOut2,diffIn2]=test37()
# test38()


# #test 40
# print "\nSkip test 40: abs max input current"
# test50()

# [cc1,offset1]=test80()
# [cc2,offset2]=test81()

# [inI1,inV1,offset1]=test90();[inI2,inV2,offset2]=test91();test92()


# [inAvg1,outAvg1]=test95()
# [inAvg2,outAvg2]=test96()
# test100()

# test120()
# test121()

# print "\nSetup2: GBIP::25 current meter between"
# print "\nSetup2: awg and pwradj."
# print "\nSetup2: float inp and inm."
# print "\nSetup2: GBPIP::26 volt meter on pwradj."

# print "\nchange to setup2"
# a=raw_input("Press any key to continue")
# test25()
# test125()
# test126()
# test127()
# test60()


# print "\nchange to Setup1:"
# [cmV1,avgOut1]=test65()
# [cmV2,avgOut2]=test66()
# test67()
# test68n69()
# test70()
# test71()
# [inCM,oCM]=test72()
# test73()
# test75()

# power('OFF')


# print 'stop here' #@@@



#fileprint(f, "Test 1: Negative ESD Diodes.")
#fileprint(f, "Test 1: Inst: Disconnect/float all pins.")
#for pin in ["in_m","in_p","cm","pwradj","clhi","shdn","gnd"]:
#        testEsdDiode(pin, -0.75,0.0005)  #test number

#print "Test 2: Positive ESD Diodes."
#for pin in ["in_m","in_p","cm","pwradj","clhi","shdn"]:
#        a=testEsdDiode(pin, 0.75,0.0005)  #test number
#        fileprint(f,str(a))




# DLOG A MV 5.1 "V_LO CLAMP 1.25V VCM VCL 2.0V OUT+"
# DLOG A1 MV 5.1 "V_LO CLAMP 1.25V VCM VCL 1.5V OUT+"
# DLOG A2 V/V 5.3 "G_HI OUT +"
# DLOG A MV 5.1 "V_LO CLAMP 1.25V VCM VCL 2.0V OUT-"
# DLOG A1 MV 5.1 "V_LO CLAMP 1.25V VCM VCL 1.5V OUT-"
# DLOG A2 V/V 5.3 "G_HI OUT-"
# DLOG A MV 5.1 "VLO CLAMP 1.25V VCM VCL2V OUT -"
# DLOG A1 MV 5.1 "VLO CLAMP 1.50V VCM VCL2V OUT -"
# DLOG A2 V/V 5.3 "GCM OUT -"
# DLOG A MV 5.1 "VLO CLAMP 1.25V VCM VCL2V OUT +"
# DLOG A1 MV 5.1 "VLO CLAMP 1.50V VCM VCL2V OUT +"
# DLOG A2 V/V 5.3 "GCM OUT +"
# DLOG A V 5.3 "LOGIC OUT NO CLAMP"
# DLOG A7 UA 5.1 "LOGIC OUT NO CLAMP @0V"
# DLOG A1 V 5.3 "LOGIC OUT BOTH HI CLAMP+"
# DLOG A2 V 5.3 "LOGIC OUT BOTH LO CLAMP-"
# DLOG A3 UA 5.1 "LOGIC OUT OUT+ CLAMP+"
# DLOG A4 UA 5.1 "LOGIC OUT OUT+ CLAMP-"
# DLOG A5 UA 5.1 "LOGIC OUT OUT- CLAMP+"
# DLOG A6 UA 5.1 "LOGIC OUT OUT- CLAMP-"
