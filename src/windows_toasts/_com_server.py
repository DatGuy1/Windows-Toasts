"""
A COM server that Windows delivers toast activations to, written with ctypes so it needs neither comtypes nor pywin32

Windows looks up the activator's CLSID in the AUMID's ``CustomActivator`` registry value. If a process has registered
that class, Windows calls its ``INotificationActivationCallback.Activate``; otherwise it starts the class's
``LocalServer32`` command, with ``-Embedding`` added, and waits for that process to register it
"""

from __future__ import annotations

import atexit
import ctypes
import threading
import uuid
from collections.abc import Callable
from ctypes import wintypes

#: Receives the activation's arguments and the toast's inputs
ActivationCallback = Callable[[str, dict[str, str]], None]

_S_OK = 0
# HRESULTs are signed. https://learn.microsoft.com/windows/win32/seccrypto/common-hresult-values
_E_NOINTERFACE = 0x80004002 - 2**32
_E_POINTER = 0x80004003 - 2**32
_E_FAIL = 0x80004005 - 2**32
_CLASS_E_NOAGGREGATION = 0x80040110 - 2**32

# https://learn.microsoft.com/windows/win32/api/objbase/ne-objbase-coinit
_COINIT_MULTITHREADED = 0x0
# https://learn.microsoft.com/windows/win32/api/wtypesbase/ne-wtypesbase-clsctx
_CLSCTX_LOCAL_SERVER = 0x4
# https://learn.microsoft.com/windows/win32/api/combaseapi/ne-combaseapi-regcls
_REGCLS_MULTIPLEUSE = 0x1


class _GUID(ctypes.Structure):
    """GUID. https://learn.microsoft.com/windows/win32/api/guiddef/ns-guiddef-guid"""

    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]

    @classmethod
    def from_uuid(cls, value: uuid.UUID) -> _GUID:
        # bytes_le has the first three fields in little-endian order, which is how a GUID is laid out in memory
        return cls.from_buffer_copy(value.bytes_le)


class _NotificationUserInputData(ctypes.Structure):
    """NOTIFICATION_USER_INPUT_DATA. https://learn.microsoft.com/windows/win32/api/notificationactivationcallback/ns-notificationactivationcallback-notification_user_input_data"""

    _fields_ = [("Key", wintypes.LPCWSTR), ("Value", wintypes.LPCWSTR)]


# The interfaces' IIDs, which Windows defines. IUnknown's and IClassFactory's are in unknwn.h
# (https://learn.microsoft.com/windows/win32/api/unknwn/nn-unknwn-iunknown and
# https://learn.microsoft.com/windows/win32/api/unknwn/nn-unknwn-iclassfactory), and
# INotificationActivationCallback's in notificationactivationcallback.h
# (https://learn.microsoft.com/windows/win32/api/notificationactivationcallback/nn-notificationactivationcallback-inotificationactivationcallback)
_IID_IUNKNOWN = bytes(_GUID.from_uuid(uuid.UUID("00000000-0000-0000-C000-000000000046")))
_IID_ICLASSFACTORY = bytes(_GUID.from_uuid(uuid.UUID("00000001-0000-0000-C000-000000000046")))
_IID_INOTIFICATIONACTIVATIONCALLBACK = bytes(_GUID.from_uuid(uuid.UUID("53E31837-6600-4A81-9395-75CFFE746F94")))

_PGUID = ctypes.POINTER(_GUID)
_PPVOID = ctypes.POINTER(ctypes.c_void_p)
# The callbacks return plain longs, since ctypes.HRESULT would turn a failure into an exception on our side. Each
# method's first argument is the object it's called on
# https://learn.microsoft.com/windows/win32/api/unknwn/nf-unknwn-iunknown-queryinterface(refiid_void)
_QueryInterface = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, _PGUID, _PPVOID)
# https://learn.microsoft.com/windows/win32/api/unknwn/nf-unknwn-iunknown-addref and
# https://learn.microsoft.com/windows/win32/api/unknwn/nf-unknwn-iunknown-release
_AddRefOrRelease = ctypes.WINFUNCTYPE(wintypes.ULONG, ctypes.c_void_p)
# https://learn.microsoft.com/windows/win32/api/unknwn/nf-unknwn-iclassfactory-createinstance
_CreateInstance = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, _PGUID, _PPVOID)
# https://learn.microsoft.com/windows/win32/api/unknwn/nf-unknwn-iclassfactory-lockserver
_LockServer = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.BOOL)
# https://learn.microsoft.com/windows/win32/api/notificationactivationcallback/nf-notificationactivationcallback-inotificationactivationcallback-activate
_Activate = ctypes.WINFUNCTYPE(
    ctypes.c_long,
    ctypes.c_void_p,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.POINTER(_NotificationUserInputData),
    wintypes.ULONG,
)


class _ClassFactoryVtbl(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", _QueryInterface),
        ("AddRef", _AddRefOrRelease),
        ("Release", _AddRefOrRelease),
        ("CreateInstance", _CreateInstance),
        ("LockServer", _LockServer),
    ]


class _ActivationCallbackVtbl(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", _QueryInterface),
        ("AddRef", _AddRefOrRelease),
        ("Release", _AddRefOrRelease),
        ("Activate", _Activate),
    ]


class _ComObject(ctypes.Structure):
    """A COM object: a pointer to its vtable, followed by the id of the server it belongs to"""

    _fields_ = [("lpVtbl", ctypes.c_void_p), ("serverId", ctypes.c_size_t)]


def _server_of(this: int | None) -> ActivatorServer | None:
    if not this:
        return None

    return _serversById.get(_ComObject.from_address(this).serverId)


def _query_interface(
    this: int | None, riid: ctypes._Pointer[_GUID], ppv: ctypes._Pointer[ctypes.c_void_p], iids: tuple[bytes, ...]
) -> int:
    if not ppv:
        return _E_POINTER

    if riid and bytes(riid.contents) in iids:
        ppv[0] = this
        return _S_OK

    ppv[0] = None
    return _E_NOINTERFACE


def _add_ref_or_release(_this: int | None) -> int:
    # Each server's objects live as long as the process, counting is useless
    return 1


def _factory_query_interface(
    this: int | None, riid: ctypes._Pointer[_GUID], ppv: ctypes._Pointer[ctypes.c_void_p]
) -> int:
    return _query_interface(this, riid, ppv, (_IID_IUNKNOWN, _IID_ICLASSFACTORY))


def _callback_query_interface(
    this: int | None, riid: ctypes._Pointer[_GUID], ppv: ctypes._Pointer[ctypes.c_void_p]
) -> int:
    return _query_interface(this, riid, ppv, (_IID_IUNKNOWN, _IID_INOTIFICATIONACTIVATIONCALLBACK))


def _create_instance(
    this: int | None, outer: int | None, riid: ctypes._Pointer[_GUID], ppv: ctypes._Pointer[ctypes.c_void_p]
) -> int:
    if not ppv:
        return _E_POINTER

    ppv[0] = None
    if outer:
        return _CLASS_E_NOAGGREGATION

    server = _server_of(this)
    if server is None:
        return _E_FAIL

    return _callback_query_interface(ctypes.addressof(server.callbackObject), riid, ppv)


def _lock_server(_this: int | None, _lock: int) -> int:
    return _S_OK


def _activate(
    this: int | None,
    _appUserModelId: str | None,
    invokedArgs: str | None,
    data: ctypes._Pointer[_NotificationUserInputData],
    count: int,
) -> int:
    # Uncaught, an exception here would only be printed, and Windows told the call succeeded
    try:
        server = _server_of(this)
        if server is None or server.stopped:
            return _E_FAIL

        inputs = {data[i].Key or "": data[i].Value or "" for i in range(count)} if data else {}
        # Run on a thread of its own so a slow callback doesn't hold up Windows, which waits for this call to return
        threading.Thread(
            target=server.callback, args=(invokedArgs or "", inputs), name="windows_toasts activation"
        ).start()
        return _S_OK
    except Exception:
        return _E_FAIL


# Kept alive for the life of the process, since Windows holds pointers to them
_classFactoryVtbl = _ClassFactoryVtbl(
    _QueryInterface(_factory_query_interface),
    _AddRefOrRelease(_add_ref_or_release),
    _AddRefOrRelease(_add_ref_or_release),
    _CreateInstance(_create_instance),
    _LockServer(_lock_server),
)
_activationCallbackVtbl = _ActivationCallbackVtbl(
    _QueryInterface(_callback_query_interface),
    _AddRefOrRelease(_add_ref_or_release),
    _AddRefOrRelease(_add_ref_or_release),
    _Activate(_activate),
)

# Every server, by the id its COM objects carry, so the methods Windows calls can find it. Servers are never removed
# from here, even once stopped, since Windows may still hold pointers to their objects
_serversById: dict[int, ActivatorServer] = {}
# The servers that are running, by the class they registered
_serversByClsid: dict[uuid.UUID, ActivatorServer] = {}
_serversLock = threading.Lock()


class ActivatorServer:
    """
    Registers a toast activator's class with COM, on a thread of its own, so it
    doesn't matter how the caller's thread is set up or whether it runs a message loop
    """

    clsid: uuid.UUID
    callback: ActivationCallback

    def __init__(self, clsid: uuid.UUID, callback: ActivationCallback) -> None:
        self.clsid = clsid
        self.callback = callback
        serverId = id(self)
        self.factoryObject = _ComObject(ctypes.addressof(_classFactoryVtbl), serverId)
        self.callbackObject = _ComObject(ctypes.addressof(_activationCallbackVtbl), serverId)
        self._stopped = threading.Event()
        self._thread: threading.Thread | None = None
        _serversById[serverId] = self

    def start(self) -> None:
        """
        :raises OSError: If COM refuses to register the class
        """
        ready = threading.Event()
        errors: list[BaseException] = []
        self._thread = threading.Thread(
            target=self._run, args=(ready, errors), name="windows_toasts activator", daemon=True
        )
        self._thread.start()
        ready.wait()
        if errors:
            raise errors[0]

    def _run(self, ready: threading.Event, errors: list[BaseException]) -> None:
        ole32 = ctypes.OleDLL("ole32")
        # CoUninitialize returns nothing, which OleDLL would read as an HRESULT
        uninitialize = ctypes.WinDLL("ole32").CoUninitialize
        uninitialize.restype = None
        # Whatever goes wrong, start() is told, so it doesn't wait forever
        try:
            # https://learn.microsoft.com/windows/win32/api/combaseapi/nf-combaseapi-coinitializeex
            ole32.CoInitializeEx(None, _COINIT_MULTITHREADED)
            try:
                cookie = wintypes.DWORD()
                clsid = _GUID.from_uuid(self.clsid)
                # https://learn.microsoft.com/windows/win32/api/combaseapi/nf-combaseapi-coregisterclassobject
                ole32.CoRegisterClassObject(
                    ctypes.byref(clsid),
                    ctypes.byref(self.factoryObject),
                    _CLSCTX_LOCAL_SERVER,
                    _REGCLS_MULTIPLEUSE,
                    ctypes.byref(cookie),
                )
            except BaseException:
                uninitialize()
                raise
        except BaseException as e:
            errors.append(e)
            ready.set()
            return

        ready.set()
        # The class stays registered as long as this thread keeps the apartment alive
        self._stopped.wait()
        try:
            ole32.CoRevokeClassObject(cookie)
        finally:
            uninitialize()

    @property
    def stopped(self) -> bool:
        return self._stopped.is_set()

    def stop(self) -> None:
        self._stopped.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None


def start_server(clsid: uuid.UUID, callback: ActivationCallback) -> None:
    """
    Register the activator class, or change the callback if this process already has

    :raises OSError: If COM refuses to register the class
    """
    with _serversLock:
        server = _serversByClsid.get(clsid)
        if server is not None:
            server.callback = callback
            return

        server = ActivatorServer(clsid, callback)
        server.start()
        _serversByClsid[clsid] = server


def stop_server(clsid: uuid.UUID) -> None:
    """
    Revoke the activator class, if this process registered it
    """
    with _serversLock:
        server = _serversByClsid.pop(clsid, None)

    if server is not None:
        server.stop()


@atexit.register
def _stop_servers() -> None:
    # Stop Windows calling into an interpreter that's shutting down
    for clsid in list(_serversByClsid):
        stop_server(clsid)
