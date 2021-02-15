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
        deploy-helm=deployer.scripts.deploy_helm:deploy_helm
        push-image=deployer.scripts.push_image:push_image
    ''',
)