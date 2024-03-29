try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='BZDTests',
    version='1.0',
    description='',
    author='Ilya Kulakov',
    author_email='kulakov.ilya@gmail.com',
    url='https://github.com/Kentzo/BZD-tests',
    install_requires=[
        "Pylons>=1.0",
        "SQLAlchemy>=0.7.3",
        "MySQL_python>=1.2.3",
        "repoze.what_pylons>=1.0",
        "repoze.what_quickstart>=1.0.9",
        "WebOb==1.0.8"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'bzdtests': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'bzdtests': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = bzdtests.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
