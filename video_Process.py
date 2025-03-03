import Stegno_image
import getpass
import cv2
import os
from subprocess import call, STDOUT
import shlex
from PIL import Image
import math
from colorama import init
from termcolor import cprint
from pyfiglet import figlet_format
from rich import print
from rich.console import Console
from rich.table import Table
import os
import getpass
from rich.progress import track

temp_folder = "frame_folder"
console = Console()


def split_string(s_str, count=10):
    per_c = math.ceil(len(s_str) / count)
    c_cout = 1
    out_str = ""
    split_list = []
    for s in s_str:
        out_str += s
        c_cout += 1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str = ""
            c_cout = 0
    if c_cout != 0:
        split_list.append(out_str)
    return split_list


def createTmp():
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)


def countFrames(path):
    cap = cv2.VideoCapture(path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return length


# Function to extract frames
def FrameCapture(path, op, password, message=""):
    # Path to video file
    createTmp()
    vidObj = cv2.VideoCapture(path)
    # Used as counter variable
    count = 0
    total_frame = countFrames(path)
    split_string_list = split_string(message)
    position = 0
    outputMessage = ""
    while count < total_frame:
        success, image = vidObj.read()
        if op == 1:
            cv2.imwrite(temp_folder + "\\" + "frame%d.png" % count, image)

        if op == 1:
            if position < len(split_string_list):
                print(
                    "Input in image working :- ",
                    split_string_list[position],
                )
                Stegno_image.main(
                    op,
                    password=password,
                    message=split_string_list[position],
                    img_path=temp_folder + "\\" + "frame%d.png" % count,
                )
                position += 1
                os.remove(temp_folder + "\\" + "frame%d.png" % count)

        if op == 2:
            str = Stegno_image.main(
                op,
                password=password,
                img_path=temp_folder + "\\" + "frame%d.png" % count,
            )
            if str == "Invalid data!":
                break
            outputMessage = outputMessage + str

        count += 1

    if op == 1:
        print("[cyan]Please wait....[/cyan]")
        makeVideoFromFrame()
    # if op == 2:
    # To delete frames
    #     images = [img for img in os.listdir("frame_folder") if img.endswith(".png")]
    #     for img in images:
    #         os.remove(os.path.join("frame_folder", img))

    if op == 2:
        print("[green]Message is :-\n[bold]%s[/bold][/green]" % outputMessage)


def makeVideoFromFrame():
    images = [img for img in os.listdir("frame_folder") if img.endswith(".png")]
    for img in images:
        if img.count("-enc") == 1:
            newImgName = img.split("-")[0] + ".png"
            os.rename("frame_folder//" + img, "frame_folder//" + newImgName)

    cmd = shlex.split(
        "ffmpeg -framerate 29.92 -i frame_folder/frame%01d.png -vcodec libx264 -profile:v high444 -crf 0 -preset ultrafast output.mov"
    )
    call(
        cmd,
        stdout=open(os.devnull, "w"),
        stderr=STDOUT,
        shell=True,
    )


def main():
    text = "Video"
    print("Choose one: ")
    print("[cyan]1. Encode[/cyan]\n[cyan]2. Decode[/cyan]")
    op = int(input(">> "))

    if op == 1:
        print(f"[cyan]{text} path (with extension): [/cyan]")
        img = input(">> ")

        print("[cyan]Message to be hidden: [/cyan]")
        message = input(">> ")
        password = ""

        print(
            "[cyan]Password to encrypt (leave empty if you want no password): [/cyan]"
        )
        password = getpass.getpass(">> ")

        if password != "":
            print("[cyan]Re-enter Password: [/cyan]")
            confirm_password = getpass.getpass(">> ")
            if password != confirm_password:
                print("[red]Passwords don't match try again [/red]")
                return

        cmd = shlex.split(f"ffmpeg -i {img} -q:a 0 -map a sample.mp3")
        call(
            cmd,
            stdout=open(os.devnull, "w"),
            stderr=STDOUT,
            shell=True,
        )

        cmd = shlex.split(f"ffmpeg -i {img} -q:a 0 -map a sample.mp3 -y")
        call(
            cmd,
            stdout=open(os.devnull, "w"),
            stderr=STDOUT,
            shell=True,
        )

        FrameCapture(img, op, password, message)

        cmd = shlex.split(
            "ffmpeg -i output.mov -i output.mov -i sample.mp3 -codec copy final.mov -y"
        )
        call(
            cmd,
            stdout=open(os.devnull, "w"),
            stderr=STDOUT,
            shell=True,
        )
        os.remove("output.mov")
        os.remove("sample.mp3")

    elif op == 2:
        print(f"[cyan]{text} path (with extension):[/cyan] ")
        img = input(">>")

        print("[cyan]Enter password (leave empty if no password):[/cyan] ")
        password = getpass.getpass(">>")
        FrameCapture(img, op, password)


# To remove Credit in starting commnet this function only.
def print_credits():
    table = Table(show_header=True)
    table.add_column("Author", style="yellow")
    table.add_column("Contact", style="yellow")
    table.add_row("Aryan Bisht", "aryanbisht9458@gmail.com ")
    console.print(table)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    cprint(figlet_format("STEGANO", font="starwars"), "yellow", attrs=["bold"])
    print_credits()
    print()
    print(
        "[bold]VIDEOHIDE[/bold] allows you to hide texts inside an video. You can also protect these texts with a password using AES-256."
    )
    print()
    main()

# -----------------------
