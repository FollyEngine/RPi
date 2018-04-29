# NFC event to mqtt event server

Simple Python service that listens to the rfid reader, and when something happens, relays that rfid tag's id to the mqtt

## setup and run

Either use the Docker container, see the Makefile, 

or if running locally, use the `local.sh` script

then to start the service on reboot, use `contrab -e` and add a line like

```
@reboot cd rpi; ./local.sh 10.10.11.2 > local.log 2&>1
```

>> **NOTE:** this requires the NFC reader to be connected before booting.

## some dev links

driver and test tool install:

- https://oneguyoneblog.com/2016/11/02/acr122u-nfc-usb-reader-linux-mint/
- https://www.acs.com.hk/en/driver/3/acr122u-usb-nfc-reader/:w
- https://github.com/acshk/acsccid
- https://github.com/AdamLaurie/RFIDIOt
- http://www.instructables.com/id/USB-RFID-Python-Pub-Sub-MQTT/
- https://github.com/hohlerde/go-nxprd
- https://golanglibs.com/top?q=nfc


## tools
- run `pcsc_scan` to see nfc tags

`sudo apt-get install libnfc-bin libnfc-dev libnfc-examples libnfc5 libnfc-pn53x-examples libmrtd0 mrtdreader ruby-nfc`
- http://nfc-tools.org/index.php?title=Libnfc#POSIX_systems

## general rPI things
* setup WiFi by setting the `ssid` and `psk` in `/etc/wpa_supplicant/wpa_supplicant.conf`:
  ```
    network={
        ssid="AUSU"
        psk="Really, I need to know this"
    }
  ```
* reset the rPI keyboard layout - run `sudo raspi-config`
