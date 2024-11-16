import serial
from PIL import Image
import logging
from pathlib import Path
from config import SerialConfig as config

__assets = Path(__file__).parent/"assets"
BITMAP_PATH = str(__assets/"logoimg.bmp")

logger = logging.getLogger(__name__)

class Printer:
    def __init__(self, port=config.PORT, baudrate=config.BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self.logo = self.create_image_buffer("BITMAP_PATH")

    def create_image_buffer(self, image_path):
            """
            画像を1ビットモノクロに変換し、ラスタ形式のバッファを作成する。
            """
            img = Image.open(image_path).convert('1')  # モノクロ変換 (1ビット)
            width, height = img.size

            # 横幅を8で割り切れるように調整
            if width % 8 != 0:
                new_width = (width + 7) // 8 * 8
                img = img.resize((new_width, height))
                width = new_width

            # ビットマップデータの生成
            bitmap_data = bytearray()
            for y in range(height):
                for x in range(0, width, 8):
                    byte = 0
                    for bit in range(8):
                        if x + bit < width and img.getpixel((x + bit, y)) == 0:
                            byte |= (1 << (7 - bit))
                    bitmap_data.append(byte)

            # xL, xH, yL, yHを計算
            xL = width // 8 % 256
            xH = width // 8 // 256
            yL = height % 256
            yH = height // 256

            # バッファ作成 (GS v 0 コマンド)
            logo = bytearray(b'\x1D\x76\x30\x00' + bytes([xL, xH, yL, yH]))
            logo.extend(bitmap_data)
            return logo
    
    def print_receipt(self, order_id, orderL, totalL, total, payment, note, menuL, order_date):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            ser.write(b'\x1B\x40')  # ESC @ (プリンタ初期化)
            ser.write(self.logo)  # 画像データを送信
            buffer = b'\x1D\x21\x00' + "福桔祭店    {}\n".format(order_date.strftime("%Y/%m/%d %H:%M:%S")).encode("shift_jis") + b'\x1D\x21\x10'
            
            buffer += b'\x1B\x2D\x01' + "                \n".encode("shift_jis") + b'\x1B\x2D\x00'
            
            # Iterate over each menu item and print the details if the count > 0
            for i in range(len(menuL)):
                if orderL[i]['quantity'] > 0:
                    buffer += "{0}{1}@{2} {3}ｺ\n".format(menuL[i]['name'], " " * (6 - len(menuL[i]['name'])), menuL[i]['price'], orderL[i]['quantity']).encode("shift_jis")
                    buffer += "{0}￥{1:,}\n".format(
                                    " " * (13 - (len(str(totalL[i])) if len(str(totalL[i])) < 4 else (len(str(totalL[i])) + 1))),
                                    totalL[i]).encode("shift_jis")
            if note:
                buffer += b'\x1D\x21\x00' + "\n{}\n".format(note).encode("shift_jis") + b'\x1D\x21\x10'
            
            buffer += b'\x1B\x2D\x01' + "                \n".encode("shift_jis") + b'\x1B\x2D\x00'
            
            buffer += "合計{0}￥{1:,}\n".format(
                            " " * (9 - (len(str(total)) if len(str(total)) < 4 else (len(str(total)) + 1))),
                            total).encode("shift_jis")
            
            buffer += "お預り{0}￥{1:,}\n".format(
                            " " * (7 - (len(str(payment)) if len(str(payment)) < 4 else (len(str(payment)) + 1))),
                            payment).encode("shift_jis")
            
            buffer += "おつり{0}￥{1:,}\n".format(
                            " " * (7 - (len(str(payment - total)) if len(str(payment - total)) < 4 else (len(str(payment - total)) + 1))),
                            (payment - total)).encode("shift_jis")
            
            buffer += b'\x1D\x21\x00' + "\n          Thank you!".encode("shift_jis")
            buffer += b'\x1D\x21\x56' + b'\x1D\x42\x01' + "\n {} \n".format(order_id).encode("shift_jis") + b'\x1D\x42\x00'
            buffer += b'\x1D\x56\x42\x2D'

            ser.write(buffer)
            
            ser.close()
        except Exception as e:
            logger.error(f"Error printing receipt: {e}")