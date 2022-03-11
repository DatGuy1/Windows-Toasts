from setuptools import setup

packages = ["windows_toasts"]

requires = ["winsdk"]

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="windows-toasts",
    version="0.3.0",
    description="Windows toast notifications sender",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="DatGuy",
    author_email="datguysteam@gmail.com",
    url="https://github.com/DatGuy1/Windows-Toasts",
    packages=packages,
    package_dir={"": "src"},
    package_data={
        "": ["LICENSE"],
        "windows_toasts": ["py.typed"]
    },
    include_package_data=True,
    scripts=["scripts/create_shell_link.py", "scripts/register_hkey_aumi.py"],
    python_requires=">=3.7",
    install_requires=requires,
    license="Apache License 2.0",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows :: Windows 10"
    ],
    project_urls={
        "Bug Tracker": "https://github.com/DatGuy1/Windows-Toasts/issues"
    }
)
