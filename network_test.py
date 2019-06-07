import subprocess
from subprocess import check_output
import datetime
import time
import signal
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as md

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--address", nargs="?", const="8.8.8.8",
                    help="Sets the ip address or domain name to ping. Default value is \"8.8.8.8\"")
parser.add_argument("-t", "--threshold", nargs="?", const="0", type=int,
                    help="Sets a packet loss threshold for saving errors to log. Default value is \"0%%\"")


args = parser.parse_args()

# Address used in the ping command
if args.address:
    address = args.address
else:
    address = "8.8.8.8"

# Packet loss threshold. If the packet loss percentage goes above this number
# the output of the command will be logged to the error.log file
if args.threshold:
    threshold = args.threshold
else:
    threshold = 0

start_time = time.time()
initial_timestamp = '{:%Y-%m-%d_%H-%M-%S}'.format(datetime.datetime.now())

# Sets what happens when the infinite loop is interrupted with a "ctrl+C"
# command
def signal_handler(signal, frame):
    print("\n Done :D \n")

    # Math for test execution duration
    duration = time.time() - start_time
    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d >= 1:
        duration_metric = "Test Duration: %d days | %d hours | %d minutes | %d seconds" % (d, h, m, s)
    elif d < 1 and h >= 1:
        duration_metric = "Test Duration: %d hours | %d minutes | %d seconds" % (h, m, s)
    elif d < 1 and h < 1 and m >= 1:
        duration_metric = "Test Duration: %d minutes | %d seconds" % (m, s)
    else:
        duration_metric = "Test Duration : %d seconds" % (s)

    # This will only print test metrics if the ping command is ran at least once
    # (otherwise count would equal zero and you would get divide by zero errors)
    if count > 0:
        packet_loss_metric =  "Average Packet Loss Percentage: %0.2f%%" % (packet_loss/count)
        response_time_metric =  "Average Response Time: %0.2fms" % (average_response/count)
        metrics = duration_metric + "\n" + packet_loss_metric + "\n" + response_time_metric + "\n"
        print(metrics)
        with open(initial_timestamp + "__raw.log", "a") as myfile:
            myfile.write(metrics)
        print("Instances of packet loss or no connection saved to \"" + initial_timestamp + "__errors.log\"")
        print("All output saved to \"" + initial_timestamp + "__raw.log\" \n")
        
        plt.plot(timestamps, minimum, "r-", label="Minimum")
        plt.plot(timestamps, maximum, "o-", label="Maximum")
        plt.plot(timestamps, average, "y-", label="Average")
        plt.legend(loc='best')
        plt.gca().xaxis.set_major_formatter(md.DateFormatter("%Y-%m-%d %H:%M:%S"))
        plt.xticks( rotation=25 )
        plt.show()

    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

count = 0
packet_loss = 0
average_response = 0
minimum = []
maximum = []
average = []
timestamps = []

while True:
    command = "ping -n 5 -w 20 " + address

    # Runs the ping command which pings the specified ip address 5 times and times
    # out completely after 20 seconds
    #proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    result = 0

    # Saves the output and errors of the ping command
    try:
        out = check_output(["ping", "-n", "5", "-w", "20", address], \
            stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as err:
        result = err.returncode

    
    timestamp = datetime.datetime.now()
    timestamps.append(timestamp)
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(timestamp)
    
    #timestamps.append(time.mktime(time.localtime()))
    #timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

    # This parses the output of the ping command for the packet loss percentage to
    # be factored into the average at the end of the test
    try:
        packet_loss +=  float(out.split("%",1)[0].split(" ")[len(out.split("%",1)[0].split(" ")) - 1])
    except:
        # Do nothing
        pass

    # This parses the output of the ping command for the average response time to
    # be factored into the average at the end of the test
    try:
        average_response += float(out.split("max",1)[1].split("=",1)[1].split("/")[1])
    except:
        # Do nothing
        pass

    count += 1

    minimum.append(int(out.split("m")[len(out.split("m")) - 6].split(" ")[len(out.split("m")[len(out.split("m")) - 6].split(" ")) - 1]))
    maximum.append(int(out.split("m")[len(out.split("m")) - 3].split(" ")[len(out.split("m")[len(out.split("m")) - 3].split(" ")) - 1]))
    average.append(int(out.split("m")[len(out.split("m")) - 2].split(" ")[len(out.split("m")[len(out.split("m")) - 2].split(" ")) - 1]))

    print('--[ ' + timestamp + ' ]----------------------------------------')
    print(out)

    with open(initial_timestamp + "__raw.log", "a") as myfile:
        myfile.write('--[ ' + timestamp + ' ]----------------------------------------')
        myfile.write(out + "\n")
    if result != 0 or float(out.split("%",1)[0].split(" ")[len(out.split("%",1)[0].split(" ")) - 1].split("(")[1]) > threshold:
        with open(initial_timestamp + "__errors.log", "a") as myfile:
            myfile.write('--[ ' + timestamp + ' ]----------------------------------------')
            myfile.write(out + "\n")