from setuptools import setup

packages = ["windows_toasts", "scripts"]

requires = [
    "winrt-runtime~=3.0",
    "winrt-Windows.Data.Xml.Dom~=3.0",
    "winrt-Windows.Foundation~=3.0",
    "winrt-Windows.Foundation.Collections~=3.0",
    "winrt-Windows.UI.Notifications~=3.0",
]

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

about: dict[str, str] = {}
with open("src/windows_toasts/_version.py", "r") as f:
    exec(f.read(), None, about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email="datguysteam@gmail.com",
    url=about["__url__"],
    packages=packages,
    package_dir={"windows_toasts": "src/windows_toasts"},
    package_data={"": ["LICENSE"], "windows_toasts": ["py.typed"]},
    include_package_data=True,
    entry_points={"console_scripts": ["register_hkey_aumid = scripts.register_hkey_aumid:main"]},
    python_requires=">=3.9",
    install_requires=requires,
    license=about["__license__"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    project_urls={
        "Documentation": "https://windows-toasts.readthedocs.io",
        "Source": "https://github.com/DatGuy1/Windows-Toasts",
    },
)
