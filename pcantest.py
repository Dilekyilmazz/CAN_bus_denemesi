import ctypes
from ctypes import c_ubyte, c_uint32, c_uint16, byref

# Sabit tipleri tanımlama (ctypes ile)
TPCANHandle = c_uint16  # 16-bit unsigned integer (kanal numarası için)
TPCANBaudrate = c_uint32  # 32-bit unsigned integer (baud rate için)

# PCAN-Basic API'nin kanal ve baud rate sabitleri
PCAN_USBBUS1 = TPCANHandle(0x51)  # PCAN-USB interface, channel 1
PCAN_BAUD_250K = TPCANBaudrate(0x011C)  # Baud rate: 250Kbps (0x011C)

# PCANBasic.dll dosyasının yolu
pcan_basic = ctypes.windll.LoadLibrary('C:\\Users\\dilek\\OneDrive\\Masaüstü\\pcan_test\\PCANBasic.dll')

# TPCANMsg yapısı (CAN mesaj yapısı)
class TPCANMsg(ctypes.Structure):
    _fields_ = [("ID", c_uint32),
                ("MSGTYPE", c_ubyte),
                ("LEN", c_ubyte),
                ("DATA", c_ubyte * 8)]  # 8 byte veri alanı

# CAN hattına bağlanma fonksiyonu
def connect_to_can():
    result = pcan_basic.CAN_Initialize(PCAN_USBBUS1, PCAN_BAUD_250K)
    if result == 0:
        print("CAN hattına başarıyla bağlanıldı!")
        return True
    else:
        print(f"CAN hattına bağlanma başarısız. Hata kodu: {result}")
        return False
    

# CAN mesajı alma fonksiyonu
def receive_can_message():
    can_msg = TPCANMsg()
    result = pcan_basic.CAN_Read(PCAN_USBBUS1, byref(can_msg), None)
    if result == 0:
        print(f"Mesaj alındı! ID: {hex(can_msg.ID)}, Data: {list(can_msg.DATA[:can_msg.LEN])}")
    else:
        print(f"Mesaj alma başarısız. Hata kodu: {result}")


# CAN mesajı gönderme fonksiyonu (Kullanıcıdan mesaj ID'si ve veri alınacak)
def send_can_message():
    can_msg = TPCANMsg()

    # Konsoldan kullanıcıdan ID ve veri alımı
    try:
        msg_id = int(input("Göndermek istediğiniz mesaj ID'sini (hex formatında) girin (ör: 100): "), 16)
        can_msg.ID = msg_id
        can_msg.MSGTYPE = 0x00  # Standart mesaj tipi
        
        # Veri uzunluğunu belirleme
        data_len = int(input("Veri uzunluğunu (0-8) girin: "))
        if data_len > 8 or data_len < 0:
            raise ValueError("Geçersiz veri uzunluğu. 0 ile 8 arasında bir değer girin.")
        
        can_msg.LEN = data_len

        # Verileri kullanıcıdan alıp CAN mesajına ekleme
        can_data = []
        for i in range(data_len):
            data_byte = int(input(f"Veri byte {i+1}: "), 16)
            can_data.append(data_byte)

        # Veriyi CAN mesajına aktarma
        can_msg.DATA = (c_ubyte * 8)(*can_data)

        # Mesaj gönderme
        result = pcan_basic.CAN_Write(PCAN_USBBUS1, byref(can_msg))
        if result == 0:
            print(f"Mesaj başarıyla gönderildi! ID: {hex(can_msg.ID)}, Data: {list(can_msg.DATA[:can_msg.LEN])}")
        else:
            print(f"Mesaj gönderme başarısız. Hata kodu: {result}")

    except ValueError as e:
        print(f"Hatalı giriş: {e}")


# Bağlantıyı kapatma fonksiyonu
def close_can_connection():
    pcan_basic.CAN_Uninitialize(PCAN_USBBUS1)
    print("CAN hattı kapatıldı.")

# Ana program
def main():
    if connect_to_can():
        while True:
            # Kullanıcıdan işlem seçimi
            print("\nSeçenekler:\n1. Mesaj Gönder\n2. Mesaj Al\n3. Çıkış")
            choice = input("Seçiminiz: ")

            if choice == '1':
                send_can_message()  # CAN mesajı gönder
            elif choice == '2':
                receive_can_message()  # CAN mesajı al
            elif choice == '3':
                close_can_connection()  # CAN hattını kapatma
                break
            else:
                print("Geçersiz seçenek. Lütfen tekrar deneyin.")

if __name__ == "__main__":
    main()
