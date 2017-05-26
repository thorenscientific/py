// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// released under the GPLv3 license to match the rest of the AdaFruit NeoPixel library
#include <Adafruit_NeoPixel.h>
#include <stdint.h>

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN            6

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS      120

char get_char(); //Prototype for funciton to get next character from serial port

uint8_t top = 110, bottom=10, ball=60; // Top of window, bottom of window, and ball position
int i;
bool updown = 1; // Going up or down? Start with up!
uint8_t oldball;
char command;

char hex_to_byte_buffer[5]=
{
  '0', 'x', '0', '0', '\0'
};               // buffer for ASCII hex to byte conversion

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int delayval = 25; // delay for half a second

void setup() {
  randomSeed(12345);
  Serial.begin(115200); // Fire up serial port
  Serial.setTimeout(100);
  pixels.begin(); // This initializes the NeoPixel library.
  // pixels.Color takes RGB values, from 0,0,0 up to 255,255,255
  for(i=0; i<bottom; i++){ // Color in bottom of window
    pixels.setPixelColor(i, pixels.Color(150, 0, 0));
  }
  for(i=top; i<NUMPIXELS; i++){ // Color in top of window
    pixels.setPixelColor(i, pixels.Color(150, 0, 0));
  }
}

void loop() {
  while(!Serial.available()){
    top = random(70, 119);
    bottom = random(0, 50);
    ball = random(bottom+1, top-1);
      for(i=0; i<bottom; i++){ // Color in bottom of window
        pixels.setPixelColor(i, pixels.Color(150, 0, 0));
      }
      for(i=top; i<NUMPIXELS; i++){ // Color in top of window
        pixels.setPixelColor(i, pixels.Color(150, 0, 0));
      }
    int j = 4;
    while(j>=0){
      // For a set of NeoPixels the first NeoPixel is 0, second is 1, all the way up to the count of pixels minus one.
      for(i=bottom;i<=top;i++){ // First, wipe playing field
        pixels.setPixelColor(i, pixels.Color(0,0,0)); // Turn off
      }
      pixels.setPixelColor(oldball, pixels.Color(0,0,0)); // Turn off oldball
      pixels.setPixelColor(ball, pixels.Color(0,0,150)); // Turn on ball
      if(ball==bottom){updown = 1; j--;} // Flip direction of ball and increment counter
      if(ball==top) updown=0;
      oldball = ball;
      if(updown == 0) ball--;
      if(updown == 1) ball++;
      pixels.show(); // This sends the updated pixel color to the hardware.
      delay(delayval); // Delay for a period of time (in milliseconds).
      if(Serial.available()) break;
    }
  }
  // Okay, we got a character, stop bouncing!
  while(1){
  command = get_char();
  switch (command)
  {
    case 't': // Set upper window
      top = read_hex();
      Serial.print("setting top to ");
      Serial.println(top);
        for(i=bottom;i<=top;i++){ // First, wipe playing field
        pixels.setPixelColor(i, pixels.Color(0,0,0)); // Turn off
      }
      for(i=top; i<NUMPIXELS; i++){ // Color in top of window
        pixels.setPixelColor(i, pixels.Color(150, 0, 0));
      }
    break;
    case 'b': // Set lower window
      bottom = read_hex();
      Serial.print("setting bottom to ");
      Serial.println(bottom);
        for(i=bottom;i<=top;i++){ // First, wipe playing field
        pixels.setPixelColor(i, pixels.Color(0,0,0)); // Turn off
      }
      for(i=0; i<bottom; i++){ // Color in bottom of window
        pixels.setPixelColor(i, pixels.Color(150, 0, 0));
      }
    break;
    case 'p': // Set ball position
      ball = read_hex();
      Serial.print("setting ball pos to ");
      Serial.println(ball);
      pixels.setPixelColor(oldball, pixels.Color(0,0,0)); // Turn off oldball
      pixels.setPixelColor(ball, pixels.Color(0,0,150)); // Turn on ball
      oldball = ball;
      break;
    default:
    while(Serial.available()){get_char();} // Out of sync somehow or invalid command, flush buffer.
    break;
    }
  pixels.show();
  }
}

char get_char()
// get the next character either from the serial port
{
    // read a command from the serial port
    while (Serial.available() <= 0);
    return(Serial.read());
}


byte read_hex()
// read 2 hex characters from the serial buffer and convert
// them to a byte
{
  byte data;
  hex_to_byte_buffer[2]=get_char();
  hex_to_byte_buffer[3]=get_char();
  data = strtol(hex_to_byte_buffer, NULL, 0);
  return(data);
}
