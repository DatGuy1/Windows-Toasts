from pathlib import Path

# Need to find a path that is constant in every Windows instance/version
iconPath = Path(
    "C:\\Windows\\WinSxS\\amd64_microsoft-windows-dxp-deviceexperience_31bf3856ad364e35_10.0.22621"
    ".1_none_a8baf777ed856ee0\\folder.ico"
)
pathExists = iconPath.exists()


def test_register_hkey():
    from scripts.register_hkey_aumid import register_hkey

    appId = "Test.Notification"
    appName = "Notification Test"
    register_hkey(appId, appName, iconPath if pathExists else None)

    import winreg

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
        displayValue = winreg.QueryValueEx(masterKey, "DisplayName")
        assert displayValue[1] == winreg.REG_SZ
        assert displayValue[0] == appName

        if pathExists:
            iconUri = winreg.QueryValueEx(masterKey, "IconUri")
            assert iconUri[1] == winreg.REG_SZ
            assert iconUri[0] == str(iconPath)
        else:
            try:
                winreg.QueryValueEx(masterKey, "IconUri")
                assert False
            except FileNotFoundError:
                pass

        winreg.DeleteKeyEx(winreg.HKEY_CURRENT_USER, keyPath)
        try:
            winreg.QueryInfoKey(masterKey)
            assert False
        except (FileNotFoundError, OSError):
            pass
