import subprocess

def call_blc(url):
    command = [rf"C:\Users\mahen\AppData\Roaming\npm\blc.cmd", url, "-ro"]

    process = subprocess.Popen(
        command,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
        text = True,
        shell = True
    )



    for line in process.stdout:
        print(line)
    process.wait()
    

call_blc("https://lighthousetradepartners.com")

