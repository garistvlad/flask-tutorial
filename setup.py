from setuptools import find_packages, setup

APP_NAME = "blog_app"


setup(
    name=APP_NAME,
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "pytest",
    ]
)
