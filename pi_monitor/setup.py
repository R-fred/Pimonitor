from setuptools import setup

setup(name='pi_monitor',
      version='0.13.4',
      description='A package to monitor your raspberry pi and more!',
      url='',
      author='Frederick Chesneau',
      author_email='fchesneau@gmail.com',
      license='MIT',
      packages=['pi_monitor', 'pi_monitor.monitor', 'pi_monitor.server', "pi_monitor.cli"],
      zip_safe=False)