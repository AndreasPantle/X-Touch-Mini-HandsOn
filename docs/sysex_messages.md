# SysEx Messages

## Traffic between editor and device

### `01_plugin.pcapng`

[01_plugin.pcapng](../usbtraffic/01_plugin.pcapng) -> This is a capturing during connecting the X-Touch Mini with opened X-Touch Editor.

#### Reading device informations

Starting with this file an packet no. 45:

```bash
# hexdump of the sysex message from the editor to the device:
# f0 40 41 42 51 00 00 00 00 00 00 00 00 f7
$ amidi -p hw:1 --send-hex="f0404142510000000000000000f7" --dump
F0 40 41 42 51 00 0A 00 00 01 08 00 00 F7
14 bytes read
```

Now we can read the version 1.08 of the device. Which is exactly what the editor also did. Switching to layer b using the editor and redo the same message:

```bash
$ amidi -p hw:1 --send-hex="f0404142510000000000000000f7" --dump
F0 40 41 42 51 00 0A 00 00 01 08 01 00 F7
14 bytes read
```

If we put the device in MC mode using the editor:

```bash
$ amidi -p hw:1 --send-hex="f0404142510000000000000000f7" --dump
F0 40 41 42 51 00 0A 01 00 01 08 01 00 F7
14 bytes read
```

Playing around with some settings in the editor leads me to:

```
+-------------+----+----+----+------------------+-----------+----------------+------------------+----+----------------+----------------+-------------------+----+------------+
|             |    |    |    |                  | 1         | 2              | 3                | 4  | 5              | 6              | 7                 | 8  |            |
+-------------+----+----+----+------------------+-----------+----------------+------------------+----+----------------+----------------+-------------------+----+------------+
| F0          | 40 | 41 | 42 | 51               | 0C        | 0A             | 00               | 00 | 01             | 08             | 00                | 00 | F7         |
+-------------+----+----+----+------------------+-----------+----------------+------------------+----+----------------+----------------+-------------------+----+------------+
| Sysex start |    |    |    | Command response | Device ID | Global channel | 00-Standard mode | ?  | Firmware major | Firmware minor | 00-Layer A active | ?  | Sysex stop |
+-------------+----+----+----+------------------+-----------+----------------+------------------+----+----------------+----------------+-------------------+----+------------+
|             |    |    |    |                  |           |                | 01-MC mode       |    |                |                | 01-Layer B active |    |            |
+-------------+----+----+----+------------------+-----------+----------------+------------------+----+----------------+----------------+-------------------+----+------------+
```

[cmd51_response.tgn](tables/cmd51_response.tgn)

I can not identify the **?** in the table. Maybe this is only for the alignment of the telegram.

Let's go on with the sysex messages...

#### Reading the device configuration

Go to packet no. 49. The editor needs the configuration for showing the user what the actual device setup is:

```bash
# hexdump of the sysex message from the editor to the device:
# f0 40 41 42 52 01 00 00 00 00 00 00 00 f7
$ amidi -p hw:1 --send-hex="f0404142520100000000000000f7" --dump
F0 50 51 52 52 01 02 07 08 0E 03 0C 0E 0F 02 0A 0A 00 09 00 7F 00 00 00 0A 00 01 00 7F 01 00 00 00 0A 00 02 00 7F 01 00 00 00 0A 00 03 00 7F 00 01 00 00 0A 00 04 00 00 7F 01 00 00 0A 00 05 00 00 7F 01 00 00 0A 00 00 06 00 7F 01 00 00 0A 00 00 07 00 7F 01 00 00 00 0A 00 08 00 7F 01 00 00 00 0A 01 00 00 7F 00 00 00 00 0A 01 01 00 7F 00 00 00 00 0A 01 02 00 00 7F 00 00 00 0A 01 03 00 00 7F 00 00 00 0A 01 00 04 00 7F 00 00 00 0A 00 01 05 00 7F 00 00 00 00 0A 01 06 00 7F 00 00 00 00 0A 01 07 00 7F 00 00 00 00 0A 01 08 00 7F 00 00 00 00 0A 01 09 00 00 7F 00 00 00 0A 01 0A 00 00 7F 00 00 00 0A 01 00 0B 00 7F 00 00 00 0A 00 01 0C 00 7F 00 00 00 00 0A 01 0D 00 7F 00 00 00 00 0A 01 0E 00 7F 00 00 00 00 0A 01 0F 00 7F 00 00 00 00 0A 01 10 00 00 7F 00 00 00 0A 01 11 00 00 7F 00 00 00 0A 01 00 12 00 7F 00 00 00 0A 00 01 13 00 7F 00 00 00 00 0A 01 14 00 7F 00 00 00 00 0A 01 15 00 7F 00 00 00 00 0A 01 16 00 7F 00 00 00 00 0A 01 17 00 00 7F 00 00 00 00 00 00 00 F7
321 bytes read
```

Let us try the command with 02 as parameter:

```bash
# hexdump of the sysex message from the editor to the device:
# f0 40 41 42 52 **02** 00 00 00 00 00 00 00 f7
$ amidi -p hw:1 --send-hex="f0404142520200000000000000f7" --dump
F0 50 51 52 52 02 02 07 08 0D 04 08 0B 0C 0B 05 0A 00 0A 00 7F 00 00 00 0A 00 0B 01 19 01 00 00 00 0A 00 0C 00 7F 02 00 00 00 0A 00 0D 00 7F 00 02 00 00 0A 00 0E 00 00 7F 02 00 00 0A 00 0F 00 00 7F 02 00 00 0A 00 00 10 00 7F 02 00 00 0A 00 00 11 00 7F 02 00 00 00 0A 00 12 01 03 03 00 00 00 0A 01 18 00 7F 00 00 00 00 0A 01 19 00 7F 00 00 00 00 0A 01 1A 00 00 7F 00 00 00 0A 01 1B 00 00 7F 00 00 00 0A 01 00 1C 00 7F 00 00 00 0A 00 01 1D 00 7F 00 00 00 00 0A 01 1E 00 7F 00 00 00 00 0A 01 1F 00 7F 00 00 00 00 0A 01 20 00 7F 00 00 00 00 0A 01 21 00 00 7F 00 00 00 0A 01 22 00 00 7F 00 00 00 0A 01 00 23 00 7F 00 00 00 0A 00 01 24 00 7F 00 00 00 00 0A 01 25 00 7F 00 00 00 00 0A 01 26 00 7F 00 00 00 00 0A 01 27 00 7F 00 00 00 00 0A 01 28 00 00 7F 00 00 00 0A 01 29 00 00 7F 00 00 00 0A 01 00 2A 00 7F 00 00 00 0A 00 01 2B 00 7F 00 00 00 00 0A 01 2C 00 7F 00 00 00 00 0A 01 2D 00 7F 00 00 00 00 0A 01 2E 00 7F 00 00 00 00 0A 01 2F 00 00 7F 01 00 00 00 00 00 00 F7
321 bytes read
```

Now we have the possibility to read the configuration of layer A and layer B. Therefore I add some SysEx files if you like to try it:

```bash
$ echo -ne "\xf0\x40\x41\x42\x52\x01\x00\x00\x00\x00\x00\x00\x00\xf7" > get_layer_a_config.syx
$ amidi -p hw:1 -s get_layer_a_config.syx --dump

$ echo -ne "\xf0\x40\x41\x42\x52\x02\x00\x00\x00\x00\x00\x00\x00\xf7" > get_layer_b_config.syx
$ amidi -p hw:1 -s get_layer_b_config.syx --dump
```

We have a look of the configuration later on. You can get the SysEx files here: [get_layer_a_config.syx](../sysex/get_layer_a_config.syx) and [get_layer_b_config.syx](../sysex/get_layer_b_config.syx).
