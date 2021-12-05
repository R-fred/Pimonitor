from setuptools import setup

setup(name='pi_monitor',
      entry_points={'console_scripts': ['pimonitor = pi_monitor.pimonitor:cli'],},
      version='0.24.8',
      description='A package to monitor your raspberry pi and more!',
      url='',
      author='Frederick Chesneau',
      author_email='fchesneau@gmail.com',
      license='MIT',
      packages=['pi_monitor', 'pi_monitor.monitor', 'pi_monitor.server'],
      zip_safe=False,
      install_requires=['psutil', 'rich', 'click'])