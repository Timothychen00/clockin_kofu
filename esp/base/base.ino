#include <SPI.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <time.h>
#define ntpServer "pool.ntp.org" //NTP伺服器
#define utcOffset 28800          //UTC偏移量 (此為UTC+8的秒數，即：8*60*60)
#define daylightOffset 0

#define URL "http://127.0.0.1:5000/api/manage"
//rfid var
String card_uid = "";
char formattedTime[9] = "00000000";
String subTime;//時間戳
short hours = 0;
short minutes = 0;
short clockInNum = 0;
short day = -1;
bool root = false;
String temp = "";
bool isClear = false;
int last_millis = 0;
int reset_button = 0;
struct tm now;
// 設定時區 *60分 * 60秒，例如:
// GMT +1 = 3600
// GMT +8 = 28800  台灣時區
// GMT 0 = 0

//wifi-time
ESP8266WiFiMulti wifiMulti;
//rfid reader
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
  SPI.begin();        // 初始化SPI介面

  pinMode(D8, OUTPUT);

  wifiMulti.addAP("cksh111", "124124124");
  wifiMulti.addAP("asas", "123123123");
  wifiMulti.addAP("51-9", "28053457");


  while (wifiMulti.run() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Wifi connected!");
  Serial.print("Connected to ");
  Serial.println(WiFi.SSID());
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  IPAddress ip = WiFi.localIP();

  Serial.println("MAC Address:" + WiFi.macAddress());

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
  digitalWrite(D8, 1);
  if (millis() - last_millis > 10000)
  {
    getLocalTime(&now);
    last_millis = millis();
  }
  esp8266Http();
  hours = now.tm_hour;
  minutes = now.tm_min;
  day = now.tm_wday;
  sprintf(formattedTime, "%02d:%02d:%02d", hours, minutes, now.tm_sec);
  Serial.println(formattedTime);
  
}

void esp8266Http(){
    HTTPClient httpClient;

//    "http://127.0.0.1:5000/api/manage";
  //配置请求地址。此处也可以不使用端口号和PATH而单纯的
    httpClient.begin(URL); 
    Serial.print("URL: "); Serial.println(URL);
 
  //启动连接并发送HTTP请求
    int httpCode = httpClient.GET();
    Serial.print("Send GET request to URL: ");
    Serial.println(URL);
  
  //如果服务器响应OK则从服务器获取响应体信息并通过串口输出
  //如果服务器不响应OK则将服务器响应状态码通过串口输出
  if (httpCode == HTTP_CODE_OK) {
    String responsePayload = httpClient.getString();
    Serial.println("Server Response Payload: ");
    Serial.println(responsePayload);
  } else {
    Serial.println("Server Respose Code：");
    Serial.println(httpCode);
  }
 
  //关闭ESP8266与服务器连接
  httpClient.end();
    
    
    
    
    
}
