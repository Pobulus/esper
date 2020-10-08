#include <DateTime.h>
//#include <NTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <WiFiUdp.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
unsigned long elapsed;
unsigned long startime;
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
const long utcOffsetInSeconds = 7200;
bool invert = false;
int rate = 1;
int port = 8888;  
int timeout = 0;
int offtime = 200;
bool recv = false;
int secs = 0;
int minutes = 0;
int hours = 0;
int dsecs = 0;
int dminutes = 0;
int dhours = 0;
int light = 0;
int rssi = 0;
int rssip = 0;
int btnpress = 0;
int elsecs=0;
String formattedDate;
String dayStamp;

WiFiUDP ntpUDP;
WiFiServer server(port);

static const unsigned char PROGMEM logo_bmp[] =
{ B00000000, B11000000,
  B00000001, B11000000,
  B00000001, B11000000,
  B00000011, B11100000,
  B11110011, B11100000,
  B11111110, B11111000,
  B01111110, B11111111,
  B00110011, B10011111,
  B00011111, B11111100,
  B00001101, B01110000,
  B00011011, B10100000,
  B00111111, B11100000,
  B00111111, B11110000,
  B01111100, B11110000,
  B01110000, B01110000,
  B00000000, B00110000 };


void setup() {
  Serial.begin(115200);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); 
  }

  
  display.display();
  display.ssd1306_command(0xA0);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(F("Display: ON"));
  display.display();      
  delay(100);
  int i = 0;
  WiFi.mode(WIFI_STA);
   WiFiManager wm;
 bool res;
    // res = wm.autoConnect(); // auto generated AP name from chipid
    // res = wm.autoConnect("AutoConnectAP"); // anonymous ap
    res = wm.autoConnect("ESPER","OpenYourEyes"); // password protected ap
    if(!res) {
        display.println("Wifi Failed");
        display.display();
        // ESP.restart();
    }
     else {
        //if you get here you have connected to the WiFi    
        display.println("Wifi Connected");
        display.display();
        display.println(F("ssid:"));
        display.println(WiFi.SSID());
        display.display();  
        display.println(F("Syncing..."));
        display.display();
        DateTime.begin();
        ntpSync();
        display.display();
        display.println("TCP on port:");
        display.display(); 
        server.begin();
        display.print(WiFi.localIP());
        display.print(":");
        display.println(port);
        display.display();
        delay(1000);
    }
}

void loop() {
  while(digitalRead(D6) != 1){
    timeout = 0;
    btnpress++;
    display.setTextSize(3);
    display.setCursor(0,0);
    display.print(btnpress);
    display.display();
    if(btnpress>300){btnpress=0;break;}
    }
  WiFiClient client = server.available();
   if (client) { //reciever mode
    while(client.connected()){
      while(client.available()>0){    
        int b = client.read();
        //Serial.print(b);
        if (b == 7){
          client.print(0);
          //client.print(1); to change the mode from reciever

        
          }
        if(b == 8){
          recv = true;
        }
        if(b ==9){
          recv = false;
          display.clearDisplay();
          display.display();
        }
        if(b==0){display.display();}
        if(b == 1){
          int x = client.read();
          int y = client.read();
          display.setCursor(x, y);
          display.display();
          }
        if(b == 2)display.clearDisplay();
        if(b == 3)display.setTextSize(1);
        if(b == 4)display.setTextSize(2);
        if(b == 5)display.setTextSize(3);
        if(b == 10){ //print text
          int c = client.read();
          while(c != 254){
            display.write(c);
            c = client.read();
            }
        }
         if(b == 20){//draw rectangle
            int x = client.read();
            int y = client.read();
            int w = client.read();
            int h = client.read();
            int color = client.read();
            if(color == 0){display.drawRect(x,y,w,h,SSD1306_BLACK);}
            if(color == 1){display.drawRect(x,y,w,h,SSD1306_WHITE);}
            if(color == 2){display.drawRect(x,y,w,h,SSD1306_INVERSE);}
            if(color == 3){display.fillRect(x,y,w,h,SSD1306_BLACK);}
            if(color == 4){display.fillRect(x,y,w,h,SSD1306_WHITE);}
            if(color == 5){display.fillRect(x,y,w,h,SSD1306_INVERSE);}
            }
        if(b==21){ //draw circle

            int x = client.read();
            int y = client.read();
            int r = client.read();
            int color = client.read();
            if(color == 0)display.drawCircle(x,y,r,SSD1306_BLACK);
            if(color == 1)display.drawCircle(x,y,r,SSD1306_WHITE);
            if(color == 2)display.drawCircle(x,y,r,SSD1306_INVERSE);
            if(color == 3)display.fillCircle(x,y,r,SSD1306_BLACK);
            if(color == 4)display.fillCircle(x,y,r,SSD1306_WHITE);
            if(color == 5)display.fillCircle(x,y,r,SSD1306_INVERSE);
          }       
        if(b==22){ //draw line
           int x = client.read();
            int y = client.read();
            int w = client.read();
            int h = client.read();
            int color = client.read();          
            if(color == 0){display.drawLine(x,y,w,h,SSD1306_BLACK);}
            if(color == 1){display.drawLine(x,y,w,h,SSD1306_WHITE);}
            if(color == 2){display.drawLine(x,y,w,h,SSD1306_INVERSE);}
          }
         if(b==23){ //draw triangle
            int x = client.read();
            int y = client.read();
            int w = client.read();
            int h = client.read();
            int p = client.read();
            int q = client.read();
            int color = client.read();
            if(color == 0){display.drawTriangle(x,y,w,h,p,q,SSD1306_BLACK);}
            if(color == 1){display.drawTriangle(x,y,w,h,p,q,SSD1306_WHITE);}
            if(color == 2){display.drawTriangle(x,y,w,h,p,q,SSD1306_INVERSE);}
            if(color == 3){display.fillTriangle(x,y,w,h,p,q,SSD1306_BLACK);}
            if(color == 4){display.fillTriangle(x,y,w,h,p,q,SSD1306_WHITE);}
            if(color == 5){display.fillTriangle(x,y,w,h,p,q,SSD1306_INVERSE);}     
            }
        }
    }
}else{
       
    if(btnpress>0){ //standalone mode
        if(btnpress > 9){
            if(btnpress > 99){
                display.clearDisplay();
                display.display();
                WiFi.disconnect();
            }else{
                invert = !invert;
            }
        }else{
            display.clearDisplay();    
        }
  }else{ 
  btnpress = 0;
  display.clearDisplay();
  showTime();
  display.setTextSize(2);
  display.println(DateTime.format(DateFormatter::DATE_ONLY));
  display.setTextSize(1);
  display.println(WiFi.SSID());
  rssi = WiFi.RSSI();
  rssip = 128+int(round(rssi*128/100));
  display.print(rssi);
  display.print(F(":"));
  display.println(rssip);
  display.fillRect(0, 60, rssip, 64, SSD1306_WHITE);
  }
  display.display();
  delay(150);
}}


void showTime(){
  display.setTextSize(3);
  display.setCursor(30, 0);
  display.print(F(":"));
  display.setCursor(70, 0);
  display.print(F(":"));  
  elsecs = int(round(elapsed/1000));
  DateTimeParts p = DateTime.getParts();
  dhours = p.getHours();
  dminutes = p.getMinutes();
  dsecs = p.getSeconds();
  display.setCursor(0,0);
  display.print(correction(dhours%24));
  display.setCursor(41, 0);
  display.print(correction(dminutes%60));
  display.setCursor(82, 0);
  display.println(correction(dsecs%60)); 
}
  
String correction(int x){
  if (x<10){
    return "0"+String(x);
  }
  else{
    return String(x);  
  }
}

void ntpSync() {
        display.setCursor(0,40);
        display.setTextSize(1);
        display.print(F("NTP sync..."));
        display.display();
        setupDateTime();
        display.print(F("Time got."));
        display.display();
        startime = millis();
        DateTimeParts p = DateTime.getParts();
        hours = p.getHours();
        minutes = p.getMinutes();
        secs = p.getSeconds();
        Serial.println(DateTime.getTime());
        display.print(correction(hours));
        display.display();
        display.print(F(":"));
        display.print(correction(minutes));
        display.display();
        display.print(F(":"));
        display.print(correction(secs));
        display.display();      
}

void setupDateTime() {
  DateTime.setTimeZone(-2);
  DateTime.setServer("pl.pool.ntp.org");
  DateTime.begin(utcOffsetInSeconds);
  if (!DateTime.isTimeValid()){display.println("Sync Failed");}
}