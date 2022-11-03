#include <Arduino.h>
#include <U8g2lib.h>
#include <Wire.h>

U8G2_SSD1306_128X64_NONAME_1_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// End of constructor list
void setup(void) {
  u8g2.begin();
  u8g2.enableUTF8Print();		// enable UTF8 support for the Arduino print() function
  u8g2.setFont(u8g2_font_unifont_t_chinese2);
}

void loop(void) {
  u8g2.setFontDirection(0);
  u8g2.firstPage();
  do {
    u8g2.setCursor(0, 15);
    u8g2.print("Hello World!");
    u8g2.setCursor(0, 40);
    u8g2.print("你好世界");		// Chinese "Hello World" 
  } while ( u8g2.nextPage() );
  delay(1000);

  u8g2.firstPage();
  do {
    u8g2.setCursor(0, 15);
    u8g2.print("Hello World!222");
    u8g2.setCursor(0, 40);
    u8g2.print("你好世界");      // Chinese "Hello World" 
  } while ( u8g2.nextPage() );
  delay(1000);
}
