import os
import gradio as gr
from services.data_handler_module import DataHandler
from services.encrypt_module import EncryptionService
from services.partitioning_module import Partitioner
from services.tracker_module import Tracker

from ui.dataAccumlator import DataLogger
from ui.terminalUI import terminalUI

def senderPage(redundancyRatio, networkPassword,  file):
    hostLogs = DataLogger()
    with gr.Box(visible=False) as senderBox:
        with gr.Column():
            gr.Markdown("### <center> Sender Mode </center>")
            with gr.Row():
                btsn = gr.Button("Send Data / Start")

            def getValsList():
                return hostLogs.commonInfoList
            gr.DataFrame(value=getValsList, headers=hostLogs.commmonHeaders,
                         datatype=["str"] + ["number"]*5, wrap=True, every=0.1)

            jsonViewer = gr.JSON(label="Progress", value=[
                                 "Tracker.json yet to be generated"])

            with gr.Accordion(label="Terminal Main Logs"):
                terminalUI()
            with gr.Accordion(label="Terminal Network Logs", open=False):
                terminalUI(log_name="hostInterface")

            def getValues():
                return hostLogs.finalList

            with gr.Accordion(label="Peers Status", open=True):
                gr.DataFrame(value=getValues, headers=hostLogs.headers,
                             datatype=["str"]*6, wrap=True, every=0.1)

        def callFunc(file, networkPasswd, redundancyRatio, progress=gr.Progress(track_tqdm=True)):
            print(file.name, file.orig_name, redundancyRatio, networkPasswd)
            path, name = os.path.split(file.name)
            _dataHandler = DataHandler(
                file_path=file.name, filename=file.orig_name)
            hostLogs.commonInfoList[0][0] = str(path+"\\"+file.orig_name)
            progress(0.01, desc="Reading file", unit="percent")
            _dataHandler.read_file()
            hostLogs.commonInfoList[0][1] = f'{len(_dataHandler.data)} Bytes'
            progress(0.05, desc="Encrypting file ", unit="percent")
            EncryptionService.encrypt(_dataHandler)
            progress(
                0.1, desc="Paritioning the cipher into 512KB chunks", unit="percent")
            buffer = Partitioner.partition(_dataHandler)
            progress(0.11, desc="Invoking tracker service", unit="percent")
            print("Redundancy Ratio:", redundancyRatio)
            tracker = Tracker(fileName=file.orig_name, bufferObj=buffer,
                              progress=progress, redundancyRatio=redundancyRatio)
            json = tracker.send_chunks(network_passwd=networkPasswd)
            return gr.JSON(label="Tracker JSON", value=json)

        runEvent = btsn.click(fn=callFunc, inputs=[
                              file, networkPassword, redundancyRatio], outputs=jsonViewer)
        return senderBox, runEvent
