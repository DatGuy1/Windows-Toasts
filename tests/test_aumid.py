import shutil

from pytest import raises


def test_register_hkey_icon(example_image_path):
    from scripts.register_hkey_aumid import register_hkey

    appId = "Test.Notification"
    appName = "Notification Test"

    with raises(ValueError, match="does not exist"):
        register_hkey(appId, appName, example_image_path.with_suffix(".nonexistant"))
    with raises(ValueError, match="must be of type .ico"):
        register_hkey(appId, appName, example_image_path)

    exampleIcoPath = example_image_path.with_suffix(".ico")
    shutil.copy(example_image_path, exampleIcoPath)
    pathExists = exampleIcoPath.exists()
    register_hkey(appId, appName, exampleIcoPath if pathExists else None)

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
            assert iconUri[0] == str(exampleIcoPath)
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

    exampleIcoPath.unlink()


def test_register_hkey_no_icon():
    from scripts.register_hkey_aumid import register_hkey

    appId = "Test.Notification"
    appName = "Notification Test"

    register_hkey(appId, appName, None)

    import winreg

    winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    keyPath = f"SOFTWARE\\Classes\\AppUserModelId\\{appId}"
    with winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER, keyPath) as masterKey:
        displayValue = winreg.QueryValueEx(masterKey, "DisplayName")
        assert displayValue[1] == winreg.REG_SZ
        assert displayValue[0] == appName

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
