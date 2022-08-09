# USB traffic

## Sniffing with Wireshark and USBPcap

For having the X-Touch Editor and Wireshark on one machine, I decided to use a Windows 10 virtual machine. Binding the X-Touch Mini directly to the vitual machine for getting the hardware connection. Actually I thought that Behringer is using a manufacturer specific protocol for the communication with the X-Touch Mini. So I was using Wireshark with the USB Pcap for sniffing the traffic. I opened the X-Touch Editor for the device communication parallel. I was a little bit surprised to see that the communication itself was only some Midi SysEx messages!?

![usb_traffic_sysex](img/usb_traffic_sysex.png)

**So it seems that the X-Touch Editor itself is putting the commands for the X-Touch Mini in SysEx messages.**

I created a folder on this repository for storing the captured traffic here `usbtraffic/`.

## `01_plugin.pcapng`

[usbtraffic/01_plugin.pcapng](usbtraffic/01_plugin.pcapng) -> This is a capturing during connecting the X-Touch Mini with opened X-Touch Editor.

Starting with this file an packet no. 45:

```bash
# hexdump of the sysex message from the editor to the device:
# f0 40 41 42 51 00 00 00 00 00 00 00 00 f7
$ amidi -p hw:1 --send-hex="f0404142510000000000000000f7" --dump
F0 40 41 42 51 00 0A 00 00 01 08 00 00 F7
14 bytes read
```

Now we can read the version 1.08 of the device. Which is exactly what the editor also did. Switching to layer b and redo the same message:

```bash
$ amidi -p hw:1 --send-hex="f0404142510000000000000000f7" --dump
F0 40 41 42 51 00 0A 00 00 01 08 01 00 F7
14 bytes read
```

If we put the device in MC mode:

```bash
$ amidi -p hw:1 --send-hex="f0404142510000000000000000f7" --dump
F0 40 41 42 51 00 0A 01 00 01 08 01 00 F7
14 bytes read
```

Playing around with some settings in the editor leads me to:

```
| F0          | 40 | 41 | 42 | 51               | 0C        | 0A             | 00               | 00 | 01             | 08             | 00                | 00 | F7         |
|-------------|----|----|----|------------------|-----------|----------------|------------------|----|----------------|----------------|-------------------|----|------------|
| Sysex start |    |    |    | Command response | Device ID | Global channel | 00-Standard mode | ?  | Firmware major | Firmware minor | 00-Layer A active | ?  | Sysex stop |
|             |    |    |    |                  |           |                | 01-MC mode       |    |                |                | 01-Layer B active |    |            |
```

I can not identify the **?** in the table. Maybe this is only for the alignment of the telegram.
