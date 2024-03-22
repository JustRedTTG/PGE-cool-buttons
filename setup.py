from setuptools import setup

version = "1.0"
short = 'Pygameextra cool buttons is a extension for pygameextra that adds cool buttons'
long = '''Pygameextra cool buttons is an extension for pygameextra,
that adds many button effects and customizations to spice up your app!

github: https://github.com/JustRedTTG/PGE-cool-buttons'''

# Setting up
setup(
    name="pygameextra_cool_buttons",
    version=version,
    author="Red",
    author_email="redtonehair@gmail.com",
    description=short,
    long_description_content_type="text/markdown",
    long_description=long,
    packages=['pygameextra_cool_buttons', 'pygameextra_cool_buttons_tester'],
    install_requires=['pygameextra>=2.0.0b45', 'Pillow'],
    package_data={},
    keywords=['python'],
    entry_points={
        'console_scripts': [
            'pygameextra-cb-tester = pygameextra_cool_buttons_tester.__init__:run',
        ],
    }
)
