# X-Touch-Mini-HandsOn

![x-touch](docs/img/xtouchmini.png)

I was searching for a control device for an embedded application. The loss of time for developing and building by myself seems to be big. So meeting the Behringer X-Touch Mini seems to be a lucky coincidence. The device is cheap enough and it offers a great functionality for using it at my application (and of course so much other stuff). Please note that I have no music background or studio experience.

If you like to add some information to this repository, please feel free to do that.

## Open points

Actually I tried some stuff with the sniffed sysex messages. For a complete reconfiguration as it is working with the Windows software, I need a checksum and some stuff for getting the data to the X-Touc Mini. **So if you are working on the same think and can help me with this matter, please contact me.** I was sniffing the reading and writing process with the Windows software. But no luck if I'm doing this with a script and the same sysex data, the X-Touch Mini is ignoring my configuration. Maybe there is an engineer from Behringer out there with the possibility to provide some informations about this stuff.

For now I decided to make this stuff public in hope there is someone who can give me some hints.

## Disadvantages

Yes there are...:

* Behringer is offering a Windows software for setting up the X-Touch Mini only. Actually I can not find a software for macOS or Linux.
* The support by Behringer feels to me to little. There is a documentation for the X-Touch Mini - Ok. So far it does not describe the interesting stuff for that device. In addition to that, there is only a forum. So everything you can read here is the result of doing testings, sniffing and try to reverse engineer.

## What are my use cases?

* I'm a Linux and a macOS user. My first goals are to load / save the settings from the device. In addition to that it would be nice to reconfigure the device.
* I have the need to change the device settings dynamically. Which means I need to load the settings in dependency of my application state. I have no Windows on my embedded device. Thinking of using an Rasperry Pi and you like to change the configuration. Actually I have not found a way for doing this.
* You can do much more with if you no some background stuff.

## Please note!

All this stuff is not officially by Behringer. I do some testings and tried to reverse engineer. So please be careful and check the [License](LICENSE.md) file. You can use this informations by your own responsibility.

# Documentation

* [USB traffic analyzing](docs/usb_traffic.md)
