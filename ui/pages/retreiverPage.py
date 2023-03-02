import os
import gradio as gr
from retrieval_module import RetrieverModule

from ui.dataAccumlator import DataLogger
from ui.terminalUI import terminalUI

def retrievalPage(networkPassword,  file):
    hostLogs = DataLogger()
    with gr.Box(visible=False) as senderBox:
        with gr.Column():
            gr.Markdown("### <center> Retrieval Mode </center>")
            with gr.Row():
                btsn = gr.Button("Retrieve File / Start")

            def getValsList():
                return hostLogs.retrieverInfoList
            gr.DataFrame(value=getValsList, headers=hostLogs.retrieverHeaders,
                         datatype=["str"] + ["number"]*6, wrap=True, every=0.1)

            # fileViewer = gr.File(visible=True, label="Progress Indicator")
            
            progressBar = gr.Markdown(value="")
            with gr.Accordion(label="Terminal Main Logs"):
                terminalUI()
            with gr.Accordion(label="Terminal Network Logs", open=False):
                terminalUI(log_name="hostInterface")

            def getValues():
                return hostLogs.finalList

            with gr.Accordion(label="Peers Status", open=True):
                gr.DataFrame(value=getValues, headers=hostLogs.headers,
                             datatype=["str"]*6, wrap=True, every=0.1)

        def callFunc(file, networkPasswd, progress=gr.Progress(track_tqdm=True)):
            path, name = os.path.split(file.name)
            hostLogs.retrieverInfoList[0][0] = str(path+"\\"+file.orig_name)

            ret = RetrieverModule(tracker_path=file.name,
                                  network_passwd=networkPasswd)
            save_loc = ret.retrieve()
            return progressBar.update(value=f"## <center> Sucessfully Completed and file saved at {save_loc}</center>")
            # return gr.File(label=f"Retrieved File: {save_loc}", value=save_loc)

        runEvent = btsn.click(fn=callFunc, inputs=[
                              file, networkPassword], outputs=progressBar)
        return senderBox, runEvent
