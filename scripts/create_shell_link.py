import argparse
import os
import sys
from pathlib import Path
from typing import Any, Optional

try:
    import pythoncom
    from win32com.propsys import propsys
    from win32com.shell import shell
except ImportError:
    raise ImportError(
        "pywin32 is required to run create_shell_link.py. To install, execute 'pip install pywin32' in a terminal"
    )


class IconFileAction(argparse.Action):  # pragma: no cover
    def __call__(self, parser_container, namespace, values: Any, option_string=None):
        if values.suffix != ".ico":
            raise ValueError("The supplied icon file is not of type .ico.")

        setattr(namespace, self.dest, values)


# noinspection PyUnresolvedReferences
def create_shell_link(
    appId: str,
    appName: str,
    iconPath: Optional[Path] = None,
    overwrite: bool = False,
    appDataPath: str = os.getenv("APPDATA"),
):
    # See https://github.com/mohabouje/WinToast/blob/master/src/wintoastlib.cpp#L594
    if appDataPath is None:  # pragma: no cover
        raise RuntimeError("Couldn't find APPDATA path. Please rerun this script with the --appdata argument")

    programsPath = Path(appDataPath) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    shellLinkPath = programsPath / f"{appName}.lnk"
    linkExists = shellLinkPath.exists()
    if linkExists:  # pragma: no cover
        if overwrite:
            print("Script run with --overwrite, overwriting existing link...")
        else:
            sys.exit(
                f"Link '{shellLinkPath}' already exists. To overwrite, rerun this script with the --overwrite argument"
            )

    # Adapted from https://github.com/mhammond/pywin32/blob/main/com/win32comext/shell/demos/create_link.py
    # noinspection PyTypeChecker
    shellLink = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink
    )
    # Set shell link arguments
    shellLink.SetPath("")
    shellLink.SetArguments("")
    shellLink.SetWorkingDirectory("")
    if iconPath is not None:
        shellLink.SetIconLocation(str(iconPath.resolve()), 0)

    # Set AUMID to supplied argument
    propertyStore = shellLink.QueryInterface(propsys.IID_IPropertyStore)
    propertyKey = propsys.PSGetPropertyKeyFromName("System.AppUserModel.ID")
    propertyStore.SetValue(propertyKey, propsys.PROPVARIANTType(appId))
    propertyStore.Commit()
    # Save file
    # noinspection PyUnresolvedReferences
    propertyStore.QueryInterface(pythoncom.IID_IPersistFile).Save(str(shellLinkPath), True)
    print(f"Successfully {'modified' if linkExists else 'created'} shell link with the AUMID '{appId}'")


def main():
    parser = argparse.ArgumentParser(description="Create shell link for use in toast notifications")
    parser.add_argument("--appdata", "-ad", type=str, required=False, help="AppData path if script fails to find it")
    parser.add_argument("--app_id", "-a", type=str, required=True, help="Application User Model ID for identification")
    parser.add_argument("--name", "-n", type=str, required=True, help="Display name on notification")
    parser.add_argument(
        "--icon", "-i", type=Path, required=False, action=IconFileAction, help="Path to image file for desired icon"
    )
    if sys.version_info >= (3, 9):
        parser.add_argument(
            "--overwrite", "-o", action=argparse.BooleanOptionalAction, help="Overwrite if a link already exists"
        )
    else:
        parser.add_argument(
            "--overwrite", "-o", default=False, action="store_true", help="Overwrite if a link already exists"
        )
    args = parser.parse_args()

    create_shell_link(
        appId=args.app_id, appName=args.name, iconPath=args.icon, overwrite=args.overwrite, appDataPath=args.appdata
    )


if __name__ == "__main__":  # pragma: no cover
    main()
