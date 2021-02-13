from setuptools import setup

setup(
    name='deployer',
    version='0.1',
    py_modules=['deployer'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        push-image=deployer.scripts.push_image:push_image
    ''',
)