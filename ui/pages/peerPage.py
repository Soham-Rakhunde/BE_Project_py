import gradio as gr

from services.network_services.peerTLSInterface import PeerTLSInterface
from ui.terminalUI import terminalUI

def peerPage(redundancyRatio, networkPasswd):
    # DiscoveryServiceInterface()
    peerInterface = PeerTLSInterface(
        remoteAddress='192.168.0.103', localPort=11111)

    with gr.Box(visible=False) as receiverBox:
        with gr.Column():
            gr.Markdown("### <center> Receiver Mode </center>")
            with gr.Row():
                btsn = gr.Button("Send Listening")

            def getValsList():
                return [[f"{peerInterface.localServerAddress}:{peerInterface.localPort}", f"{peerInterface.remClientAddress}",
                         peerInterface.localRedundancyCount, peerInterface.mode,
                         "-" if peerInterface.locationsList == None else " ".join(peerInterface.locationsList)]]
            gr.DataFrame(value=getValsList, headers=["Local IP Address",  "Peer IP Address", 'Local Redundancy Ratio', 'Mode', 'Locations list'],
                         datatype=["str"]*5, wrap=True, every=1)

            def callFunc(progressBar, redundancyRatio, networkPasswd, progress=gr.Progress(track_tqdm=True)):
                peerInterface.progress = progress
                peerInterface.connectToRemoteClient(
                    networkPassword=networkPasswd, localRedundancyCount=redundancyRatio)
                return progressBar.update(value="<center> # Sucessfully Completed </center>")
            terminalUI()
            progressBar = gr.Markdown(value="")
            btsn.click(fn=callFunc, inputs=[
                       progressBar, redundancyRatio, networkPasswd], outputs=progressBar)

            return receiverBox

