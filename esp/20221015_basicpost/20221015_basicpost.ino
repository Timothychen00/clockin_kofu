#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
//#define SERVER_IP "10.0.1.7:9080" // PC address with emulation on host
#define SERVER_IP "192.168.0.170:8000"

#ifndef STASSID
#define STASSID "51-9"
#define STAPSK  "28053457"
#endif



void send_request(String method);
void setup() {

  Serial.begin(115200);

  Serial.println();
  Serial.println();
  Serial.println();

  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

}

void loop() {
  if(Serial.available()){
    char inputchar=Serial.read();
    switch(inputchar){
        case 'g':
            Serial.println("sending a get request");send_request("get");break;
        case 'p':
            Serial.println("sending a post request");send_request("post");break;
    }
  }
  
  if ((WiFi.status() != WL_CONNECTED)) {
    Serial.println("losted!!");
  }
}



void send_request(String method="get"){
      // wait for WiFi connection
    
  
    int httpCode=0;
    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    http.begin(client, "http://" SERVER_IP "/api/manage"); //HTTP
    if(method=="post"){
        http.addHeader("Content-Type", "application/x-www-form-urlencoded");
        httpCode = http.POST("name=123");
    }else{
        httpCode = http.GET();
    }

    Serial.print("[HTTP] POST...\n");

    if (httpCode > 0) {
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);

      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.println(payload);
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
 
    
}
