import gradio as gr
from services.hiding_service.image_gatherer import ImageGatherer

from services.network_services.peerTLSInterface import PeerTLSInterface
from ui.terminalUI import terminalUI

def peerPage(redundancyRatio, networkPasswd):
    peerInterface = None
    ImageGatherer()
    with gr.Box(visible=False) as receiverBox:
        with gr.Column():
            gr.Markdown("### <center> Peer Mode </center>")
            with gr.Row():
                btsn = gr.Button("Start Listening")

            def getValsList():
                return [[
                    f"{peerInterface.localServerAddress if peerInterface else ''}:{peerInterface.localPort if peerInterface else ''}", 
                    f"{peerInterface.remClientAddress if peerInterface else ''}",
                         peerInterface.localRedundancyCount if peerInterface else '', 
                         peerInterface.mode if peerInterface else '',
                         "-" if peerInterface==None or peerInterface.locationsList == None else " ".join(peerInterface.locationsList)]]
            gr.DataFrame(value=getValsList, headers=["Local IP Address",  "Peer IP Address", 'Local Redundancy Ratio', 'Mode', 'Locations list'],
                         datatype=["str"]*5, wrap=True, every=1)

            terminalUI()
            progressBar = gr.Markdown(value="")
            def callFunc(redundancyRatio, networkPasswd, progress=gr.Progress(track_tqdm=True)):
                peerInterface = PeerTLSInterface(
                    remoteAddress='192.168.0.103', localPort=11111)
                peerInterface.progress = progress
                peerInterface.connectToRemoteClient(
                    networkPassword=networkPasswd, localRedundancyCount=redundancyRatio)
                return progressBar.update(value="## <center> Sucessfully Completed </center>")
            
            btsn.click(fn=callFunc, inputs=[
                       redundancyRatio, networkPasswd], outputs=progressBar)

            return receiverBox

