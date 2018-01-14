from setuptools import setup, find_packages


setup(
    name="proxy_server",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'selectors2 >= 2.0.1',
        'pyyaml >= 3.12'
    ],
    author="pjmd",
    author_email="pjmd@pjmd.com",
    description="light proxy",
    license="PSF",
    keywords="proxy server",
)