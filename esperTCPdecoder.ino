#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <Wire.h>

 
int port = 8888;  
WiFiServer server(port);
 

const char *ssid = "********";  //Put your ssid and password here
const char *password = "********"; 
byte customChar[] = {
  B00000,
  B10000,
  B01000,
  B00100,
  B00010,
  B00001,
  B00000,
  B00000
};
LiquidCrystal_I2C lcd(0x3f, 2, 1, 0, 4, 5, 6, 7, 3, POSITIVE);  
int count=0;

void setup() 
{
  Serial.begin(115200);
  Wire.begin(D2, D1);

  lcd.begin(16, 2);
  lcd.createChar(0, customChar);
 
  WiFi.mode(WIFI_STA);
 lcd.print("$");
lcd.print(ssid);
  delay(10);
  WiFi.begin(ssid, password);
    lcd.setCursor(0, 1);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);

    lcd.print("#");
  }

lcd.clear();


lcd.setCursor(0, 0);

  lcd.print(WiFi.localIP());
 
  server.begin();
  lcd.setCursor(1, 1);
  lcd.print(port);

}

void loop() 
{
  WiFiClient client = server.available();
  int y = 0;
  if (client) {
    
    
    while(client.connected()){      
      while(client.available()>0){
    
      
       int b = client.read();
       Serial.print(b);
       if(b < 64){
            if(b >= 32){
                lcd.backlight();
                b -= 32 ;
            } else {
                lcd.noBacklight();
            }
            if (b >= 16){
              int y = 1;
              b -= 16;

            int x = b;
            char c = client.read();
            lcd.setCursor(x, y);
            lcd.write(c);
            Serial.println(c);
            } else {
              int y = 0;
          int x = b;
            char c = client.read();
            lcd.setCursor(x, y);
            lcd.write(c);
            Serial.println(c);
            }

            
        }
      }

    }
    client.stop();

  
  }
}
