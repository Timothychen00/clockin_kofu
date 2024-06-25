// config struct
#define RFID_TYPE_mfrc522 0
#define RFID_TYPE_m5 1
#define RFID_TYPE RFID_TYPE_m5 

struct CONFIG {
  bool Display = true;
  bool ExtendIO = false; //PCF8574
  bool RFID = true;
  bool buttonless = true;
  String  Display_type = "m5"; //u8g2 or M5 Display
  int rfid_type = RFID_TYPE;

  String board = "esp32";
  String mode = "test"; // test or production
  String connection_mode = "buttonless";

} _config;

#ifdef ESP32
    #include <WiFi.h>
    #include <WiFiMulti.h>
    #include <HTTPClient.h>
#else
    #include <ESP8266WiFi.h>
    #include <ESP8266WiFiMulti.h>
    #include <ESP8266HTTPClient.h>
#endif

#define ARDUINOJSON_ENABLE_PROGMEM 0
#define LINE_TOKEN "Q6scLDKfUjTrgp7XWW8nAsJkmeGvFPy2DKQrHoUgZkT"
#include <ArduinoJson.h>
#include <time.h>
#include <SPI.h>
#include <U8g2lib.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include "M5Dial.h"
#include "data.h"
#if RFID_TYPE==RFID_TYPE_mfrc522
    #include <MFRC522.h>
#endif
#include <TridentTD_LineNotify.h>

// #include <PCF8574.h>    //Include the HCPCF8574 library
// 闪烁时间间隔(秒)
#define I2C_ADD 0x20      //I2C address of the PCF8574
//#define SERVER_IP "https://bao7clockinsys.azurewebsites.net"
#define SERVER_IP "http://192.168.0.18:8000"
#define ntpServer "pool.ntp.org" //NTP伺服器
#define utcOffset 28800          //UTC偏移量 (此為UTC+8的秒數，即：8*60*60)
#define daylightOffset 0

#if RFID_TYPE==RFID_TYPE_mfrc522
#define RST_PIN         D0
#define SS_PIN          D4  //就是模組上的SDA接腳
#endif

#define imgWidth 128
#define imgHeight 64  //這裡只用到48的高度，因為上方要放文字

char formattedTime[9] = "00000000";
char old_formattedTime[9] = "00000000";


short hours = 0;
short minutes = 0;
short day = -1;
short clockInNum = 0;
const int blinkInterval = 2;

int last_millis = 0;
int card_uid_timestamp = 0;
int last_display = 0;
int last_button[3] = {0}; //clockin clockout overtime
int button[3] = {0};

String temp = "";
String card_uid = "";
String connection_mode = "buttonless";

struct tm now;
// PCF8574 Port(I2C_ADD);
WiFiMulti wifiMulti;

//WiFiClient client;

#if RFID_TYPE==RFID_TYPE_mfrc522
MFRC522 mfrc522;
#endif

U8G2_SSD1306_128X64_NONAME_1_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

#ifndef ESP32  //esp32 already defined this
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
#endif

void send_request(String methods = "get", String carduid = "", String type = "clockin");
void dump_byte_array(byte *buffer, byte bufferSize);//rfid gen uid string func
void multi_wifi_setup();
void display_unit(String data1, String data2 = " ");
void display_unit_setup();
void OTA_setup();
void time_setup();
void output_configuration();
void sound();

void setup() {
    display_unit_setup();
    Serial.begin(115200);
    SPI.begin();//初始化SPI總線
    #if RFID_TYPE==RFID_TYPE_mfrc522
      mfrc522.PCD_Init(SS_PIN, RST_PIN); // 初始化MFRC522卡
      mfrc522.PCD_DumpVersionToSerial();
    #endif
    
    multi_wifi_setup();//wifi configuration
    time_setup();
    OTA_setup();//ota configuration

    // WiFi.setSleepMode(WIFI_NONE_SLEEP);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    Serial.println("------初始化完成-------");
    Serial.println(connection_mode);
    Serial.println(connection_mode == "buttonless");
    
    M5Dial.Display.clear();
    //button
//    if (connection_mode != "buttonless") {
//    // Port.pinMode(0, INPUT_PULLUP);
//    // Port.pinMode(1, INPUT_PULLUP);
//    // Port.pinMode(2, INPUT_PULLUP);
//    // Port.begin();
//    }
    //buzzer_configuration
     pinMode(G3,OUTPUT);
    // digitalWrite(10,LOW);
    
    LINE.setToken(LINE_TOKEN);
    // 先換行再顯示
    LINE.notify("系統已經上線");
}

void loop() {
    ArduinoOTA.handle();
    //debug aera
    if (Serial.available()) {
        char inputchar = Serial.read();
        switch (inputchar) {
            case 'g'://get method test
            Serial.println("sending a get request"); send_request("get"); break;
            case 'p'://post method test
            Serial.println("sending a post request"); send_request("post"); break;
        }
    }

    //update time
    if (millis() - last_millis > 5000)
    {
        getLocalTime(&now);
        last_millis = millis();
    }
    if (millis() - card_uid_timestamp > 30000) {
        card_uid = "";
    }
    hours = now.tm_hour;
    minutes = now.tm_min;
    day = now.tm_wday;
    sprintf(formattedTime, "%02d:%02d", hours, minutes);
    
    //get_tim
    //output time to lcd
    if (strcmp(formattedTime, old_formattedTime) != 0)
    {
        //        display_unit("u8g2",formattedTime);
        M5Dial.Display.clear();
        M5Dial.Display.setTextSize(2);
        M5Dial.Display.drawString(String(formattedTime), M5Dial.Display.width() / 2, M5Dial.Display.height() / 2);
        
        last_display = millis();
        strcpy(old_formattedTime, formattedTime);
    }
    
    //rfid detecting
    if (M5Dial.Rfid.PICC_IsNewCardPresent() && M5Dial.Rfid.PICC_ReadCardSerial()) {
//         digitalWrite(G3,HIGH);
//        M5Dial.Speaker.tone(2000, 1000);
//        tone(G3,3000,1000);
        uint8_t piccType = M5Dial.Rfid.PICC_GetType(M5Dial.Rfid.uid.sak);
        // 顯示卡片內容
        //get now time
        dump_byte_array(M5Dial.Rfid.uid.uidByte, M5Dial.Rfid.uid.size); // 讀取卡片+顯示16進制
        Serial.print(F("Card UID:"));
        Serial.println(card_uid);
        display_unit("card id:",card_uid);
        
        M5Dial.Rfid.PICC_HaltA();  // 卡片進入停止模式
        delay(1000);
        
        send_request("post", card_uid, "");
    }
//     digitalWrite(G3,LOW);

    
    if (_config.Display_type.equals("button")) { //only button mode sent here
        // button[0]=!Port.digitalRead(0);
        // button[1]=!Port.digitalRead(1);
        // button[2]=!Port.digitalRead(2);
        
        
        for (int i = 0; i < 3; i++) {
          if (button[i] && millis() - last_button[i] > 500) {
            String type = "";
            Serial.println("waiting for type input");
            switch (i) {
              case 0:
                type = "clockin"; break;
              case 1:
                type = "clockout"; break;
              case 2:
                type = "workovertime"; break;
            }
            send_request("post", card_uid, type);
            last_button[i] = millis();
          }
        }
    }
}



void send_request(String methods, String carduid, String type) { //默認參數值不能放在定義這邊
  int httpCode = 0;
  DynamicJsonDocument doc(1024);

//  WiFiClientSecure client;
  WiFiClient client;
  HTTPClient http;
//  client.setInsecure();
  Serial.print("[HTTP] begin...\n");
  int timestart = millis();
  http.setTimeout(5000);
  if (methods == "post") {

    http.begin(client,  SERVER_IP "/api/staff"); //HTTP
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");


    if (connection_mode == "buttonless")
      httpCode = http.POST(String("connection_mode=buttonless") + String("&key=cardid&value=") + carduid);
    else
      httpCode = http.POST(String("type=") + type + String("&key=cardid&value=") + carduid);

  } else {
    http.begin(client,  SERVER_IP "/api/manage"); //HTTP
    httpCode = http.GET();
  }


  Serial.print("[HTTP] POST...\n");
  Serial.println(millis() - timestart + String("ms"));

  if (httpCode > 0) {
    Serial.printf("[HTTP] POST... code: %d\n", httpCode);

    if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
      const String& payload = http.getString();
      Serial.println("received payload:\n<<");
      Serial.println(payload);
      deserializeJson(doc, payload);
      Serial.println(doc.as<String>());

      M5Dial.Display.clear();
      M5Dial.Display.drawString(doc.as<String>(), M5Dial.Display.width() / 2, M5Dial.Display.height() / 2);
      
      M5Dial.Display.setTextSize(2);
      M5Dial.Display.drawString("Report:", M5Dial.Display.width() / 2-30, M5Dial.Display.height() / 2-100);
      M5Dial.Display.drawPngUrl( SERVER_IP "/static/"+name+".png"
                                , 0    // X position
                                , 0    // Y position
                                , M5Dial.Display.width()  // Width
                                , M5Dial.Display.height() // Height
                                , 0    // X offset
                                , 0    // Y offset
                                , 0.5  // X magnification(default = 1.0 , 0 = fitsize , -1 = follow the Y magni)
                                , 0.5  // Y magnification(default = 1.0 , 0 = fitsize , -1 = follow the X magni)
                                , datum_t::middle_center
                              );
                          
      delay(5000);
      Serial.println(">>");
      if (doc.as<String>() != "null") {
        // digitalWrite(10,1);
        // delay(100);
        // digitalWrite(10,0);
        // delay(50);
        // digitalWrite(10,1);
        // delay(100);
        // digitalWrite(10,0);
        // delay(50);
      }
    } else {
      const String& payload = http.getString();
        Serial.println(payload);    
      deserializeJson(doc, payload);
      Serial.println(doc.as<String>());
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());

      Serial.println("ERRRR");

      //        display_unit("u8g2","Try Again",type+String(" Try Again!"));
      M5Dial.Display.clear();
      M5Dial.Display.drawString("Try Again", M5Dial.Display.width() / 2, M5Dial.Display.height() / 2);

      delay(1000);
      Serial.println(">>");
      if (doc.as<String>() != "null") {
        // digitalWrite(10,1);
        // delay(500);
        // digitalWrite(10,0);
        // delay(50);
        // digitalWrite(10,1);
        // delay(500);
        // digitalWrite(10,0);
        // delay(50);
      }
    }
    card_uid = "";
  }
  http.end();
}

void dump_byte_array(byte *buffer, byte bufferSize) {
    temp = "";
    for (byte i = 0; i < bufferSize; i++) {
        temp += String(buffer[i], HEX);
    }
    if (!temp.equals("")) {
        card_uid = temp;
        card_uid_timestamp = millis();
    }
    Serial.println();
}

void multi_wifi_setup() {
    wifiMulti.addAP("cksh111", "124124124");
    wifiMulti.addAP("asas", "123123123");
    wifiMulti.addAP("paulina", "28053457");
    wifiMulti.addAP("kofu", "0938126816");
    wifiMulti.addAP("22226677", "0927018776");
    wifiMulti.addAP("dsseven77777", "b00829ckkc");
    wifiMulti.addAP("LouisaCoffee", "25112613");
    while (wifiMulti.run() != WL_CONNECTED) {
        delay(300);
        Serial.print(".");
    }
    Serial.println(WiFi.SSID());
}

void display_unit(String data1, String data2) {
    if (_config.Display_type.equals("m5"))//#這邊可能有bug
    {
        M5Dial.Display.clear();
        M5Dial.Display.setTextSize(1);
        M5Dial.Display.drawString(data1, M5Dial.Display.width() / 2, M5Dial.Display.height() / 2-30);
        M5Dial.Display.drawString(data2, M5Dial.Display.width() / 2, M5Dial.Display.height() / 2+10);

    }

          // u8g2.setFontDirection(0);
      // u8g2.firstPage();
      // do {
  
      //     u8g2.setCursor(15, 15);
      //     Serial.println(data1);
      //     u8g2.print(data1);
      //     u8g2.setCursor(15, 30);
      //     u8g2.print(data2);
      // } while ( u8g2.nextPage() );
}


//void display_unit_image(String type="m5",String img_type,pointer){
//    if (type.equals("m5"))//#這邊可能有bug
//    {
//          display.drawJpg( pointer  // data_pointer
//                         , ~0u  // data_length (~0u = auto)
//                         , 0    // X position
//                         , 0    // Y position
//                         , display.width()  // Width
//                         , display.height() // Height
//                         , 0    // X offset
//                         , 0    // Y offset
//                         , 0  // X magnification(default = 1.0 , 0 = fitsize , -1 = follow the Y magni)
//                         , 0  // Y magnification(default = 1.0 , 0 = fitsize , -1 = follow the X magni)
//                         , datum_t::middle_center
//                         );
//    }
//}

void display_unit_setup() {
    if (_config.Display_type.equals("u8g2")) {
        u8g2.begin();
        u8g2.enableUTF8Print();        // enable UTF8 support for the Arduino print() function
        u8g2.setFont(u8g2_font_tenstamps_mf);
    
        do {
            u8g2.drawXBMP(0, 0, imgWidth, imgHeight, logo_bmp); //繪圖
        } while ( u8g2.nextPage() );
    } else {
        auto cfg = M5.config();
        M5Dial.begin(cfg, false, true);
        M5Dial.Display.setTextColor(WHITE);
        M5Dial.Display.setTextDatum(middle_center);
        M5Dial.Display.setTextFont(&fonts::Orbitron_Light_32);
        M5Dial.Display.setTextSize(2);
        M5Dial.Display.drawJpg( logo  // data_pointer
                            , ~0u  // data_length (~0u = auto)
                            , 0    // X position
                            , 0    // Y position
                            , M5Dial.Display.width()  // Width
                            , M5Dial.Display.height() // Height
                            , 0    // X offset
                            , 0    // Y offset
                            , 0  // X magnification(default = 1.0 , 0 = fitsize , -1 = follow the Y magni)
                            , 0  // Y magnification(default = 1.0 , 0 = fitsize , -1 = follow the X magni)
                            , datum_t::middle_center
                          );
        delay(1000);
  }
}

void OTA_setup() {
  ArduinoOTA.setHostname("Clockin-");
  ArduinoOTA.setPassword("0000");
  ArduinoOTA.begin();
  Serial.println("[time_setup]done!");
}
void time_setup(){
    configTime(utcOffset, daylightOffset, ntpServer);//setting
    while (!getLocalTime(&now));//get the real time
    Serial.println("[time_setup]done!");
}
void output_configuration(){
    //
}
