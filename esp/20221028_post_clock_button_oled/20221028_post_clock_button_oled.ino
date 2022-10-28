#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoJson.h>
#include <time.h>
#include <SPI.h>
#include <MFRC522.h>
#include <U8g2lib.h>
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
int last_button[3]={0};//clockin clockout overtime
struct tm now;
String temp = "";
String card_uid = "";
int button[3]={0};

ESP8266WiFiMulti wifiMulti;
MFRC522 mfrc522;
U8G2_SSD1306_128X64_NONAME_1_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

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
    SPI.begin();//初始化SPI總線

    pinMode(10,INPUT_PULLUP);
//    pinMode(8,INPUT_PULLUP);
    
    mfrc522.PCD_Init(SS_PIN, RST_PIN); // 初始化MFRC522卡
    mfrc522.PCD_DumpVersionToSerial();

    u8g2.begin();
    u8g2.enableUTF8Print();        // enable UTF8 support for the Arduino print() function
    u8g2.setFont(u8g2_font_unifont_t_chinese2);
    u8g2.print("hello");

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
        u8g2.setFontDirection(0);
        u8g2.clear();
        u8g2.setCursor(0, 15);
        u8g2.print(formattedTime);
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
    
//    button[0]=!digitalRead(8);
    button[2]=!digitalRead(10);
    
    for(int i=0;i<3;i++){
        if(button[i] && millis()-last_button[i]>500){
            String type="";
            Serial.println(String("type:")+i);
//            Serial.println("waiting for type input");
//            while(Serial.available()==0);
//            char input=Serial.read();
            switch(i){
                case 0:
                    type="clockin";break;
                case 1:
                    type="clockout";break;
                case 2:
                    type="workovertime";break;
            }
            send_request("post",card_uid,type);
            last_button[i]=millis();
        }
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
        u8g2.clear();
        u8g2.print(doc["id"].as<String>());
        
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
}
