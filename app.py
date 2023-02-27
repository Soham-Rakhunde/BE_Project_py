import json
import time
import gradio as gr
# from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from services.network_services.peerTLSInterface import PeerTLSInterface
from services.tracker_module import Tracker
from ui.dataAccumlator import DataLogger

from ui.printer import Printer
from services.key_handling_module import KeyHandlerUI
from retrieval_module import RetrieverModule
from services.encrypt_module import EncryptionService
from services.data_handler_module import DataHandler
from services.hmac_module import HMAC_Module
from services.partitioning_module import Partitioner




pr = Printer()

def terminalUI(log_name:str = None):
    if log_name == None:
        term =  gr.HTML(value=pr.getHTML,label="Terminal", every = 1)
    else:
        def callSpecialLogs():
            return pr.getHTML(log_name=log_name)
        term = gr.HTML(value=callSpecialLogs,label="Terminal", every = 1)
    return term
    

def upload_file(files):
    file_paths = [file.name for file in files]
    print(file_paths)
    print(files.name)
    return files.name


def passwordPage():
    keyHandler = KeyHandlerUI()

    # tabBox = mainTabs()
    with gr.Box() as passwordBox:
        if keyHandler.is_password_created():
            password = gr.Textbox(label="Keystore Passphrase", placeholder='Enter keystore Passphrase')
            btn = gr.Button(value="Submit")
            btn.style(full_width=False)

            def retrieve_key(passwd):
                keyHandler.retrieve(password=passwd)
                return [btn.update(visible=False), password.update(visible=False)]

            btn.click(retrieve_key, inputs=password, outputs=[passwordBox])
        else:
            with gr.Row():
                password = gr.Textbox(label="Keystore Passphrase", placeholder='Enter new Passphrase')
                confirmPassword = gr.Textbox(label="Confirm Passphrase", placeholder='Confirm the Passphrase', type='password')
            btn = gr.Button(value="Confirm", visible=False)
            btn.style(full_width=False)

            def password_validation(passwd, passwd2):
                if len(passwd) > 0 and passwd == passwd2:
                    return btn.update(visible=True)
                else:
                    return btn.update(visible=False)
                
            password.change(password_validation, inputs=[password, confirmPassword], outputs=btn)
            confirmPassword.change(password_validation, inputs=[password, confirmPassword], outputs=btn)

            def password_generate(passwd):
                keyHandler.generate(password=passwd)
                keyHandler.save()


                return [password.update(visible=False), confirmPassword.update(visible=False), btn.update(visible=False)]

            btn.click(password_generate, inputs= password, outputs=[password, confirmPassword, btn])

           


def receiverPage(redundancyRatio):
    # DiscoveryServiceInterface()
    peerInterface = PeerTLSInterface(remoteAddress = '192.168.0.103', localPort= 11111)

    with gr.Box(visible=False) as receiverBox:
        gr.Markdown("### <center> Receiver Mode </center>")   
        def getValsList():
            return [[f"{peerInterface.localServerAddress}:{peerInterface.localPort}", f"{peerInterface.remClientAddress}",
                              peerInterface.localRedundancyCount, peerInterface.mode,
                              "-" if peerInterface.locationsList == None else " ".join(peerInterface.locationsList)]]
        gr.DataFrame(value=getValsList, headers=["Local IP Address",  "Peer IP Address", 'Local Redundancy Ratio', 'Mode', 'Locations list'], 
                     datatype=["str"]*5, wrap=True, every=1)
        

        def callFunc(progressBar, progress=gr.Progress(track_tqdm=True)):
            print(redundancyRatio, "Sasw")
            peerInterface.progress = progress
            peerInterface.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            return progressBar.update(value="<center> # Sucessfully Completed </center>")
        terminalUI()
        progressBar = gr.Markdown(value="")
        btsn = gr.Button("Run")
        btsn.click(fn=callFunc, inputs=[progressBar, redundancyRatio],outputs=progressBar)
    
        return receiverBox

def senderPage(redundancyRatio):
    # DiscoveryServiceInterface()
    _dataHandler, tracker = None, None
    with gr.Box(visible=False) as senderBox:
        with gr.Column():
            gr.Markdown("### <center> Sender Mode </center>")
            with gr.Row():
                btsn = gr.Button("Send Data / Start")   
                
            def getValsList():
                return [[_dataHandler.file_path if _dataHandler is not None else "", 
                    len(_dataHandler.data) if _dataHandler is not None else "", 
                    tracker.num_of_chunks if tracker is not None else "",
                    tracker.nodes_redundancy_ratio if tracker is not None else "",
                    ]]
            gr.DataFrame(value=getValsList, headers=["File Name", "File Size(Bytes)", "Total Chunks", 'Redundancy Ratio'], 
                        datatype=["str"]*5, wrap=True, every=0.1)
            
            # progressBar = gr.Markdown(value="")
            

            jsonViewer = gr.JSON(visible="Progress",value=["Tracker.json yet to be generated"])

            with gr.Accordion(label="Terminal Main Logs"):
                terminalUI()
            with gr.Accordion(label="Termianl Network Logs", open=False):
                terminalUI(log_name="hostInterface")

            hostLogs = DataLogger()
            def getValues():
                return hostLogs.finalList

            with gr.Accordion(label="Peers Status", open=True):
                gr.DataFrame(value=getValues, headers=["Thread Id", "Chunk Id", "Peer Id", "Peer IP Address", 'Location List', "Status"],
                            datatype=["str"]*6, wrap=True, every=0.1)
            

        def callFunc(redundancyRatio, progress=gr.Progress(track_tqdm=True)):
            _dataHandler = DataHandler('C:\\Users\\soham\\OneDrive\\Pictures\\Wallpapers\\3433.jpg')
            progress(0.01, desc="Reading file", unit="percent")
            _dataHandler.read_file()
            progress(0.05, desc="Encrypting file ", unit="percent")
            EncryptionService.encrypt(_dataHandler)
            progress(0.1, desc="Paritioning the cipher into 512KB chunks", unit="percent")
            buffer = Partitioner.partition(_dataHandler)
            progress(0.11, desc="Invoking tracker service", unit="percent")
            print("Redundancy Ratio:", redundancyRatio)
            tracker = Tracker(fileName=_dataHandler.file_name(), bufferObj=buffer, progress=progress, redundancyRatio=redundancyRatio)
            json = tracker.send_chunks()
            return gr.JSON(label="Tracker JSON", value=json)
    
        runEvent =btsn.click(fn=callFunc, inputs=redundancyRatio,outputs=jsonViewer)
        return senderBox, runEvent


def homePage():
    with gr.Box(visible= True) as homeBox:
        with gr.Row():
            with gr.Column(scale=8):
                gr.Markdown('<center>For Send mode upload the file to be sent & for Retreiver mode upload tracker.json file</center>')
                file_output = gr.File()
                uploadButton = gr.UploadButton(value="Browse Files to Send or Tracker file to retrieve")
                uploadButton.upload(upload_file, uploadButton, file_output)
            with gr.Column(scale=6, variant='panel'):
                redundancyRatio = gr.Slider(minimum=1,step=1, maximum=10, value=2, label="Select a redundancy ratio", interactive=True)
                radio = gr.Radio(label="Select a mode to continue",
                         choices=["Send", "Retrieve", "Receive"])
                startBtn = gr.Button(value="Start", elem_id='homeBtn1')
        return homeBox, radio, redundancyRatio, startBtn


with gr.Blocks(css='ui/main.css') as demo:
    # discovery = DiscoveryServiceInterface()
    with gr.Row():
        with gr.Column(scale=6,): 
            gr.Markdown("# Secure data storage and hiding")
        backBtn = gr.Button("Back", visible=False)
    
    homeBox, radio, redundancyRatio, startBtn = homePage()
    senderBox, runEvent = senderPage(redundancyRatio)
    receiverBox = receiverPage(redundancyRatio)
 

    def openPage(radio):
        if radio == "Receive":
            return [homeBox.update(visible=False), senderBox.update(visible=False), receiverBox.update(visible=True), backBtn.update(visible=True)]
        elif radio == "Send":
            return [homeBox.update(visible=False), senderBox.update(visible=True), receiverBox.update(visible=False), backBtn.update(visible=True)]

    startBtn.click(openPage, inputs=radio ,outputs=[homeBox, senderBox, receiverBox, backBtn])

    def backBtnHandler(radio):
        printer = Printer()
        printer.flush()
        return [homeBox.update(visible=True), senderBox.update(visible=False), receiverBox.update(visible=False), backBtn.update(visible=False)]
    
    backBtn.click(backBtnHandler, inputs=radio ,outputs=[homeBox, senderBox, receiverBox, backBtn], cancels=[runEvent])

demo.queue()


if __name__ == '__main__':
    demo.launch()