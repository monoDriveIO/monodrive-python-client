import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='monodrive',
    version='0.0.1',
    author='monoDrive',
    author_email='support@monodrive.io',
    description='The python client for the monoDrive autonomous vehicle simulator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/monoDriveIO/python_client',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
    install_requires=[
        'Rx>=1.6,<3',
        'numpy>=1.17.4',
        'objectfactory>=0.0.3,<1',
        'elasticsearch>=7,<8'
    ]
)
