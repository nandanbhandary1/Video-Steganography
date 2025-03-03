from PIL import Image
import os.path
from os import path
import base64
from colorama import init
import os
import getpass
import sys
from Crypto.Cipher import AES  # type: ignore
from Crypto.Hash import SHA256  # type: ignore
from Crypto import Random  # type: ignore

headerText = "M6nMjy5THr2J"


def encrypt(key, source, encode=True):
    key = SHA256.new(
        key
    ).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
    source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
    return base64.b64encode(data).decode() if encode else data


def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode())
    key = SHA256.new(
        key
    ).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[: AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size :])  # decrypt
    padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if (
        data[-padding:] != bytes([padding]) * padding
    ):  # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


def convertToRGB(img):
    try:
        rgba_image = img
        rgba_image.load()
        background = Image.new("RGB", rgba_image.size, (255, 255, 255))
        background.paste(rgba_image, mask=rgba_image.split()[3])
        print("Converted image to RGB ")
        return background
    except Exception as e:
        print("Couldn't convert image to RGB - %s" % e)


def getPixelCount(img):
    width, height = Image.open(img).size
    return width * height


def encodeImage(image, message, filename):
    try:
        width, height = image.size
        pix = image.getdata()

        current_pixel = 0
        tmp = 0
        # three_pixels = []
        x = 0
        y = 0
        for ch in message:
            binary_value = format(ord(ch), "08b")

            # For each character, get 3 pixels at a time
            p1 = pix[current_pixel]
            p2 = pix[current_pixel + 1]
            p3 = pix[current_pixel + 2]

            three_pixels = [val for val in p1 + p2 + p3]

            for i in range(0, 8):
                current_bit = binary_value[i]

                # 0 - Even
                # 1 - Odd
                if current_bit == "0":
                    if three_pixels[i] % 2 != 0:
                        three_pixels[i] = (
                            three_pixels[i] - 1
                            if three_pixels[i] == 255
                            else three_pixels[i] + 1
                        )
                elif current_bit == "1":
                    if three_pixels[i] % 2 == 0:
                        three_pixels[i] = (
                            three_pixels[i] - 1
                            if three_pixels[i] == 255
                            else three_pixels[i] + 1
                        )

            current_pixel += 3
            tmp += 1

            # Set 9th value
            if tmp == len(message):
                # Make as 1 (odd) - stop reading
                if three_pixels[-1] % 2 == 0:
                    three_pixels[-1] = (
                        three_pixels[-1] - 1
                        if three_pixels[-1] == 255
                        else three_pixels[-1] + 1
                    )
            else:
                # Make as 0 (even) - continue reading
                if three_pixels[-1] % 2 != 0:
                    three_pixels[-1] = (
                        three_pixels[-1] - 1
                        if three_pixels[-1] == 255
                        else three_pixels[-1] + 1
                    )

            three_pixels = tuple(three_pixels)

            st = 0
            end = 3

            for i in range(0, 3):

                image.putpixel((x, y), three_pixels[st:end])
                st += 3
                end += 3

                if x == width - 1:
                    x = 0
                    y += 1
                else:
                    x += 1

        encoded_filename = filename.split(".")[0] + "-enc.png"
        image.save(os.path.join("frame_folder", encoded_filename))
    except Exception as e:
        print("An error occured - %s" % e)
        sys.exit(0)


def decodeImage(image):

    try:
        pix = image.getdata()
        current_pixel = 0
        decoded = ""
        while True:
            # Get 3 pixels each time
            binary_value = ""
            p1 = pix[current_pixel]
            p2 = pix[current_pixel + 1]
            p3 = pix[current_pixel + 2]
            three_pixels = [val for val in p1 + p2 + p3]

            for i in range(0, 8):
                if three_pixels[i] % 2 == 0:
                    # add 0
                    binary_value += "0"
                elif three_pixels[i] % 2 != 0:
                    # add 1
                    binary_value += "1"

            # Convert binary value to ascii and add to string
            binary_value.strip()
            ascii_value = int(binary_value, 2)
            decoded += chr(ascii_value)
            current_pixel += 3

            if three_pixels[-1] % 2 != 0:
                break

        # print("Decoded: %s"%decoded)
        return decoded
    except Exception as e:
        print("An error occured - %s" % e)
        sys.exit()


def main(op, password, img_path, message=""):
    # insertHeaders(img)
    if op == 1:
        img = img_path
        message = headerText + message
        if not (path.exists(img)):
            raise Exception("Image not found!")

        if (len(message) + len(headerText)) * 3 > getPixelCount(img):
            raise Exception("Given message is too long to be encoded in the image.")

        cipher = ""
        if password != "":
            cipher = encrypt(key=password.encode(), source=message.encode())
            cipher = headerText + cipher
        else:
            cipher = headerText + message

        image = Image.open(img)
        # print("Image Mode: %s" % image.mode)
        if image.mode != "RGB":
            image = convertToRGB(image)
        newimg = image.copy()
        encodeImage(
            image=newimg,
            message=cipher,
            filename=img.split("\\").pop(),
        )

    elif op == 2:
        img = img_path
        if not (path.exists(img)):
            raise Exception("Image not found!")

        image = Image.open(img)

        cipher = decodeImage(image)
        header = cipher[: len(headerText)]
        if header.strip() != headerText:
            return "Invalid data!"

        decrypted = ""
        cipher = cipher[len(headerText) :]

        if password != "":
            # print("Message is :- ", password)
            try:
                # pass
                decrypted = decrypt(key=password.encode(), source=cipher)
                header = decrypted.decode()[: len(headerText)]
                if header != headerText:
                    print("Wrong password!")
                    sys.exit(0)

                decrypted = decrypted[len(headerText) :]
                return decrypted.decode("utf-8")
            except Exception as e:
                print("Wrong password!")
                sys.exit(0)
        else:
            # print("Simple Decoded Text: - ", cipher[len(headerText) :])
            return cipher[len(headerText) :]


if __name__ == "__main__":

    print(
        "IMGHIDE allows you to hide texts inside an image. You can also protect these texts with a password using AES-256."
    )
    print()
    main()
