An SOCD cleaner (snap tap) script for Python as Autohotkey wasn't reliable enough.    
It prevents the opposing WASD keys from being simultanously pressed by only sending the most recent one.    
The script uses the Python port of Interception, a low level input device driver, and is as a side effect more difficult to detect for applications.

Setup instructions:    
> pip install interception-python==1.5.2    
pip install pywin32    
install driver as instructed -> https://github.com/oblitum/Interception    
reboot    

Reference:
https://github.com/kennyhml/pyinterception
