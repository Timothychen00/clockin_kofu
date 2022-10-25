#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoJson.h>
#include <time.h>
#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h> 
#include <ESP8266HTTPClient.h>

#define SERVER_IP "192.168.112.86:8000"
#define ntpServer "pool.ntp.org" //NTP伺服器
#define utcOffset 28800          //UTC偏移量 (此為UTC+8的秒數，即：8*60*60)
#define daylightOffset 0
#define RST_PIN         D0
#define SS_PIN          D4  //就是模組上的SDA接腳

char formattedTime[9] = "00000000";
char old_formattedTime[9] = "00000000";
short hours = 0;
short minutes = 0;
short day = -1;
short clockInNum = 0;
int last_millis = 0;
int last_display=0;
int last_button=0;
struct tm now;
String temp = "";
String card_uid = "";
int button=0;

ESP8266WiFiMulti wifiMulti;
LiquidCrystal_I2C lcd(0x27,16,2);
MFRC522 mfrc522;
//create bigfont
//number char
byte UB[8] ={B11111,B11111,B11111,B00000,B00000,B00000,B00000,B00000};
byte MB[8] ={B11111,B11111,B11111,B00000,B00000,B00000,B11111,B11111};
byte LB[8] ={B00000,B00000,B00000,B00000,B00000,B11111,B11111,B11111};
//colon
byte colon_U[8] ={B00000,B00000,B00000,B00000,B11111,B11111,B00000,B00000};
byte colon_D[8] ={B00000,B00000,B11111,B11111,B00000,B00000,B00000,B00000};
int x=0;


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
void send_request(String methods="get",String carduid="",String type="clockin");

void dump_byte_array(byte *buffer, byte bufferSize) {
  temp = "";
  for (byte i = 0; i < bufferSize; i++) {
    temp += String(buffer[i], HEX);
  }
  if (!temp.equals(""))
    card_uid = temp;
  Serial.println();
}


void setup() {
    
    Serial.begin(115200);
    lcd.begin();
    SPI.begin();//初始化SPI總線

    pinMode(10,INPUT_PULLUP);
    
    mfrc522.PCD_Init(SS_PIN, RST_PIN); // 初始化MFRC522卡
    mfrc522.PCD_DumpVersionToSerial();
    //lcd_create_char
    lcd.createChar(0,UB);//upper 
    lcd.createChar(1,LB);//lower 
    lcd.createChar(2,MB);//middle
    lcd.createChar(3,colon_U);
    lcd.createChar(4,colon_D);  
    
    //lcd_setting
    lcd.backlight();
    lcd.clear();

//wifi configuration
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
    Serial.println(WiFi.SSID());
    WiFi.setSleepMode(WIFI_NONE_SLEEP);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    Serial.println("------初始化完成-------");
}

void loop() {
    
    //debug aera
    if(Serial.available()){
        char inputchar=Serial.read();
        switch(inputchar){
            case 'g'://get method test
                Serial.println("sending a get request");send_request("get");break;
            case 'p'://post method test
                Serial.println("sending a post request");send_request("post");break;
        }
    }
    
    //update time
    if (millis() - last_millis > 5000)
    {
        getLocalTime(&now);
        last_millis = millis();
    }
    hours = now.tm_hour;
    minutes = now.tm_min;
    day = now.tm_wday;
    sprintf(formattedTime, "%02d:%02d", hours, minutes);
    //get_time

//    Serial.println(formattedTime);
    
    //output time to lcd
    if (strcmp(formattedTime, old_formattedTime) != 0)
    {
        lcd.clear();
        x=0;//reset cursor
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

    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    // 顯示卡片內容
    //get now time
        dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size); // 讀取卡片+顯示16進制
        Serial.print(F("Card UID:"));
        Serial.println(card_uid);
        mfrc522.PICC_HaltA();  // 卡片進入停止模式
    }
    
    button=!digitalRead(10);
    if(button && millis()-last_button>500){
        String type="";
        Serial.println("waiting for type input");
        while(Serial.available()==0);
        char input=Serial.read();
        switch(input){
            case 'i':
                type="clockin";break;
            case 'q':
                type="clockout";break;
            case 'o':
                type="workovertime";break;
        }
        send_request("post",card_uid,type);
        last_button=millis();
    }
}

void send_request(String methods,String carduid,String type){//默認參數值不能放在定義這邊
    int httpCode=0;
    DynamicJsonDocument doc(1024);
    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    
    if(methods=="post"){
        http.begin(client, "http://" SERVER_IP "/api/staff"); //HTTP
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");
        httpCode = http.POST(String("type=")+type+String("&key=cardid&value=")+carduid);
    }else{
        http.begin(client, "http://" SERVER_IP "/api/manage"); //HTTP
        httpCode = http.GET();
    }

    Serial.print("[HTTP] POST...\n");

    if (httpCode > 0) {
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);

      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.println(payload);
        deserializeJson(doc,payload);
//        serializeJson(doc,Serial);
        Serial.println(doc.as<String>());
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print(doc["id"].as<String>());
        lcd.setCursor(0,1);
        lcd.print(type);
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
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
