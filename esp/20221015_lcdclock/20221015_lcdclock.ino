#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <time.h>
#define SERVER_IP "10.0.1.7:9080" // PC address with emulation on host
#define SERVER_IP "192.168.0.170:8000"
#define ntpServer "pool.ntp.org" //NTP伺服器
#define utcOffset 28800          //UTC偏移量 (此為UTC+8的秒數，即：8*60*60)
#define daylightOffset 0
#ifndef STASSID
#define STASSID "51-9"
#define STAPSK  "28053457"
#endif
#include <LiquidCrystal_I2C.h> 

char formattedTime[9] = "00000000";
char old_formattedTime[9] = "00000000";
short hours = 0;
short minutes = 0;
short day = -1;
short clockInNum = 0;
int last_millis = 0;
int last_display=0;
struct tm now;
ESP8266WiFiMulti wifiMulti;
LiquidCrystal_I2C lcd(0x27,16,2);

#define sound_sensor_pin A0
//create bigfont
//number char
byte UB[8] ={B11111,B11111,B11111,B00000,B00000,B00000,B00000,B00000};
byte MB[8] ={B11111,B11111,B11111,B00000,B00000,B00000,B11111,B11111};
byte LB[8] ={B00000,B00000,B00000,B00000,B00000,B11111,B11111,B11111};
//colon
byte colon_U[8] ={B00000,B00000,B00000,B00000,B11111,B11111,B00000,B00000};
byte colon_D[8] ={B00000,B00000,B11111,B11111,B00000,B00000,B00000,B00000};
int x=0;
char realtime[6];

bool getLocalTime(struct tm * info, uint32_t ms = 5000)
{
  uint32_t start = millis();
  time_t now;
  while ((millis() - start) <= ms) {
    time(&now);
    localtime_r(&now, info);
    if (info->tm_year > (2016 - 1900)) {
      return true;
    }
    delay(10);
  }
  return false;
}
void setup() {
    
    Serial.begin(115200);
    lcd.begin();
//lcd_create_char
    lcd.createChar(0,UB);//upper 
    lcd.createChar(1,LB);//lower 
    lcd.createChar(2,MB);//middle
    lcd.createChar(3,colon_U);
    lcd.createChar(4,colon_D);  
//lcd_setting
    lcd.backlight();
    lcd.clear();
//checkpoint
    Serial.print(F("compiled: "));Serial.print(F(__DATE__));Serial.println(F(__TIME__));

    wifiMulti.addAP("cksh111", "124124124");
    wifiMulti.addAP("asas", "123123123");
    wifiMulti.addAP("51-9", "28053457");
    while (wifiMulti.run() != WL_CONNECTED) {
        delay(300);
        Serial.print(".");
    }
    configTime(utcOffset, daylightOffset, ntpServer);
    int duration = millis();
    while (!getLocalTime(&now));
    duration = millis();
    WiFi.setSleepMode(WIFI_NONE_SLEEP);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    Serial.println("------初始化完成-------");
}

void loop() {
    if (millis() - last_millis > 10000)
    {
        getLocalTime(&now);
        last_millis = millis();
    }
    hours = now.tm_hour;
    minutes = now.tm_min;
    day = now.tm_wday;
    sprintf(formattedTime, "%02d:%02d", hours, minutes);

    Serial.println(formattedTime);


    if (strcmp(formattedTime, old_formattedTime) != 0)
    {
        lcd.clear();
        x=0;
        for (int i=0 ;i<5;i++)
        {
            switch(formattedTime[i])
            {
                case '0':custom0();break;
                case '1':custom1();break;
                case '2':custom2();break;
                case '3':custom3();break;
                case '4':custom4();break;
                case '5':custom5();break;
                case '6':custom6();break;
                case '7':custom7();break;
                case '8':custom8();break;
                case '9':custom9();break;
                case ':':custom_colon();break;
            }
        } 
        last_display=millis();
        strcpy(old_formattedTime,formattedTime);
    }
    

//    custom9();
}


void custom0()
{ // uses segments to build the number 0
    lcd.setCursor(x, 0); 
    lcd.write(255);//0  
    lcd.write(0); 
    lcd.write(255);//2  
    lcd.setCursor(x, 1); 
    lcd.write(255);  
    lcd.write(1);  
    lcd.write(255);
    x+=3;
}
void custom1()
{
    lcd.setCursor(x,0);
    lcd.write(0);
    lcd.write(255);//2
    lcd.setCursor(x,1);
    lcd.write(1);
    lcd.write(255);
    lcd.write(1);
    x+=3;
}
void custom2()
{
    lcd.setCursor(x,0);
    lcd.write(2);
    lcd.write(2);
    lcd.write(255);//2
    lcd.setCursor(x, 1);
    lcd.write(255);
    lcd.write(1);
    lcd.write(1);
    x+=3;
}
void custom3()
{
    lcd.setCursor(x,0);
    lcd.write(2);
    lcd.write(2);
    lcd.write(255);//2
    lcd.setCursor(x, 1);
    lcd.write(1);
    lcd.write(1);
    lcd.write(255); 
    x+=3;
}
void custom4()
{
    lcd.setCursor(x,0);
    lcd.write(255);
    lcd.write(1);
    lcd.write(255);//2
    lcd.setCursor(x+2, 1);
    lcd.write(255);
    x+=3;
}
void custom5()
{
    lcd.setCursor(x,0);
    lcd.write(255);
    lcd.write(2);
    lcd.write(2);
    lcd.setCursor(x, 1);
    lcd.write(1);
    lcd.write(1);
    lcd.write(255);
    x+=3;
}
void custom6()
{
    lcd.setCursor(x,0);
    lcd.write(255);//0
    lcd.write(2);
    lcd.write(2);
    lcd.setCursor(x, 1);
    lcd.write(255);
    lcd.write(1);
    lcd.write(255);
    x+=3;
}
void custom7()
{
    lcd.setCursor(x,0);
    lcd.write(0);
    lcd.write(0);
    lcd.write(255);//2
    lcd.setCursor(x+1, 1);
    lcd.write(255);//0
    x+=3;
}
void custom8()
{
    lcd.setCursor(x,0);
    lcd.write(255);
    lcd.write(2);
    lcd.write(255);
    lcd.setCursor(x, 1);
    lcd.write(255);
    lcd.write(1);
    lcd.write(255);
    x+=3;
}
void custom9()
{
    lcd.setCursor(x,0);
    lcd.write(255);
    lcd.write(2);
    lcd.write(255);
    lcd.setCursor(x+2, 1);
    lcd.write(255);
    x+=3;
}
void custom_colon()
{
    lcd.setCursor(x,0);
    lcd.write(3);
    lcd.setCursor(x, 1);
    lcd.write(4);
    x++;
}
//rfid reader
