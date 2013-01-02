from logan.runner import run_app


def generate_settings():
    """
    Generate initial settings.
    """
    import os

    root_path = os.path.dirname(__file__)
    config_path = 'conf/initial.py'

    initial_settings = open(os.path.join(root_path, config_path))

    return initial_settings.read()


def main():
    run_app(
        project='newspeak',
        default_config_path='~/.newspeak/newspeak.conf.py',
        default_settings='newspeak.conf.defaults',
        settings_initializer=generate_settings,
        settings_envvar='NEWSPEAK_CONF',
    )

if __name__ == '__main__':
    main()
