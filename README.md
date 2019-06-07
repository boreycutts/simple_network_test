# Simple Network Test
This script is used to run a continuous test on your home network and display/save the results. To run this test navigate to the repo directory and run `python3 network_test.py`. This script take two optional arguments:

`--address`: Sets the address used in the ping command in the test. Default = 8.8.8.8

`--threshold`: Sets the packet loss percentage threshold used to determine if the output should be saved to `[timestamp]__errors.log` Default = 0%

