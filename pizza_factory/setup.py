from setuptools import setup, find_packages

requires = ['pyramid']

setup(name='pizza_factory',
      version='0.0.1',
      description='',
      long_description='',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pizza_factory",
      entry_points="""\
      [paste.app_factory]
          main = pizza_factory:main
      """)
