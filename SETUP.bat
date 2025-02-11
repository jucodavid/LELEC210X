@echo off
title SETUP

echo Passing thru usb to wsl...
usbipd list
set /p input="Enter busid: "
usbipd attach --wsl --busid %input%
