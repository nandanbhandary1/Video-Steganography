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


# ========== ADDED FUNCTION ==========
def get_script_dir():
    """Returns the directory where the script is located"""
    return os.path.dirname(os.path.abspath(__file__))


# ====================================


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


def FrameCapture(path, op, password, message=""):
    createTmp()
    vidObj = cv2.VideoCapture(path)
    count = 0
    total_frame = countFrames(path)
    split_string_list = split_string(message)
    position = 0
    outputMessage = ""

    while count < total_frame:
        success, image = vidObj.read()
        if not success:
            break

        if op == 1:
            frame_path = os.path.join(temp_folder, f"frame{count}.png")
            cv2.imwrite(frame_path, image)

            if position < len(split_string_list):
                print("Input in image working :- ", split_string_list[position])
                Stegno_image.main(
                    op,
                    password=password,
                    message=split_string_list[position],
                    img_path=frame_path,
                )
                position += 1
                os.remove(frame_path)

        if op == 2:
            frame_path = os.path.join(temp_folder, f"frame{count}.png")
            str = Stegno_image.main(
                op,
                password=password,
                img_path=frame_path,
            )
            if str == "Invalid data!":
                break
            outputMessage = outputMessage + str

        count += 1

    if op == 1:
        print("[cyan]Please wait....[/cyan]")
        makeVideoFromFrame()

    if op == 2:
        print("[green]DECRYPTED MESSAGE IS :-\n[bold]%s[/bold][/green]" % outputMessage)


def makeVideoFromFrame():
    script_dir = get_script_dir()
    output_path = os.path.join(script_dir, "final.mp4")
    audio_path = os.path.join(script_dir, "sample.m4a")

    # Debug: Show frame folder contents
    print("\n[DEBUG] Frame folder contents:", os.listdir("frame_folder"))

    # Verify we have frames to process
    frames = [
        f
        for f in os.listdir("frame_folder")
        if f.startswith("frame") and f.endswith(".png")
    ]
    if not frames:
        print("[ERROR] No frames found in frame_folder!")
        return

    # Rename encoded frames
    for img in os.listdir("frame_folder"):
        if "-enc" in img and img.endswith(".png"):
            new_name = img.replace("-enc", "")
            os.rename(
                os.path.join("frame_folder", img),
                os.path.join("frame_folder", new_name),
            )

    # Get frame sequence in correct order
    frames = sorted(
        [
            f
            for f in os.listdir("frame_folder")
            if f.startswith("frame") and f.endswith(".png")
        ],
        key=lambda x: int(x[5:-4]),
    )

    # Create video from frames
    video_temp_path = os.path.join(script_dir, "temp_video.mp4")
    cmd = (
        f"ffmpeg -framerate 30 -i frame_folder/frame%d.png "
        f"-c:v libx264 -pix_fmt yuv420p -profile:v main -crf 18 "
        f'"{video_temp_path}" -y'
    )
    print("\n[DEBUG] Creating video with command:", cmd)

    try:
        return_code = call(
            shlex.split(cmd), stdout=open(os.devnull, "w"), stderr=STDOUT
        )
        if return_code != 0:
            print(f"[ERROR] FFmpeg video creation failed with code {return_code}")
            return
    except Exception as e:
        print(f"[ERROR] Video creation failed: {str(e)}")
        return

    # Merge audio if available
    if os.path.exists(audio_path):
        print("\n[DEBUG] Merging audio track...")
        cmd = (
            f'ffmpeg -i "{video_temp_path}" -i "{audio_path}" '
            f"-c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "
            f'-movflags +faststart "{output_path}" -y'
        )
    else:
        print("\n[DEBUG] No audio track found, creating video without audio")
        cmd = f'ffmpeg -i "{video_temp_path}" -c:v copy "{output_path}" -y'

    print("[DEBUG] Final merge command:", cmd)
    try:
        return_code = call(
            shlex.split(cmd), stdout=open(os.devnull, "w"), stderr=STDOUT
        )
        if return_code != 0:
            print(f"[ERROR] FFmpeg merge failed with code {return_code}")
            return
    except Exception as e:
        print(f"[ERROR] Final merge failed: {str(e)}")
        return

    # Verify output
    if os.path.exists(output_path):
        print(f"\n[SUCCESS] Created final video at: {output_path}")
        print(f"File size: {os.path.getsize(output_path)} bytes")
    else:
        print("\n[ERROR] Final video was not created!")

    # Cleanup
    for f in [video_temp_path, audio_path]:
        if os.path.exists(f):
            os.remove(f)


def main():
    # ========== ADDED WORKING DIRECTORY FIX ==========
    os.chdir(get_script_dir())
    print(f"[DEBUG] Working directory set to: {os.getcwd()}")
    # ================================================

    text = "Video"
    print("Choose one: ")
    print("[cyan]1. Encode[/cyan]\n[cyan]2. Decode[/cyan]")
    op = int(input(">> "))

    # Only clean up files if we're encoding
    if op == 1:
        for f in ["sample.mp3", "output.mov", "final.mov"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

    if op == 1:
        print(f"[cyan]{text} path (with extension): [/cyan]")
        img = input(">> ").strip()

        if not os.path.exists(img):
            print(f"[red]Error: File not found at {img}[/red]")
            return
        if not os.path.isfile(img):
            print("[red]Error: Path is not a file![/red]")
            return

        print("[cyan]Message to be hidden: [/cyan]")
        message = input(">> ")
        password = ""

        print("[cyan]Password to encrypt: [/cyan]")
        password = getpass.getpass(">> ")

        if password:
            print("[cyan]Re-enter Password: [/cyan]")
            confirm_password = getpass.getpass(">> ")
            if password != confirm_password:
                print("[red]Passwords don't match![/red]")
                return

        try:
            # Replace the audio extraction with:
            audio_path = os.path.join(get_script_dir(), "sample.m4a")
            print(f"\n[DEBUG] Attempting to extract audio to: {audio_path}")

            # First try to copy the audio stream directly
            cmd = f'ffmpeg -i "{img}" -c:a copy -map a "{audio_path}" -y'
            if call(shlex.split(cmd), stdout=open(os.devnull, "w"), stderr=STDOUT) != 0:
                print("[WARNING] Direct audio copy failed, trying to convert...")
                # If direct copy fails, try converting to AAC
                cmd = f'ffmpeg -i "{img}" -c:a aac -b:a 192k -map a "{audio_path}" -y'
                if (
                    call(shlex.split(cmd), stdout=open(os.devnull, "w"), stderr=STDOUT)
                    != 0
                ):
                    print("[WARNING] Audio extraction failed, proceeding without audio")
                    if os.path.exists(audio_path):
                        os.remove(audio_path)

            # Process frames
            FrameCapture(img, op, password, message)

            # Final verification
            final_path = os.path.join(get_script_dir(), "final.mp4")
            if os.path.exists(final_path):
                print(f"\n[SUCCESS] final.mov created at: {final_path}")
                print(f"File size: {os.path.getsize(final_path)} bytes")
            else:
                print("\n[ERROR] final.mov was not created!")
                print("Current directory contents:", os.listdir())

        except Exception as e:
            print(f"\n[FATAL ERROR] {e}")
            print("Current directory contents:", os.listdir())

    elif op == 2:
        print(f"[cyan]{text} path (with extension): [/cyan]")
        img = input(">> ").strip()

        if not os.path.exists(img):
            print(f"[red]Error: File not found at {img}[/red]")
            return
        if not os.path.isfile(img):
            print("[red]Error: Path is not a file![/red]")
            return

        print("[cyan]Password to decrypt: [/cyan]")
        password = getpass.getpass(">> ")

        FrameCapture(img, op, password)


def print_credits():
    table = Table(show_header=True)
    table.add_column("Author", style="yellow")
    table.add_column("Contact", style="yellow")
    table.add_row("Nandan Bhandary", "nandanbhandary24@gmail.com")
    console.print(table)


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    cprint(figlet_format("STEGANO", font="starwars"), "yellow", attrs=["bold"])
    print_credits()
    print()
    print("[bold]VIDEOHIDE[/bold] allows you to hide texts inside an video.")
    print()
    main()
