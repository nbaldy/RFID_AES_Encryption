
/******************************************
  Computer Networks Project
  Elena Falcione and Nicole Baldy
  Code Author: Elena Falcione
  Spring 2021
*******************************************/

/*
   REFERENCES:
   Dr.Leong   ( WWW.B2CQSHOP.COM )
   Miguel Balboa (circuitito.com), Jan, 2012.
   Søren Thing Andersen (access.thing.dk), fall of 2013 (Translation to English, refactored, comments, anti collision, cascade levels.)
   https://github.com/miguelbalboa/rfid
*/


#include <SPI.h>//include the SPI bus library
#include <MFRC522.h>//include the RFID reader library

#define SS_PIN 10  //slave select pin
#define RST_PIN 5  //reset pin
MFRC522 mfrc522(SS_PIN, RST_PIN);        // instatiate a MFRC522 reader object.
MFRC522::MIFARE_Key key;//create a MIFARE_Key struct named 'key', which will hold the card information
char command = 'a';
byte towrite[19];

void setup() {
  Serial.begin(9600);        // Initialize serial communications with the PC
  while (!Serial);
  SPI.begin();               // Init SPI bus
  mfrc522.PCD_Init();        // Init MFRC522 card (in case you wonder what PCD means: proximity coupling device)
  delay(4);       // Optional delay. Some board do need more time after init to be ready, see Readme
  // Prepare the security key for the read and write functions - all six key bytes are set to 0xFF at chip delivery from the factory.
  // Since the cards in the kit are new and the keys were never defined, they are 0xFF
  // if we had a card that was programmed by someone else, we would need to know the key to be able to access it. This key would then need to be stored in 'key' instead.

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;//keyByte is defined in the "MIFARE_Key" 'struct' definition in the .h file of the library
  }
}

int block = 2; //this is the block number we will write into and then read. Do not write into 'sector trailer' block, since this can make the block unusable.
byte blockcontent[16] = {"SubScribe______"};//an array with 16 bytes to be written into one of the 64 card blocks is defined!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//byte blockcontent[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};//all zeros. This can be used to delete a block.
byte readbackblock[18];//This array is used for reading out a block. The MIFARE_Read method requires a buffer that is at least 18 bytes to hold the 16 bytes of a block.

void loop()
{

  int command_not_received = 1;
  Serial.println("Would you like to read or write? (r/w)");
  while (command_not_received)
  {
    while (Serial.available() <= 0) {}
    command = Serial.read();
    if (command == 10)
    {
      continue;
    }
    Serial.print("received: ");
    Serial.println(command);

    if (command == 114 || command == 119)
    {
      while (Serial.available() <= 0) {}
      char wasted_space = Serial.read();

      Serial.println("valid command");
      if (command == 119) //user wants to write, ask for some input
      {
        Serial.println("enter 16 bytes of data: ");
        while (Serial.available() < 16) {}
        Serial.readBytes(towrite,  19);

        Serial.println("command read: ");
        // Pyserial seems to add 3 junk characters at the beginning, remove these
        for (int i = 0; i < 16; i++)
        {
          towrite[i] = towrite[i+3];
          Serial.print(towrite[i], HEX);
          Serial.print(" ");
        }
        Serial.println();

      }
      Serial.println("scan RFID tag");
      command_not_received = 0;
    }
    else
    {
      Serial.println("invalid command");
      Serial.println("Would you like to read or write? (r/w)");
    }
  }

  int read_write_not_done = 1;
  while (read_write_not_done)
  {
    // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
    if ( ! mfrc522.PICC_IsNewCardPresent())
      continue;

    // Select one of the cards
    if ( ! mfrc522.PICC_ReadCardSerial())
      continue;

    // Show some details of the PICC (that is: the tag/card)
    Serial.print(F("Card UID:"));
    dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);

    Serial.println();
    // In this sample we use the second sector,
    // that is: sector #1, covering block #4 up to and including block #7
    byte sector         = 1;
    byte blockAddr      = 4;
    byte trailerBlock   = 7;
    MFRC522::StatusCode status;
    byte buffer[18];
    byte size = sizeof(buffer);

    // Authenticate using key A
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }

    if (command == 114)
    {
      // Read data from the block
      status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(blockAddr, buffer, &size);
      if (status != MFRC522::STATUS_OK) {
        Serial.print(F("MIFARE_Read() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
      }
      Serial.print(F("Data in block ")); Serial.print(blockAddr); Serial.println(F(":"));
      dump_byte_array(buffer, 16); Serial.println();
      Serial.println();
      read_write_not_done = 0;
    }
    // Authenticate using key B
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("PCD_Authenticate() failed: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
    }

    if (command == 119)
    {
      // Write data to the block
      Serial.print(F("Writing data into block ")); Serial.print(blockAddr);
      Serial.println(F(" ..."));
      status = (MFRC522::StatusCode) mfrc522.MIFARE_Write(blockAddr, towrite, 16);
      if (status != MFRC522::STATUS_OK) {
        Serial.print(F("MIFARE_Write() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
      }
      Serial.println();

      // Read data from the block (again, should now be what we have written)
      Serial.print(F("Reading data from block ")); Serial.print(blockAddr);
      Serial.println(F(" ..."));
      status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(blockAddr, buffer, &size);
      if (status != MFRC522::STATUS_OK) {
        Serial.print(F("MIFARE_Read() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
      }
      Serial.print(F("Data in block ")); Serial.print(blockAddr); Serial.println(F(":"));
      dump_byte_array(buffer, 16); Serial.println();

      // Check that data in block is what we have written
      // by counting the number of bytes that are equal
      Serial.println(F("Checking result..."));
      byte count = 0;
      for (byte i = 0; i < 16; i++) {
        // Compare buffer (= what we've read) with towrite (= what we've written)
        if (buffer[i] == towrite[i])
          count++;
      }
      if (count == 16) {
        Serial.println(F("Success :)"));
      } else {
        Serial.println(F("Failure, no match :("));
        Serial.println(F("  perhaps the write didn't work properly..."));
      }
      Serial.println();
      read_write_not_done = 0;
    }

    // Halt PICC
    mfrc522.PICC_HaltA();
    // Stop encryption on PCD
    mfrc522.PCD_StopCrypto1();
  }
}

/**
   Helper routine to dump a byte array as hex values to Serial.
*/
void dump_byte_array(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
}
