from logan.runner import run_app


def generate_secret_key():
    """ Generate a random secret key. """
    from random import choice

    key_characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    key_length = 50
    return ''.join([choice(key_characters) for i in range(key_length)])


def generate_settings():
    """
    Generate initial settings.
    """
    import os

    root_path = os.path.dirname(__file__)
    config_path = 'conf/initial.py'

    initial_settings = open(os.path.join(root_path, config_path)).read()

    secret_key = generate_secret_key()
    initial_settings += (
        "\n# Automatically generated by Newspeak.\n"
        "SECRET_KEY = '%s'\n" % secret_key
    )

    return initial_settings


def main():
    """ Use logan to run newspeak as a standalone application. """

    run_app(
        project='newspeak',
        default_config_path='~/.newspeak/newspeak.conf.py',
        default_settings='newspeak.conf.default',
        settings_initializer=generate_settings,
        settings_envvar='NEWSPEAK_CONF',
    )

if __name__ == '__main__':
    main()
