% For 2387 lab board.  Starts continuously running conversions in test
% mode. The input argument numLanes is either 1 or 2. numSamples is the 
% number of samples to be converted. The ADC converts for ~200ms before
% collecting data. 
%   result = lab_convert ( numSamples, numLanes ); %full speed data
%
% If a third input argument is given, the input data is decimated by 4x.
%   result = lab_convert ( numSamples, numLanes, 1 ); %0.25x data
%
%
%RefDvm address needs to be 21
%AinDvm address needs to be 10
%Data Precision address needs to be 1
%
%If you want to force an error for the "Ain" voltage use the supplied
%variable "AinVoltageOffset"
%


function   result = lab_convert_gain_a (gain_mode, varargin )


numSamples = varargin{1};
numLanes = varargin{2};


if (nargin == 2)        % full data rate (no decimation)
    if (numLanes == 1)
        ma37a('0000 0002 0270');    %% twolanes=0, testmode=1, spi_en=0
    elseif (numLanes == 2)
        ma37a('0000 0006 0270');    %% twolanes=1, testmode=1, spi_en=0
    else
        disp('numLanes must be 1 or 2. Exiting function.');
        return;
    end
end

if (nargin == 3)        % decimate data by 4x
    if (numLanes == 1)
        ma37a('0000 0102 0270');    %% div4=1, twolanes=0, testmode=1, spi_en=0
    elseif (numLanes == 2)
        ma37a('0000 0106 0270');    %% div4=1, twolanes=1, testmode=1, spi_en=0
    else
        disp('numLanes must be 1 or 2. Exiting function.');
        return;
    end
end

ma37a('0000 0090 0263');  %%trigger waveform output (start conversion)

pause(0.2);        % let reference settle before grabbing data. Was 0.02

 %Set gain selection here*****************************************************************************************  
 %PlusFullScale = 2;  %   2 = PluseFullScale,  1 = Offset 0 = MinusFullScale
 %PlusFullScale = 1 ;  %   2 = PluseFullScale,  1 = Offset 0 = MinusFullScale
 PlusFullScale = gain_mode;
 fs=PlusFullScale;
  
 DP=gpib('agilent',7,1);
 fopen(DP);
 if (PlusFullScale == 2) || (PlusFullScale == 0)
     fprintf(DP, 'V1+04.09600');
 else
     fprintf(DP, 'V1+02.04800');
 end

 AinVoltageOffset = +.000 ; %Used to force error at "Ain"
 dvmAin = gpib('agilent',7,10);         %Setup object for Ain Dvm
 set(dvmAin,'EOSMode','read')           %Needed to properly terminate a read statement to the Dvm
 fopen(dvmAin);                         %Open objet;
 fprintf(dvmAin, 'NPLC 100');            %Set the number of power line cycles
 fprintf(dvmAin, 'FUNC DCV, 8');                           
 fprintf(dvmAin, 'TRIG SGL');           %Trigger Dvm
 AinVolts = fscanf(dvmAin, '%f',1);     %Read DvmAin
 
 dvmRef = gpib('agilent',7,22);         %Setup object for Ref Dvm
 set(dvmRef,'EOSMode','read')           %Needed to properly terminate a read statement to the Dvm
 fopen(dvmRef);                         %Open objet
 fprintf(dvmRef, 'NPLC 100');           %Set the number of power line cycles
 fprintf(dvmRef, 'FUNC DCV, 8');
 fprintf(dvmRef, 'TRIG SGL');           %Trigger Dvm
 RefVolts = fscanf(dvmRef, '%f',1);     %Read DvmRef
 disp 'Ref Volts = ';
 disp (RefVolts);
 
 if (PlusFullScale == 2) 
   VoltError=RefVolts-AinVolts;
   %NewVoltage=4.096+VoltError;
   NewVoltage=4.096+VoltError + AinVoltageOffset; % "AinVoltageOffset" usualy set to zero.
   str = sprintf('%1.5f',NewVoltage);
   str2 = ['V1+0',str];
   if NewVoltage<5 
     fprintf(DP, str2);
     fprintf(dvmAin, 'TRIG SGL');           %Trigger Dvm
     AinVolts = fscanf(dvmAin, '%f',1);
     disp 'Ain Volts = ';
     disp (AinVolts);
   else
     disp '*******check setup. Ain Voltage trying to go above 5v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage trying to go above 5v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage trying to go above 5v. Please correct the problem and re-run' 
   end
   CorectionCode = (RefVolts-AinVolts)/((RefVolts*2)/262144); %Correct for Ain Voltage not being perfect
 end
 if (PlusFullScale == 0) 
   VoltError=RefVolts-((AinVolts)*-1);
   %NewVoltage=(4.096+VoltError)
   NewVoltage=(4.096+VoltError) + AinVoltageOffset; % "AinVoltageOffset" usualy set to zero.
   str = sprintf('%1.5f',NewVoltage);
   str2 = ['V1+0',str];
   if NewVoltage<5
     fprintf(DP, str2);
     fprintf(dvmAin, 'TRIG SGL');
     AinVolts = fscanf(dvmAin, '%f',1);
     disp 'Ain Volts = ';
     disp (AinVolts);
   else
     disp '*******check setup. Ain Voltage trying to go above 5v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage trying to go above 5v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage trying to go above 5v. Please correct the problem and re-run' 
   end
   CorectionCode = ((RefVolts+AinVolts)/((RefVolts*2)/262144))*-1; %Correct for Ain Voltage not being perfect
 end
 
 if (PlusFullScale == 1)
    CorectionCode = (0-AinVolts)/((RefVolts*2)/262144); %Correct for Ain Voltage not being perfect
    disp 'Ain Volts = ';
    disp (AinVolts);
 end

     fclose(dvmAin);  %Close dvmAin object
     fclose(dvmRef);  %Close dvmRef object
     fclose(DP);      %Close Data Precision

result = convert_data( ma37a_stream_capture(numSamples),fs,CorectionCode );
pause(.05);
%ma37a('0000 0000 0263');    %% turn off triggers

end

% Local function to convert 2's complement to straight binary
function   dataOut = convert_data( dataIn,fs,CorectionCode )
    %dataOutTmp = zeros(size(dataIn), 'uint32');
    %dataOutExtCodes = zeros(size(dataIn), 'uint32');
    dataOutTmp = zeros(size(dataIn), 'double');
    dataOutExtCodes = zeros(size(dataIn), 'double');
    
format long;
PlusFullScale=fs;
 
    
        for i=1:(size(dataIn,1))
            if dataIn(i) >= 131072  %convert 2's complement to straight binary
                dataOutTmp(i) = dataIn(i) - 131072;
            else
                dataOutTmp(i) = dataIn(i) + 131072;
            end
        end
    DataStraight_Binary = double(dataOutTmp);
      
 dvmAin = gpib('agilent',7,10);         %Setup object for Ref Dvm
 set(dvmAin,'EOSMode','read')           %Needed to properly terminate a read statement to the Dvm
 fopen(dvmAin);
 fprintf(dvmAin, 'TRIG SGL');           %Trigger Dvm
 AinVolts = fscanf(dvmAin, '%f',1);     %Read DvmAin
 %disp 'Ain Volts = ';
 fclose(dvmAin);

if PlusFullScale == 2         
     
 if ~(AinVolts>4.086 && AinVolts<4.106) %Display message if Ain voltage is to far from target
     disp '*******check setup. Ain Voltage should be close to +4.096v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage should be close to +4.096v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage should be close to +4.096v. Please correct the problem and re-run'
 end
         
      for i=1:(size(dataIn,1)) %Correct for extended codes plus full scale
            if DataStraight_Binary(i) <= 131072  % 131072 is a randomly chosen number used to see if the codes have rolled over 
                dataOutExtCodes(i) = DataStraight_Binary(i) + 262144; % If they have rolled over add full scale to code
            else
               dataOutExtCodes(i) = DataStraight_Binary(i); % If the codes havn't rolled over do nothing
            end
      end
      ave = mean(double(dataOutExtCodes));
      %tmp = (262144-(ave + CorectionCode))*-1; %Calculate plus full scale error in lsb's
      %tmp = (262142.5-(ave + CorectionCode))*-1; %Calculate plus full scale error in lsb's
      tmp = (ave + CorectionCode)-262142.5; %Calculate plus full scale error in lsb's
end
     
if PlusFullScale == 0
  
 if ~(AinVolts<-4.086 && AinVolts>-4.106) %Display message if Ain voltage is to far from target
     disp '*******Please check setup. Ain Voltage should be close to -4.096v. Please correct the problem and re-run.'
     disp '*******Please check setup. Ain Voltage should be close to -4.096v. Please correct the problem and re-run.'
     disp '*******Please check setup. Ain Voltage should be close to -4.096v. Please correct the problem and re-run.'
 end
         
        for i=1:(size(dataIn,1)) %Correct for extended codes minus full scale
            if DataStraight_Binary(i) >= 131072  % 131072 is a randomly chosen number used to see if the codes have rolled over
                dataOutExtCodes(i) = DataStraight_Binary(i) - 262144; % If they have rolled over subtract full scale from code
            else
               dataOutExtCodes(i) = DataStraight_Binary(i);% If the codes havn't rolled over do nothing
            end
        end       
  ave = mean(double(dataOutExtCodes));
  %tmp = (0-(ave + CorectionCode))*-1;      %Calculate minus full scale error in lsb's
  %tmp = (0.5-(ave + CorectionCode))*-1;      %Calculate minus full scale error in lsb's
  tmp = (ave + CorectionCode)-0.5;      %Calculate minus full scale error in lsb's
end
     
if PlusFullScale == 1  %Offset
     
  if ~(AinVolts<0.01 && AinVolts>-0.01)  %Display message if Ain voltage is to far from target
     disp '*******check setup. Ain Voltage should be close to 0v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage should be close to 0v. Please correct the problem and re-run'
     disp '*******check setup. Ain Voltage should be close to 0v. Please correct the problem and re-run'
  end
                
       ave = mean(DataStraight_Binary);
       %tmp = (131072-(ave + CorectionCode))*-1;
       %tmp = (131071.5-(ave + CorectionCode))*-1;
       tmp = (ave + CorectionCode)-131071.5;
  
end
     
     disp 'Error = '; %Display error in Lsb's
     dataOut=tmp;     %Return error to calling function
end
