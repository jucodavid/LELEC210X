# UTILS

## gnu radio
```bash
cd LELEC210X/telecom/hands_on_measurements/gr-fsk
wsl
gnuradio-companion
```

### gnu radio modifications
```bash
cd LELEC210X/telecom/hands_on_measurements/gr-fsk/build
wsl
sudo make install
```
Eventually, when everything brakes, delete de build directory and reconstruct it.
```bash
mkdir build
cd build
cmake ..
sudo make install
sudo ldconfig
```
And replace the .grc file in apps by clean ones from the teching staff github.

> You should then reconfigure it. As for now, `carrier_freq = 862e6` and `fdev = data_rate/2`.

## usbipd
```bash
usbipd list
usbipd attach --wsl --busid
```

## leaderboard
```bash
cd LELE210X/leaderboard
rye run leaderboard serve --open
```
On local:

**basic display :** http://localhost:5000/lelec210x/leaderboard

**admin inputs :** http://localhost:5000/lelec210x/leaderboard/doc/

> **Teaching Assistants key :** RnWjdc8E8ZTCCmS_FyXHfuI5ieH43uKSCUDdig4Y

> **Group B key :** X6wLG0KYZwh0Op0BIiq0GdmEy4x7Ot3BDlRyecx-

On web:

**basic display :** http://lelec210x.sipr.ucl.ac.be/lelec210x/leaderboard

**admin inputs :** http://lelec210x.sipr.ucl.ac.be/lelec210x/leaderboard/doc/

> **Group B key :** a5vIbTLb5gDwxC2VXEj2lLuv4UAGSPmKm-iyCJVQ

## marcel
```bash
rye run python mcu/hands_on_main_app/marcel.py
```
Edit on marcel.py the commented lines to switch from local server to live serve
