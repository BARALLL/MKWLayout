__author__ = "baral"
__version__ = "0.1"

from BrawlCrate.API import *
from BrawlCrate.API.BrawlAPI import AppPath
from BrawlCrate.NodeWrappers import *
from BrawlLib.SSBB.ResourceNodes import *
from System.Windows.Forms import ToolStripMenuItem
from System.IO import *
from System import Environment


SCRIPT_NAME = "Minimap Scraping"

# BrawlAPI.ShowOKCancelPrompt("Press OK to continue.", SCRIPT_NAME)


user32 = windll.user32
kernel32 = windll.kernel32

WM_CLOSE = 0x0010


class DialogCloser:
    def __init__(self):
        self.cancelled = False
        if len(threading.enumerate()) == 0:
            raise Exception("No open forms found")
        self.check_window()

    def check_window(self):
        EnumWindowsProc = WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

        def enum_callback(hwnd, lparam):
            class_name = create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name, 256)
            if class_name.value == "#32770":
                user32.SendMessageW(hwnd, WM_CLOSE, 0, 0)
            return not self.cancelled

        user32.EnumThreadWindows(
            kernel32.GetCurrentThreadId(), EnumWindowsProc(enum_callback), 0)

    def dispose(self):
        self.cancelled = True


importFolderPath = BrawlAPI.OpenFolderDialog(
    "Choose the directory containing your .szs files")


if importFolderPath != "":

    defaultFolder = Environment.ExpandEnvironmentVariables(
        Path.Combine("%appdata%", "minimap-dae"))

    selectingExportFolderPath = BrawlAPI.ShowYesNoPrompt(
        "Would you like to choose the directory to export .dae files to?\n Default is "+defaultFolder, "Export Directory")

    if selectingExportFolderPath:
        exportFolderPath = BrawlAPI.OpenFolderDialog(
            "Choose the directory to export .dae files to")

    if not selectingExportFolderPath or exportFolderPath == "":
        exportFolderPath = defaultFolder

    exportFolder = Directory.CreateDirectory(exportFolderPath)

    szsFiles = Directory.EnumerateFiles(importFolderPath, "*.szs")

    for currentFile in szsFiles:
        # BrawlAPI.ShowWarning(currentFile, SCRIPT_NAME)
        fileName = currentFile.Substring(0)

        if BrawlAPI.OpenFileNoErrors(currentFile):
            root = BrawlAPI.RootNode

            with DialogCloser():
                mapBrres = root.FindChildrenByName("map_model.brres")

            if mapBrres != []:
                mapMDL0 = mapBrres[0].FindChildrenByName("map")

                indexExtension = currentFile.rfind(".")
                nameLength = (
                    indexExtension - (len(importFolderPath) + 1)
                    if indexExtension != -1
                    else len(importFolderPath) + 1
                )
                mapName = (
                    currentFile.Substring(
                        len(importFolderPath) + 1, nameLength)
                    + "-minimap.dae"
                )

                # mapMDL0[0].Export(Path.Combine(exportFolderPath, mapName))

                BrawlAPI.ForceCloseFile()
            else:
                BrawlAPI.ShowWarning("No map model found", SCRIPT_NAME)
        else:
            BrawlAPI.ShowWarning("Error opening the file", SCRIPT_NAME)

        # if not BrawlAPI.ForceCloseFile():
        #    BrawlAPI.ShowWarning("Error closing the file", SCRIPT_NAME)
else:
    BrawlAPI.ShowWarning("No folder selected.\n\n Abording...", SCRIPT_NAME)
