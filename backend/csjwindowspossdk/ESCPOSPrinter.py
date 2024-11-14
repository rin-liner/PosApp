import clr
from pathlib import Path
dllPath = Path(__file__).parent/"Library"/"CSJPOSLib.dll"


def setDllPath(path: str):
    global dllPath
    dllPath = path


class CitizenPrinterInfo:
    def __init__(self, ipAddress: str, macAddress: str, bdAddress: str, deviceName: str, printerModel: str, **kwargs):
        self.ipAddress = ipAddress
        self.macAddress = macAddress
        self.bdAddress = bdAddress
        self.deviceName = deviceName
        self.printerModel = printerModel


class ESCPOSPrinter:
    def __init__(self):
        if not dllPath.exists():
            raise FileNotFoundError(f"CSJPOSLib.dll not found in {dllPath}")
        clr.AddReference(str(dllPath))
        # This import may cause an error in some IDEs or linters because the DLL is dynamically loaded at runtime
        import com.citizen.sdk
        self.__printer = com.citizen.sdk.ESCPOSPrinter()

    def Connect(self, connectType: int, addr: int, Port: int = None, Timeout: int = None):
        args = [connectType, addr]
        Port and args.append(Port)
        Timeout and args.append(Timeout)
        return self.__printer.Connect(*args)

    def Disconnect(self):
        return self.__printer.Disconnect()

    def SetCommProperties(self, baudRate: int, parity: int, handShake: int):
        return self.__printer.SetCommProperties(baudRate, parity, handShake)

    def SetEncoding(self, charset: str):
        return self.__printer.SetEncoding(charset)

    def PrinterCheck(self):
        return self.__printer.PrinterCheck()

    def Status(self, type: int = None):
        args = [type] if type else []
        return self.__printer.Status(*args)

    def PrintText(self, data: str, alignment: int, attribute: int, textSize: int):
        return self.__printer.PrintText(data, alignment, attribute, textSize)

    def PrintPaddingText(self, data: str, attribute: int, textSize: int, length: int, side: int):
        return self.__printer.PrintPaddingText(data, attribute, textSize, length, side)

    def PrintTextPCFont(self, data: str, alignment: int, fntName: str, point: int, style: int, hRatio: int, vRatio: int):
        return self.__printer.PrintTextPCFont(data, alignment, fntName, point, style, hRatio, vRatio)

    def PrintBitmap(self, fileName: str, alignment: int, width: int = None, mode: int = None) -> int:
        args = [fileName, alignment]
        width and args.append(width)
        mode and args.append(mode)
        return self.__printer.PrintBitmap(*args)

    def SetNVBitmap(self, number: int, fileName: str, width: int, mode: int = None) -> int:
        args = [number, fileName, width]
        mode and args.append(mode)
        return self.__printer.SetNVBitmap(*args)

    def PrintNVBitmap(self, nvImageNumber: int, alignment: int) -> int:
        return self.__printer.PrintNVBitmap(nvImageNumber, alignment)

    def PrintBarCode(self, data: str, symbology: int, height: int, width: int, alignment: int, textPosition: int):
        return self.__printer.PrintBarCode(data, symbology, height, width, alignment, textPosition)

    def PrintPDF417(self, data: str, columns: int, rows: int, width: int, height: int, ECLevel: int, alignment: int) -> int:
        return self.__printer.PrintPDF417(data, columns, rows, width, height, ECLevel, alignment)

    def PrintQRCode(self, data: str, moduleSize: int, ECLevel: int, alignment: int):
        return self.__printer.PrintQRCode(data, moduleSize, ECLevel, alignment)

    def PrintGS1DataBarStacked(self, data: str, symbology: int, moduleSize: int, maxSize: int, alignment: int) -> int:
        return self.__printer.PrintGS1DataBarStacked(data, symbology, moduleSize, maxSize, alignment)

    def CutPaper(self, type: int):
        return self.__printer.CutPaper(type)

    def UnitFeed(self, ufCount: int) -> int:
        return self.__printer.UnitFeed(ufCount)

    def MarkFeed(self, markType: int) -> int:
        return self.__printer.MarkFeed(markType)

    def OpenDrawer(self, drawer: int, pulseLen: int) -> int:
        return self.__printer.OpenDrawer(drawer, pulseLen)

    def TransactionPrint(self, control: int) -> int:
        return self.__printer.TransactionPrint(control)

    def RotatePrint(self, rotation: int) -> int:
        return self.__printer.RotatePrint(rotation)

    def PageModePrint(self, control: int) -> int:
        return self.__printer.PageModePrint(control)

    def ClearPrintArea(self) -> int:
        return self.__printer.ClearPrintArea()

    def ClearOutput(self) -> int:
        return self.__printer.ClearOutput()

    def PrintData(self, data: bytes) -> int:
        return self.__printer.PrintData(data)

    def PrintNormal(self, data: str) -> int:
        return self.__printer.PrintNormal(data)

    def WatermarkPrint(self, start: int, nvImageNumber: int, pass_num: int, feed: int, repeat: int) -> int:
        return self.__printer.WatermarkPrint(start, nvImageNumber, pass_num, feed, repeat)

    def SearchCitizenPrinter(self, connectType: int, searchTime: int) -> tuple[list[CitizenPrinterInfo], int]:
        result: int = 0
        data, result = self.__printer.SearchCitizenPrinter(
            connectType, searchTime, result)
        data = [{k: getattr(x, k) for k in dir(x)} for x in data]
        data = [CitizenPrinterInfo(**x) for x in data]
        return data, result

    def SearchESCPOSPrinter(self, connectType: int, searchTime: int) -> tuple[list[str], int]:
        result: int = 0
        data, result = self.__printer.SearchESCPOSPrinter(
            connectType, searchTime, result)
        return list(data), result

    def SetIPSettings(self, macAddress: str, enableDHCP: bool, ipAddress: str, subnetMask: str, defaultGateway: str) -> int:
        return self.__printer.SetIPSettings(macAddress, enableDHCP, ipAddress, subnetMask, defaultGateway)

    def PrinterCheckEx(self, connectType: int, addr: str, port: int = None, timeout: int = None) -> tuple[int, int]:
        status: int = 0
        args = [status, connectType, addr]
        port and args.append(port)
        timeout and args.append(timeout)
        return self.__printer.PrinterCheckEx(*args)

    def OpenDrawerEx(self, drawer: int, pulseLen: int, connectType: int, addr: str, port: int = None, timeout: int = None) -> int:
        args = [drawer, pulseLen, connectType, addr]
        port and args.append(port)
        timeout and args.append(timeout)
        return self.__printer.OpenDrawerEx(*args)

    def SetPrintCompletedTimeout(self, timeout: int) -> int:
        return self.__printer.SetPrintCompletedTimeout(timeout)

    def SetLog(self, mode: int, path: str, maxSize: int) -> None:
        self.__printer.SetLog(mode, path, maxSize)

    def GetVersionCode(self) -> int:
        return self.__printer.GetVersionCode()

    def GetVersionName(self) -> str:
        return self.__printer.GetVersionName()
