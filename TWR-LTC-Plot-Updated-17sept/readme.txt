For using DAC ltc2600 & ADC ltc2498 select the command file test_cmds_ltc2600_ltc2498
For using DAC ltc2600 & ADC ltc2498 select the command file test_cmds_ltc2704_ltc1859

---------------------------------------------------------------------------------------
Command file description
----------------------------------------------------------------------------------------

Selection of ADC & DAC

X0- DAC LTC-2600
X1- ADC LTC-2498
X2- DAC LTC-2704
X3- ADC LTC-1859

There are two types of comands set

1. test_cmds_ltc2600_ltc2498

format: X0Nabcd    :X0- select chip LTC2600(DAC) 'N'- Initialization "ab"-selection of channel "cd"- Commands settings
        S1.23      :send voltage 1.23
        X2N1104    :X1- select chip LTC2498(ADC) 'N'- Initialization "ab" -selection of channel "cd"- selecting the command
        R	   : Receive


2. test_cmds_ltc2704_ltc1859


Format: X1Nabcdef :X2- select chip LTC2704(DAC), 'N'- Initialization, "ab"-selection of channel, "cd"- slecting the span, "ef"- select the commindex 
        s1.23     :send voltage 1.23
        X3N090200 :X3- select chip LTC1859(ADC), 'N'- Initialization, "ab"-selection of channel, "cd"- slecting the span, "ef"- sleep Settings
        R	  : Receive




----------------------------------------------------------------------------------------
1. LTC2600
----------------------------------------------------------------------------------------
 Function sets for ltc2600.
 The sommand format is X0Nxxxx. The first group of xx is for channel selection
 channel selection:
 00  ADR DAC A
 01  ADR DAC B
 02  ADR DAC C
 03  ADR DAC D
 04  ADR DAC E
 05  ADR DAC F
 06  ADR DAC G
 07  ADR DAC H
 08 ADR DAC ALL

 which is 8-bit num and the second xx is for selecting the command as follows
 00  WRITE N
 01  UPDATE N
 02  WRITE UPDATE ALL
 03  WRITE_UPDATE_N
 04  POWER DOWN N
 05  NO OPERATION
---------------------------------------------------------------------------------------
2. LTC2700
---------------------------------------------------------------------------------------

 The command format is X1Nxxxxxx. The first two xx are for celecting the 
 channel index with following code format
 00  ADR DAC A
 01  ADR DAC B
 02  ADR DAC C
 03  ADR DAC D
 04  ADR DAC ALL

 The next two xx are for slecting the span with following code format
 00  UNIPOLAR 0 5
 01  UNIPOLAR 0 10
 02  BIPOLAR -5 5
 03  BIPOLAR -10 10
 04  BIPOLAR  -2.5 2.5
 05  BIPOLAR -2.5 7.5

 The next two xx select the commindex  
 00  WRITE UPDATE N           WRITE SPAN N
 01  WRITE CODE N UPDATE N    WRITE SPAN N UPDATE N
 02  WRITE CODE N UPDATE ALL  WRITE SPAN N UPDATE ALL
 03  UPDATE N
 04  UPDATE ALL
 05  READ B1 SPAN N
 06  READ B1 CODE N
 07  READ B2 SPAN N
 08  READ B2 CODE N
 09  SLEEP N
 0A  NO OPERATION
 0B  WRITE N
 0C  UPDATE N
 0D  WRITE UPDATE ALL
-------------------------------------------------------------------------------------
3. LTC 2498
-------------------------------------------------------------------------------------
 The command format is X2Nxxxx. The first set X, xx is for selecting the 
 channel and the code format for selcting the channel is

 00 NO CHANNEL CHANGE

 01 DIFF 0-1
 02 DIFF 2-3
 03 DIFF 4-5
 04 DIFF 6-7
 05 DIFF 8-9
 06 DIFF 10-11
 07 DIFF 12-13
 08 DIFF 14-15

 09 DIFF 1-0
 0A DIFF 3-2
 0B DIFF 5-4
 0C DIFF 7-6
 0D DIFF 9-8
 0E DIFF 11-10
 0F DIFF 13-12
 10 DIFF 15-14

 11 SING 0
 12 SING 1
 13 SING 2
 14 SING 3
 15 SING 4
 16 SING 5
 17 SING 6
 18 SING 7
 19 SING 8
 1A SING 9
 1B SING 10
 1C SING 11
 1D SING 12
 1E SING 13
 1F SING 14
 20 SING 15


 settings are enocded with following code format
 00  KEEP PREVIOUS SETTING
 01  EXT REJECT 50 60 X1
 02  EXT REJECT 50 X1  
 03  EXT REJECT 60 X1
 04  EXT REJECT 50 60 X2
 05  EXT REJECT_50 X2 
 06  TEMP REJECT 50 60 X1
 07  TEMP REJECT 50 X1
 08  TEMP REJECT 60 X1    

------------------------------------------------------------------------------------
4. LTC 1859
------------------------------------------------------------------------------------
 The command format is X2Nxxxxxx. The first two xx are for celecting the 
 channel index with following code format

 

 00 DIFF 0-1
 01 DIFF 2-3
 02 DIFF 4-5
 03 DIFF 6-7
 
 04 DIFF 1-0
 05 DIFF 3-2
 06 DIFF 5-4
 07 DIFF 7-6
 08 Single-Ended 0
 09 Single-Ended 1
 0A Single-Ended 2
 0B Single-Ended 3
 0c Single-Ended 4
 0D Single-Ended 5
 0E Single-Ended 6
 0F Single-Ended 7



 The next two xx are for slecting the span with following code format
00 Bipolar [-5V to 5V]
01  Bipolar [-10V to 10V]
02  Unipolar [0 to 5V]
03  Unipolar [0 to 10V]

The next two xx select the sleep setings

00 on
01 nap
02 sleep	
