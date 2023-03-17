from setuptools import setup

packages = ["windows_toasts", "scripts"]

requires = ["winsdk"]

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="windows-toasts",
    version="0.3.3",
    description="Windows toast notifications sender",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="DatGuy",
    author_email="datguysteam@gmail.com",
    url="https://github.com/DatGuy1/Windows-Toasts",
    packages=packages,
    package_dir={"windows_toasts": "src/windows_toasts"},
    package_data={"": ["LICENSE"], "windows_toasts": ["py.typed"]},
    include_package_data=True,
    entry_points={"console_scripts": ["register_hkey_aumid = scripts.register_hkey_aumid:main"]},
    python_requires=">=3.8",
    install_requires=requires,
    license="Apache 2.0",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    project_urls={"Bug Tracker": "https://github.com/DatGuy1/Windows-Toasts/issues"},
)
