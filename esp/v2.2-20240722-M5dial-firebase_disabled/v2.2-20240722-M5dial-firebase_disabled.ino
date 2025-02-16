// config struct
//fonts https://github.com/m5stack/M5GFX/tree/master/src/lgfx/Fonts/Custom

#define RFID_TYPE_mfrc522 0
#define RFID_TYPE_m5 1
#define RFID_TYPE RFID_TYPE_m5
//#define DEVICE_ID "Kofu-02"
#define DEVICE_ID "Kofu-01"
#define Version "V2.2"

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
#define LINE_TOKEN "Q6scLDKfUjTrgp7XWW8nAsJkmeGvFPy2DKQrHoUgZkT" //for testting
#include <ArduinoJson.h>
#include <time.h>
#include <SPI.h>
#include <U8g2lib.h>
#include <ArduinoOTA.h>
#include <Ticker.h>
#include "M5Dial.h"
#include "data.h"
#include <Firebase_ESP_Client.h>

//Provide the token generation process info.
#include "addons/TokenHelper.h"
//Provide the RTDB payload printing info and other helper functions.
#include "addons/RTDBHelper.h"

#if RFID_TYPE==RFID_TYPE_mfrc522
#include <MFRC522.h>
#endif
#include <TridentTD_LineNotify.h>

// #include <PCF8574.h>    //Include the HCPCF8574 library
// 闪烁时间间隔(秒)
#define I2C_ADD 0x20      //I2C address of the PCF8574
//#define SERVER_IP "https://bao7clockinsys.azurewebsites.net"
#define SERVER_IP "https://clockinkofu.azurewebsites.net" 
//https://friedclockin.azurewebsites.net
#define ntpServer "pool.ntp.org" //NTP伺服器
#define utcOffset 28800          //UTC偏移量 (此為UTC+8的秒數，即：8*60*60)
#define daylightOffset 0
// Insert Firebase project API Key
#define API_KEY "AIzaSyDYStX0RzBFxDCq54tkBfYRWgJINEgFKEE"

// Insert RTDB URLefine the RTDB URL */
#define DATABASE_URL "https://esp32-log-fried-default-rtdb.asia-southeast1.firebasedatabase.app" 

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
String Date="";

struct tm now;
// PCF8574 Port(I2C_ADD);
WiFiMulti wifiMulti;
//Define Firebase Data object
FirebaseData fbdo;

FirebaseAuth auth;
FirebaseConfig config; 

unsigned long sendDataPrevMillis = 0;
bool signupOK = false;

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
void firebase_setup();
void output_configuration();
void sound();
String getValue(String data, char separator, int index);
template<typename T, typename Tsize, typename Tcolor>
void display_unit(const String& text,int x_offset,int y_offset,const T* font,Tsize fontsize,Tcolor color); 
void display_time();
void firebase_send(String data_firebase);


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
    
    //buzzer_configuration
    pinMode(G3, OUTPUT);
    // digitalWrite(10,LOW);
    
    LINE.setToken(LINE_TOKEN);
    // 先換行再顯示
    LINE.notify(DEVICE_ID "系統已經上線 " Version);
    display_unit("Version=" Version,0,0,&fonts::Orbitron_Light_24,1,WHITE);
    delay(2000);
    M5Dial.Display.clear();
//    firebase_setup();
    
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
    
    //get_time
    //output time to lcd
    if (strcmp(formattedTime, old_formattedTime) != 0){
        Date=String(now.tm_year+1900)+"-"+String(now.tm_mon+1)+"-"+String(now.tm_mday)+" "+formattedTime;
        Serial.println("date:"+Date);
        display_time();
    }
    //rfid detecting
    if (M5Dial.Rfid.PICC_IsNewCardPresent() && M5Dial.Rfid.PICC_ReadCardSerial()) {
        
//        tone(G3,3000,1000);
        uint8_t piccType = M5Dial.Rfid.PICC_GetType(M5Dial.Rfid.uid.sak);
        // 顯示卡片內容
        //get now time
        
        dump_byte_array(M5Dial.Rfid.uid.uidByte, M5Dial.Rfid.uid.size); // 讀取卡片+顯示16進制
        Serial.print(F("Card UID:"));
        Serial.println(card_uid);
        
        
        M5Dial.Display.clear();
        
        display_unit("card id:",0,- 30,&fonts::Orbitron_Light_32,1,WHITE);
        display_unit(card_uid,0, + 10,&fonts::Orbitron_Light_32,1,WHITE);
        LINE.notify(DEVICE_ID "打卡紀錄："+String("card_uid")+" "+Date);
//        firebase_send("cardid:"+String(card_uid));
        M5Dial.Rfid.PICC_HaltA();  // 卡片進入停止模式
        delay(800);
        
        send_request("post", card_uid, "");
    }
    
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
    
    WiFiClientSecure client;
//    WiFiClient client;
    HTTPClient http;
    client.setInsecure();
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
            String string_payload = doc.as<String>();
            
            if (!getValue(string_payload, ',', 0).equals("Not Found")){
                M5Dial.Display.clear();
                display_unit(getValue(string_payload, ',', 0),0,0,&fonts::Orbitron_Light_24,1,WHITE);
                delay(1500);
                
                M5Dial.Display.clear();
                display_unit("Report",0,- 90,&fonts::Orbitron_Light_24,1,WHITE);
//                M5Dial.Display.drawPngUrl( SERVER_IP "/static/" + getValue(string_payload, ',', 1) + ".png"
//                                         , 0    // X position
//                                         , 0    // Y position
//                                         , M5Dial.Display.width()  // Width
//                                         , M5Dial.Display.height() // Height
//                                         , 0    // X offset
//                                         , 0    // Y offset
//                                         , 0.5  // X magnification(default = 1.0 , 0 = fitsize , -1 = follow the Y magni)
//                                         , 0.5  // Y magnification(default = 1.0 , 0 = fitsize , -1 = follow the X magni)
//                                         , datum_t::middle_center
//                                       );
                M5Dial.Display.qrcode(SERVER_IP "/preview/"+getValue(string_payload, ',', 1),50,50,190-50,6);
            }
            delay(7000);
            M5Dial.Display.clear();
            display_time();
            
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
//    display_unit("connecting \n to Wi-Fi" Version,0,0,&fonts::Orbitron_Light_24,1,WHITE);
    wifiMulti.addAP("cksh111", "124124124");
    wifiMulti.addAP("asas", "123123123");
    wifiMulti.addAP("paulina", "28053457");
    wifiMulti.addAP("kofu", "0938126816");
    wifiMulti.addAP("22226677", "0927018776");
    wifiMulti.addAP("dsseven77777", "b00829ckkc");
    wifiMulti.addAP("LouisaCoffee", "25988613");
    wifiMulti.addAP("MetroTaipei x Louisa","25112613");
    while (wifiMulti.run() != WL_CONNECTED) {
        delay(300);
        Serial.print(".");
    }
    Serial.println(WiFi.SSID());
}

template<typename T, typename Tsize, typename Tcolor>
void display_unit(const String& text,int x_offset,int y_offset,const T* font,Tsize fontsize,Tcolor color){
    if (_config.Display_type.equals("m5"))
    {
        M5Dial.Display.setTextSize(fontsize);
        M5Dial.Display.setTextFont(font);
        M5Dial.Display.setTextColor(color);
        M5Dial.Display.drawString(text, M5Dial.Display.width() / 2+x_offset, M5Dial.Display.height() / 2 +y_offset);
    }
}

void display_unit(const String& text, int x_offset, int y_offset) {
    display_unit(text, x_offset, y_offset, &fonts::Orbitron_Light_32, 2, WHITE);
}

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
void time_setup() {
    configTime(utcOffset, daylightOffset, ntpServer);//setting
    while (!getLocalTime(&now));//get the real time
    Serial.println("[time_setup]done!");
   
}

void output_configuration() {
  //
}

String getValue(String data, char separator, int index) {
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;
    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i + 1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
void display_time(){
    M5Dial.Display.clear();
    display_unit(String(formattedTime),0,0);
    
    //wifi information
    if (wifiMulti.run() == WL_CONNECTED) {
        display_unit(String(WiFi.SSID()),0,50,&fonts::Orbitron_Light_24,1,GREEN);
    } else {
        display_unit("No WiFi",0,50,&fonts::Orbitron_Light_24,1,RED);
    }
    
    last_display = millis();
    strcpy(old_formattedTime, formattedTime);
 }

void firebase_setup(){
      config.api_key = API_KEY;
      config.database_url = DATABASE_URL;
    
      /* Sign up */
      if (Firebase.signUp(&config, &auth, "", "")){
        Serial.println("ok");
        signupOK = true;
      }
      else{
        Serial.printf("%s\n", config.signer.signupError.message.c_str());
      }
    
      /* Assign the callback function for the long running token generation task */
      config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
      Firebase.begin(&config, &auth);
      Firebase.reconnectWiFi(true);    
}

void firebase_send(String data_firebase){
   if (Firebase.ready() && signupOK ){
    sendDataPrevMillis = millis();
    // Write an Int number on the database path test/int
    if (Firebase.RTDB.setString(&fbdo, DEVICE_ID "/"+String(Date), data_firebase)){
      Serial.println("PASSED");
    }
    else {
      Serial.println("FAILED");
      Serial.println("REASON: " + fbdo.errorReason());
    }
    Serial.println("time:"+String(millis()-sendDataPrevMillis));
  }
}


//
//   if (Firebase.ready() && signupOK ){
//    sendDataPrevMillis = millis();
//    // Write an Int number on the database path test/int
//    if (Firebase.RTDB.setString(&fbdo, DEVICE_ID+"/"+String(formattedTime), count)){
//      Serial.println("PASSED");
//    }
//    else {
//      Serial.println("FAILED");
//      Serial.println("REASON: " + fbdo.errorReason());
//    }
//    Serial.println("time:"+String(millis()-sendDataPrevMillis));
//    
//    
//  }
