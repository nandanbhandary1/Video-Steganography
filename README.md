# Video-steganography

This my final year project. If you want, you can it and modifiy it. 
In this project a message is first encrypted using SHA256 and AES256, then encoded in the video.
You need to run the python script on both sender and reciever to encode and decode the message.
I have used LSB algorithm in this.

I am also uploading documentation(report) with latex zip and presentation for this project. If you want can edit it easily in overleaf.
Thank me later.!!

Example of my project :- 

![encode]([Screenshot 2025-04-11 230140](https://github.com/user-attachments/assets/683537ed-d410-441b-9d47-43a299b1651c))



![decode]([Screenshot 2025-04-11 230424](https://github.com/user-attachments/assets/3f09beea-3e12-4afc-aa71-566e7cf13abc))


If there is some error like :- "The system cannot not find the file specified output.mov".
Then make sure first to install all library which are required by program (specially this error raised when you didn't install ffmepg).
And If you are sure all libraries are install but still error is coming then, add path of ffmepg to environment variable.

How to add path to enviroment variable of ffmepg : - https://www.wikihow.com/Install-FFmpeg-on-Windows
