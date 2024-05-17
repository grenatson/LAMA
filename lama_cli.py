import cmd2
from cmd2 import Bg, Fg, ansi
import argparse

import serial
from pynput import keyboard

import ephem
import catalogue

class LAMA_CLI(cmd2.Cmd):
    
    def on_press(self, key):
        message = None

        if key == keyboard.Key.enter:
            self.pico_connection.write(b'bind\n')
            self.me.date = ephem.now()
            self.target.compute(self.me)
            az = f'{self.target.az / ephem.degree}\n'.encode()
            alt = f'{self.target.alt / ephem.degree}\n'.encode()
            self.pico_connection.write(az)
            self.pico_connection.write(alt)
            return False

        if key == keyboard.Key.esc: message = b'break\n'

        if key == keyboard.Key.space: message = b'led_on\n'
        if key == keyboard.Key.shift_l or key == keyboard.Key.shift_r: 
            message = b'fast_on\n'
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            message = b'slow_on\n'

        if key == keyboard.Key.left: message = b'start_left\n'
        if key == keyboard.Key.right: message = b'start_right\n'
        if key == keyboard.Key.up: message = b'start_up\n'
        if key == keyboard.Key.down: message = b'start_down\n'

        if message: self.pico_connection.write(message)

        #self.poutput(ansi.clear_line(), end='')
        #self.poutput('Laser is under control...', end='')

    def on_release(self, key):
        message = None

        if key == keyboard.Key.space: message = b'led_off\n'
        if key == keyboard.Key.shift_l or key == keyboard.Key.shift_r: 
            message = b'fast_off\n'
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            message = b'slow_off\n'

        if key == keyboard.Key.left: message = b'stop_left\n'
        if key == keyboard.Key.right: message = b'stop_right\n'
        if key == keyboard.Key.up: message = b'stop_up\n'
        if key == keyboard.Key.down: message = b'stop_down\n'

        if message: self.pico_connection.write(message)

        if key == keyboard.Key.esc: return False

        #self.poutput(ansi.clear_line(), end='')
        #self.poutput('Laser is under control...', end='')

    def __init__(self):
        super().__init__()
        self.register_postloop_hook(self.do_disconnect)

        to_hide = ['alias','edit', 'macro', 'run_pyscript', 'run_script',
                  'shell', 'shortcuts']
        for cmd in to_hide: self.hidden_commands.append(cmd)

        self.prompt = 'LAMA> '
        self.allow_style = ansi.AllowStyle.TERMINAL
        self.poutput('Welcome to L.A.M.A. CLI!')

        self.target = None
        self.me = ephem.Observer()
        self.me.epoch = ephem.now()

        # MIPT stadium coordinates
        self.me.lat = '55.927762'
        self.me.lon = '37.524273'
        self.me.elevation = 195

        self.pico_connection = None
        self.binded = False

        self.poutput('Run "connect" to set up RPi Pico connection')
        self.poutput('Enter your location with "locate" command')
        self.poutput('Run "bind" to bind the mount to sky coordinates')
        self.poutput('Run "target" to set and lock on target object')

    def set_observer(self):
        self.me.lat = self.read_input('latitude: ')
        self.me.lon = self.read_input('longitude: ')
        self.me.elevation = int(self.read_input('elevation: '))
        self.me.pressure = int(self.read_input('pressure: '))
        self.me.temperature = int(self.read_input('temperature: '))
        # implement reading temperature from pico sensor

    def do_locate(self, args):
        """set observer's location"""
        self.set_observer()

    def do_info(self, args):
        """show observer and target info"""
        my_lat = '---' if not self.me.lat else str(self.me.lat)
        my_lon = '---' if not self.me.lon else str(self.me.lon)
        my_ele = '---' if not self.me.elevation else f'{self.me.elevation:.0f}'
        my_pres = '---' if not self.me.pressure else f'{self.me.pressure:.0f}'
        my_temp = '---' if not self.me.temperature else f'{self.me.temperature:.0f}'

        targetFlag = True if self.target else False
        if targetFlag:
            self.me.date = ephem.now()
            self.target.compute(self.me)

        name = '---' if not targetFlag else self.target.name.split('|')[0]
        ta_ra  = '---' if not targetFlag else str(self.target.ra)
        ta_dec = '---' if not targetFlag else str(self.target.dec)
        ta_az  = '---' if not targetFlag else str(self.target.az)
        ta_alt = '---' if not targetFlag else str(self.target.alt)

        header = 'Data for ' + str(ephem.localtime(self.me.date))

        info = f'====================================================\n'+\
               f'> {header:^48s} <\n' +\
               f'== Your current position ==|== Target information ==\n'+\
               f'latitude: {my_lat:>16s} | name: {name:>17s}\n'+\
               f'longitude: {my_lon:>15s} | RA: {ta_ra:>19s}\n'+\
               f'elevation: {my_ele:>15s} | DEC: {ta_dec:>18s}\n'+\
               f'pressure: {my_pres:>16s} | AZ: {ta_az:>19s}\n'+\
               f'temperature: {my_temp:>13s} | ALT: {ta_alt:>18s}\n'+\
               f'===================================================='

        self.poutput(info)

    def do_connect(self, args):
        """connect to RPi Pico"""
        self.poutput('Establishing connection with RPi Pico...')

        port = '/dev/ttyACM0'
        baudrate = 115200
        self.pico_connection = serial.Serial(port, baudrate)

        self.poutput('Connected successfully!')

    def do_disconnect(self) -> None:
        """disconnect from RPi Pico"""
        if self.pico_connection: self.pico_connection.close()

    def set_target(self, *target_name):
        if target_name[0] == '':
            name = self.read_input("Enter the target: ")
        else: name = " ".join(*target_name) 
        
        self.target = catalogue.get_target(name)
        name = ansi.style(name, fg=Fg["MAGENTA"], bold=True)
        if self.target:
            self.poutput(name + " has been set as a target!")
            return True
        else:
            self.poutput(name + " cannot be found!")
            return False

    target_parser = cmd2.Cmd2ArgumentParser()
    target_parser.add_argument('object', type=str, nargs='*', default='',
                                   help='name of the target object')
    target_parser.add_argument('-l', '--list', action='store_true',
                                   help='list available catalogues')
    @cmd2.with_argparser(target_parser)
    def do_target(self, args):
        """set object as a target"""
        if args.list:
            catalogue.list_catalogues()
            return

        if not self.set_target(args.object): return False

    bind_parser = cmd2.Cmd2ArgumentParser()
    bind_parser.add_argument('object', type=str, nargs='*', default='',
                                   help='name of the binding object')
    @cmd2.with_argparser(bind_parser)
    def do_bind(self, args):
        """bind mount to the sky"""
        if not self.pico_connection:
            self.poutput('Connect using "connect"!')
            return False
        if not self.set_target(args.object): return False

        name = self.target.name.split('|')[0]
        name = ansi.style(name, fg=Fg['MAGENTA'], bold=True)
        self.poutput(f'Point laser to {name} using arrow keys\n\
- Hold <SHIFT> for higher speed\n\
- Hold <CTRL> for precise motion\n\
- Press <ENTER> when done\n\
- Press <ESC> to exit binding')

        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release,
                suppress=True) as listener:
            listener.join()

        self.binded = True

    def do_goto(self, args):
        """point laser to target"""
        if not self.binded:
            self.poutput('Bind the mount using "bind"!')
        if not self.target: 
            self.poutput('Set target first!')
            return False

        self.me.date = ephem.now()
        self.target.compute(self.me)
        if self.target.alt < 0:
            self.poutput('Target is under the horizon!')
            return False

        self.pico_connection.write(b'goto\n')
        az = f'{self.target.az / ephem.degree}\n'.encode()
        alt = f'{self.target.alt / ephem.degree}\n'.encode()
        self.pico_connection.write(az)
        self.pico_connection.write(alt)

if __name__ == '__main__':
    import sys
    LAMA_APP = LAMA_CLI()
    sys.exit(LAMA_APP.cmdloop())

