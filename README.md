A SOCD cleaner (snap tap) script for Python as Autohotkey wasn't reliable enough.    
It prevents the opposing WASD keys from being simultanously pressed by only sending the most recent one.    
The script uses the [Python port of Interception](https://github.com/kennyhml/pyinterception), a low level input device driver, and is as a side effect more difficult to detect for applications.

The socd_cleaner.py is just the SOCD cleaning script, whereas the socd_cleaner_tray.pyw also includes a tray icon with context menu for toggling of the script.

Setup instructions:    
> pip install interception-python==1.6.2    
pip install pywin32    
install driver as instructed -> https://github.com/oblitum/Interception    
reboot
