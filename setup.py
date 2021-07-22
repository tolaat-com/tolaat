from distutils.core import setup


setup(
    name='tolaat',
    version='0.0.1',
    description='tolat hamishpat\'s website',
    url='https://github.com/tolaat-com/tolaatcom',
    download_url='https://github.com/tolaat/tolaatcom/archive/refs/tags/0.0.1.tar.gz',
    author='Andy Worms',
    author_email='andyworms@gmail.com',
    license='mit',
    packages=['tolaatcom'],
    install_requires=['tolaat-nhc==0.0.11'],
    zip_safe=False
)