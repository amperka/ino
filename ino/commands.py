# -*- coding: utf-8; -*-

class Command(object):
    name = None

    def __init__(self, env):
        self.env = env

    def setup_arg_parser(self, parser):
        pass

    def run(self, args):
        raise NotImplementedError


def command(name):
    def decorator(cls):
        cls.name = name
        return cls
    return decorator


@command('init')
class Init(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-t', '--template', default='blink', help='Project template to use')

    def run(self, args):
        raise Exception
        pass


@command('build')
class Build(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-t', '--template', help='Jinja makefile template to use')

    def run(self, args):
        if 'avr-gcc' not in self.env:
            self.env['avr-gcc'] = self.find_program('avr-gcc')
        render_template(args.template, env=env)
        run('make')


@command('upload')
class Upload(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-d', '--device', help='USB-device to upload firmware to')

    def run(self, args):
        pass


@command('serial')
class Serial(Command):
    def setup_arg_parser(self, parser):
        parser.add_argument('-d', '--device', help='USB-device to upload firmware to')

    def run(self, args):
        pass
