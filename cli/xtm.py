#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import rich_click as click
import rtmidi
from rich.table import Table
from rich.console import Console
# Create a console instance for formatting the output against this
console = Console()
from utils import bytes_to_hex_str
from sysexdata import SYSEX_DEVICE_INFO, SYSEX_MODE_SWITCH, SYSEX_DEVICE_ID, SYSEX_GLOBAL_CH


"""
Constans for the context dictionary.
"""
VERBOSE_MODE = 'VERBOSE_MODE'
TIMEOUT = 'TIMEOUT'
RTMIDI_PORT_NO = 'RTMIDI_PORT_NO'
RTMIDI_MIDI_IN = 'RTMIDI_MIDI_IN'
RTMIDI_MIDI_OUT = 'RTMIDI_MIDI_OUT'


def xtm_cli_open_midi_port(rtmidi_in, rtmidi_out, port):
    """
    Open the given input and output Midi port.
    :param rtmidi_in: Midi in instance.
    :param rtmidi_out: Midi out instance.
    :param port: The port (as int) for opening.
    :return: A list of the opened rtmidi port.
    """
    return rtmidi_in.open_port(port=port), rtmidi_out.open_port(port=port)


@click.group()
@click.option(
    '-v', '--verbose',
    default=False,
    required=False,
    help='Prints some more information about the device communication.',
    is_flag=True
)
@click.option(
    '-p', '--port',
    default=0,
    required=False,
    help='The port of the connected X-Touch Mini.',
)
@click.option(
    '-t', '--timeout',
    default=2,
    required=False,
    help='The timeout in seconds for waiting for an answer of the device.',
)
@click.pass_context
def cli(ctx, verbose, port, timeout):
    """
    Behringer X-Touch Mini CLI.
    Some stuff for testing the SysEx messages.
    You can use --help at the top level and also for specific group subcommands.
    """

    # Storing dictionaries in click context
    ctx.ensure_object(dict)

    # Adding the debug flag
    if verbose:
        ctx.obj[VERBOSE_MODE] = True
    else:
        ctx.obj[VERBOSE_MODE] = False

    # Adding the timeout
    ctx.obj[TIMEOUT] = timeout

    # Adding the port number
    ctx.obj[RTMIDI_PORT_NO] = port

    # Creating Midi input/output instances
    ctx.obj[RTMIDI_MIDI_IN] = rtmidi.MidiIn()
    ctx.obj[RTMIDI_MIDI_OUT] = rtmidi.MidiOut()


@cli.command()
@click.pass_context
def ports(ctx):
    """
    List available Midi ports.
    """

    # List the Midi input ports
    ports_in = ctx.obj[RTMIDI_MIDI_IN].get_ports()
    ports_in_table = Table(title='Midi Input Ports')
    ports_in_table.add_column('Index', justify='left', style='')
    ports_in_table.add_column('Name', justify='left', style='')
    for port_in_index, port_in in enumerate(ports_in):
        ports_in_table.add_row('%i' % port_in_index, port_in)
    console.print(ports_in_table)

    # List the Midi output ports
    ports_out = ctx.obj[RTMIDI_MIDI_OUT].get_ports()
    ports_out_table = Table(title='Midi Output Ports')
    ports_out_table.add_column('Index', justify='left', style='')
    ports_out_table.add_column('Name', justify='left', style='')
    for port_out_index, port_out in enumerate(ports_out):
        ports_out_table.add_row('%i' % port_out_index, port_out)
    console.print(ports_out_table)


@cli.command()
@click.pass_context
def info(ctx):
    """
    Get the device information.
    """

    # Open the Midi ports
    try:
        port_midi_in, port_midi_out = xtm_cli_open_midi_port(
            rtmidi_in=ctx.obj[RTMIDI_MIDI_IN], rtmidi_out=ctx.obj[RTMIDI_MIDI_OUT], port=ctx.obj[RTMIDI_PORT_NO]
        )
        port_midi_in.ignore_types(sysex=False)
        sending_data = bytearray.fromhex(SYSEX_DEVICE_INFO)
        if ctx.obj[VERBOSE_MODE]:
            console.print(
                '[white]Sending: %s - %i bytes[/white]' % (bytes_to_hex_str(sending_data), len(sending_data)),
                highlight=False
            )
        timeout_start = time.time()
        port_midi_out.send_message(sending_data)
        while True:
            receiving_data = port_midi_in.get_message()
            timeout_actual = time.time()
            if (timeout_actual - timeout_start) > ctx.obj[TIMEOUT]:
                console.print('[bold][red]Timeout! -> No answering from device.[/red][/bold]')
                break
            if receiving_data is not None and isinstance(receiving_data, tuple):
                if ctx.obj[VERBOSE_MODE]:
                    console.print(
                        '[white]Reading: %s - %i bytes[/white]' % (bytes_to_hex_str(receiving_data[0]),
                                                                   len(receiving_data[0])),
                        highlight=False
                    )
                break
        info_table = Table(title='Device Information', show_header=False)
        info_table.add_row('Device ID:', '%i' % (receiving_data[0][5] + 1))
        if receiving_data[0][6] == 0x12:
            info_table.add_row('Global channel:', 'Off')
        else:
            info_table.add_row('Global channel:', '%i' % (receiving_data[0][6] + 1))
        if receiving_data[0][7] == 0x00:
            info_table.add_row('Mode:', 'Standard')
        elif receiving_data[0][7] == 0x01:
            info_table.add_row('Mode:', 'MC')
        info_table.add_row('Firmware:', '%i.%i' % (receiving_data[0][9], receiving_data[0][10]))
        if receiving_data[0][11] == 0x00:
            info_table.add_row('Layer:', 'A')
        elif receiving_data[0][11] == 0x01:
            info_table.add_row('Layer:', 'B')

        # Print the table
        console.print(info_table)
    except rtmidi.InvalidPortError:
        console.print(
            '[bold][red]InvalidPortError[/red][/bold] Port: %i is not a valid port!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except rtmidi.InvalidUseError:
        console.print(
            '[bold][red]InvalidUseError[/red][/bold] Port: %i is already open!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except TypeError:
        console.print(
            '[bold][red]TypeError[/red][/bold] The port is always a number starting from 0.'
        )


@cli.command()
@click.argument('mode', required=True, default=0)
@click.pass_context
def mode(ctx, mode):
    """
    Set the new mode.
    0 - Standard mode
    1 - MC mode
    """

    if not 0 <= mode <= 1:
        console.print('[bold][red]Unknown mode! Choose between 0 - Standard or 1 - MC.[/red][/bold]')
        return

    # Open the Midi ports
    try:
        port_midi_in, port_midi_out = xtm_cli_open_midi_port(
            rtmidi_in=ctx.obj[RTMIDI_MIDI_IN], rtmidi_out=ctx.obj[RTMIDI_MIDI_OUT], port=ctx.obj[RTMIDI_PORT_NO]
        )
        port_midi_in.ignore_types(sysex=False)
        sending_data = bytearray.fromhex((SYSEX_MODE_SWITCH % mode))
        if ctx.obj[VERBOSE_MODE]:
            console.print(
                '[white]Sending: %s - %i bytes[/white]' % (bytes_to_hex_str(sending_data), len(sending_data)),
                highlight=False
            )
        timeout_start = time.time()
        port_midi_out.send_message(sending_data)
        while True:
            receiving_data = port_midi_in.get_message()
            timeout_actual = time.time()
            if (timeout_actual - timeout_start) > ctx.obj[TIMEOUT]:
                console.print('[bold][red]Timeout! -> No answering from device.[/red][/bold]')
                break
            if receiving_data is not None and isinstance(receiving_data, tuple):
                if ctx.obj[VERBOSE_MODE]:
                    console.print(
                        '[white]Reading: %s - %i bytes[/white]' % (bytes_to_hex_str(receiving_data[0]),
                                                                   len(receiving_data[0])),
                        highlight=False
                    )
                break
            # TODO: Check the return value!
    except rtmidi.InvalidPortError:
        console.print(
            '[bold][red]InvalidPortError[/red][/bold] Port: %i is not a valid port!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except rtmidi.InvalidUseError:
        console.print(
            '[bold][red]InvalidUseError[/red][/bold] Port: %i is already open!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except TypeError:
        console.print(
            '[bold][red]TypeError[/red][/bold] The port is always a number starting from 0.'
        )


@cli.command()
@click.argument('devid', required=True, default=1)
@click.pass_context
def devid(ctx, devid):
    """
    Set the device id from 1 to 16.
    """

    if not 1 <= devid <= 16:
        console.print('[bold][red]Unknown device id! Choose between 1 to 16.[/red][/bold]')
        return

    # Open the Midi ports
    try:
        port_midi_in, port_midi_out = xtm_cli_open_midi_port(
            rtmidi_in=ctx.obj[RTMIDI_MIDI_IN], rtmidi_out=ctx.obj[RTMIDI_MIDI_OUT], port=ctx.obj[RTMIDI_PORT_NO]
        )
        port_midi_in.ignore_types(sysex=False)
        sending_data = bytearray.fromhex((SYSEX_DEVICE_ID % (devid - 1)))
        if ctx.obj[VERBOSE_MODE]:
            console.print(
                '[white]Sending: %s - %i bytes[/white]' % (bytes_to_hex_str(sending_data), len(sending_data)),
                highlight=False
            )
        timeout_start = time.time()
        port_midi_out.send_message(sending_data)
        while True:
            receiving_data = port_midi_in.get_message()
            timeout_actual = time.time()
            if (timeout_actual - timeout_start) > ctx.obj[TIMEOUT]:
                console.print('[bold][red]Timeout! -> No answering from device.[/red][/bold]')
                break
            if receiving_data is not None and isinstance(receiving_data, tuple):
                if ctx.obj[VERBOSE_MODE]:
                    console.print(
                        '[white]Reading: %s - %i bytes[/white]' % (bytes_to_hex_str(receiving_data[0]),
                                                                   len(receiving_data[0])),
                        highlight=False
                    )
                break
            # TODO: Check the return value!
    except rtmidi.InvalidPortError:
        console.print(
            '[bold][red]InvalidPortError[/red][/bold] Port: %i is not a valid port!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except rtmidi.InvalidUseError:
        console.print(
            '[bold][red]InvalidUseError[/red][/bold] Port: %i is already open!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except TypeError:
        console.print(
            '[bold][red]TypeError[/red][/bold] The port is always a number starting from 0.'
        )


@cli.command()
@click.argument('globch', required=True, default=1)
@click.pass_context
def globch(ctx, globch):
    """
    Set the global channel from 1 to 16 / or 0 for off.
    """

    if not 0 <= globch <= 16:
        console.print('[bold][red]Unknown global channel! Choose between 0-off or 1 to 16.[/red][/bold]')
        return

    # Open the Midi ports
    try:
        port_midi_in, port_midi_out = xtm_cli_open_midi_port(
            rtmidi_in=ctx.obj[RTMIDI_MIDI_IN], rtmidi_out=ctx.obj[RTMIDI_MIDI_OUT], port=ctx.obj[RTMIDI_PORT_NO]
        )
        port_midi_in.ignore_types(sysex=False)
        if globch == 0:
            sending_data = bytearray.fromhex((SYSEX_GLOBAL_CH % 0x12))
        else:
            sending_data = bytearray.fromhex((SYSEX_GLOBAL_CH % (globch - 1)))
        if ctx.obj[VERBOSE_MODE]:
            console.print(
                '[white]Sending: %s - %i bytes[/white]' % (bytes_to_hex_str(sending_data), len(sending_data)),
                highlight=False
            )
        timeout_start = time.time()
        port_midi_out.send_message(sending_data)
        while True:
            receiving_data = port_midi_in.get_message()
            timeout_actual = time.time()
            if (timeout_actual - timeout_start) > ctx.obj[TIMEOUT]:
                console.print('[bold][red]Timeout! -> No answering from device.[/red][/bold]')
                break
            if receiving_data is not None and isinstance(receiving_data, tuple):
                if ctx.obj[VERBOSE_MODE]:
                    console.print(
                        '[white]Reading: %s - %i bytes[/white]' % (bytes_to_hex_str(receiving_data[0]),
                                                                   len(receiving_data[0])),
                        highlight=False
                    )
                break
            # TODO: Check the return value!
    except rtmidi.InvalidPortError:
        console.print(
            '[bold][red]InvalidPortError[/red][/bold] Port: %i is not a valid port!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except rtmidi.InvalidUseError:
        console.print(
            '[bold][red]InvalidUseError[/red][/bold] Port: %i is already open!' % ctx.obj['RTMIDI_PORT_NO']
        )
    except TypeError:
        console.print(
            '[bold][red]TypeError[/red][/bold] The port is always a number starting from 0.'
        )


@cli.result_callback()
@click.pass_context
def cli_result(ctx, result, **kwargs):
    """
    This is the end. Here we put everything for cleaning. These are the last lines of code.
    """

    # Closing the opened ports
    if ctx.obj[RTMIDI_MIDI_IN].is_port_open():
        ctx.obj[RTMIDI_MIDI_IN].close_port()
        del(ctx.obj[RTMIDI_MIDI_IN])
    if ctx.obj[RTMIDI_MIDI_OUT].is_port_open():
        ctx.obj[RTMIDI_MIDI_OUT].close_port()
        del (ctx.obj[RTMIDI_MIDI_OUT])


def main():
    # Starting the command line interface
    cli()


if __name__ == '__main__':
    main()
