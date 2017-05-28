// Read analog value and send it using serial
//
// Copyright (C) 2012 Asaf Paris Mandoki http://asaf.pm
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

//   This program for Arduino reads one channel and sends the data
//   out through the serial port in 2 bytes.
//   For synchronization purposes, the following scheme was chosen:
//   A0 data:   A09 (MSB) A08 A07 A06 A05 A04 A03 A02 A01 A00 (LSB)
//   sent as byte 1:   1 1 1 A09 A08 A07 A06 A05
//       and byte 2:   0 1 1 A04 A03 A02 A01 A00
//
//
//
int sensorValue = 0;        // value read from the pot
byte lb;
byte hb;

void setup() {
  // initialize serial communications at 115200 bps:
  Serial.begin(115200); 
}

void loop() {
  // read A0:
  sensorValue = analogRead(A0);            
  // shift sample by 3 bits, and select higher byte  
  hb=highByte(sensorValue<<3); 
  // set 3 most significant bits and send out
  Serial.write(hb|0b11100000); 
  // select lower byte and clear 3 most significant bits
  lb=(lowByte(sensorValue))&0b00011111;
  // set bits 5 and 6 and send out
  Serial.write(lb|0b01100000);
}

