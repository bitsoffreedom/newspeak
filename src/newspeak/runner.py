from logan.runner import run_app


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """
    return ""


def main():
    run_app(
        project='newspeak',
        default_config_path='~/.newspeak/',
        default_settings='newspeak.conf.defaults',
        settings_initializer='newspeak.logan_runner.generate_settings',
        settings_envvar='NEWSPEAK_CONF',
    )

if __name__ == '__main__':
    main()
