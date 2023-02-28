import json
import os
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

           


def peerPage(redundancyRatio, networkPasswd):
    # DiscoveryServiceInterface()
    peerInterface = PeerTLSInterface(remoteAddress = '192.168.0.103', localPort= 11111)

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
                peerInterface.connectToRemoteClient(networkPassword=networkPasswd, localRedundancyCount=redundancyRatio)
                return progressBar.update(value="<center> # Sucessfully Completed </center>")
            terminalUI()
            progressBar = gr.Markdown(value="")
            btsn.click(fn=callFunc, inputs=[progressBar, redundancyRatio, networkPasswd],outputs=progressBar)
        
            return receiverBox

def senderPage(redundancyRatio, networkPassword,  file):
# DiscoveryServiceInterface()
    hostLogs = DataLogger()
    with gr.Box(visible=False) as senderBox:
        with gr.Column():
            gr.Markdown("### <center> Sender Mode </center>")
            with gr.Row():
                btsn = gr.Button("Send Data / Start")   
                
            def getValsList():
                return hostLogs.commonInfoList
            gr.DataFrame(value=getValsList, headers=hostLogs.commmonHeaders, 
                        datatype=["str"] +["number"]*5, wrap=True, every=0.1)

            jsonViewer = gr.JSON(label="Progress",value=["Tracker.json yet to be generated"])

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
            _dataHandler = DataHandler(file_path=file.name, filename=file.orig_name)
            hostLogs.commonInfoList[0][0] =str(path+"\\"+file.orig_name)
            progress(0.01, desc="Reading file", unit="percent")
            _dataHandler.read_file()
            hostLogs.commonInfoList[0][1] = f'{len(_dataHandler.data)} Bytes'
            progress(0.05, desc="Encrypting file ", unit="percent")
            EncryptionService.encrypt(_dataHandler)
            progress(0.1, desc="Paritioning the cipher into 512KB chunks", unit="percent")
            buffer = Partitioner.partition(_dataHandler)
            progress(0.11, desc="Invoking tracker service", unit="percent")
            print("Redundancy Ratio:", redundancyRatio)
            tracker = Tracker(fileName=_dataHandler.file_name, bufferObj=buffer, progress=progress, redundancyRatio=redundancyRatio)
            json = tracker.send_chunks(network_passwd=networkPasswd)
            return gr.JSON(label="Tracker JSON", value=json)
        
        runEvent =btsn.click(fn=callFunc, inputs=[file, networkPassword,redundancyRatio],outputs=jsonViewer)
        return senderBox, runEvent


def retrievalPage(networkPassword,  file):
# DiscoveryServiceInterface()
    hostLogs = DataLogger()
    with gr.Box(visible=False) as senderBox:
        with gr.Column():
            gr.Markdown("### <center> Retrieval Mode </center>")
            # with gr.Accordion(label="Tracker JSON file", open=False):
            #     retrJSON = gr.JSON(label="Tracker JSON", value=["json"])
            with gr.Row():
                btsn = gr.Button("Retrieve File / Start")   
                
            def getValsList():
                return hostLogs.retrieverInfoList
            gr.DataFrame(value=getValsList, headers=hostLogs.retrieverHeaders, 
                        datatype=["str"] +["number"]*6, wrap=True, every=0.1)

            fileViewer = gr.File(visible=True,label="Progress Indicator")

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
            hostLogs.retrieverInfoList[0][0] =str(path+"\\"+file.orig_name)

            ret = RetrieverModule(tracker_path=file.name, network_passwd=networkPasswd)
            save_loc = ret.retrieve()
            return gr.File(label=f"Retrieved File: {save_loc}", value=save_loc)
        
        runEvent =btsn.click(fn=callFunc, inputs=[file, networkPassword],outputs=fileViewer)
        return senderBox, runEvent


def homePage():
    with gr.Box(visible= True) as homeBox:
        gr.Markdown('#### <center>Select a mode to continue</center>')
        with gr.Column(scale=8):
            with gr.Row():
                with gr.Column(scale=5, variant='panel'):
                    radio = gr.Radio(label="Modes", type="index",
                                choices=["Send/Store files", "Retrieve file", "Peer Mode"])
                    file = gr.File(interactive=True, label="Select File to Send or Tracker file to retrieve", visible=False)
                    jsonFile = gr.File(interactive=True, label="Select File to Send or Tracker file to retrieve", visible=False, file_types=['.json'])
                    
                with gr.Column(scale=5):
                    networkPassword = gr.Textbox(label="Enter Network Passphrase", placeholder='Network Passphrase')
                    
                    redundancyRatio = gr.Slider(minimum=1,step=1, maximum=10, value=2, label="Select a redundancy ratio", interactive=True, visible=False)
            startBtn = gr.Button(value="Continue", elem_id='homeBtn1', visible=False)
            startBtn.style(full_width=False)
            preview = gr.Image(visible=False)
            jsonPreview = gr.JSON(visible=False)

            def onRadioChange(radioIndex):
                if radioIndex == 0:
                    return [file.update(visible=True), jsonFile.update(visible=False), redundancyRatio.update(visible=True, label="Select a node_wise redundancy ratio"), startBtn.update(visible=True)]
                elif radioIndex == 1:
                    return [file.update(visible=False), jsonFile.update(visible=True), redundancyRatio.update(visible=False, label="Select a node_wise redundancy ratio"), startBtn.update(visible=True)]
                elif radioIndex == 2:
                    return [file.update(visible=False), jsonFile.update(visible=False), redundancyRatio.update(visible=True, label="Select a local redundancy ratio"), startBtn.update(visible=True)]
                else:
                    return [file.update(visible=False), jsonFile.update(visible=False), redundancyRatio.update(visible=False), startBtn.update(visible=False)]
                
            radio.change(onRadioChange, inputs=radio, outputs=[file, jsonFile, redundancyRatio, startBtn])


            def onFileChange(file, jsonFile):
                if file is not None and file.orig_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    return [preview.update(value=file.name,visible=True), jsonPreview.update(visible=False)]
                elif jsonFile is not None and jsonFile.orig_name.lower().endswith(('.json')):
                    with open(jsonFile.name, 'r') as openfile:
                        return [preview.update(visible=False), jsonPreview.update(value=json.load(openfile), visible=True)]
                else:
                    return [preview.update(visible=False), jsonPreview.update(visible=False)]
                
            file.change(onFileChange, inputs=[file,jsonFile], outputs=[preview, jsonPreview])
            jsonFile.change(onFileChange, inputs=[file,jsonFile], outputs=[preview, jsonPreview])
        return homeBox, radio, redundancyRatio, startBtn, file, jsonFile, networkPassword


with gr.Blocks(css='ui/main.css') as demo:
    # discovery = DiscoveryServiceInterface()
    with gr.Row():
        with gr.Column(scale=6,): 
            gr.Markdown("# Secure data storage and hiding")
        backBtn = gr.Button("Back", visible=False)
    
    homeBox, radio, redundancyRatio, startBtn, file, jsonFile, networkPassword = homePage()

    senderBox, runEvent = senderPage(redundancyRatio, networkPassword, file)
    retrievalBox, runEvent2 = retrievalPage(networkPassword, jsonFile)
    receiverBox = peerPage(redundancyRatio, networkPassword)

 

    def openPage(radio,jsonFile):
        if radio == 0:
            return [homeBox.update(visible=False), senderBox.update(visible=True), retrievalBox.update(visible=False), receiverBox.update(visible=False), backBtn.update(visible=True)]
        elif radio == 1:
            if jsonFile is not None and jsonFile.orig_name.lower().endswith(('.json')):
                return [homeBox.update(visible=False), senderBox.update(visible=False), retrievalBox.update(visible=True), receiverBox.update(visible=False), backBtn.update(visible=True)]
            else:
                return [homeBox, senderBox, retrievalBox, receiverBox, backBtn]
        elif radio == 2:
            return [homeBox.update(visible=False), senderBox.update(visible=False), retrievalBox.update(visible=False), receiverBox.update(visible=True), backBtn.update(visible=True)]

    startBtn.click(openPage, inputs=[radio, jsonFile] ,outputs=[homeBox, senderBox, retrievalBox, receiverBox, backBtn])

    def backBtnHandler(radio):
        printer = Printer()
        printer.flush()
        hostLogs = DataLogger()
        hostLogs.flush()
        return [homeBox.update(visible=True), senderBox.update(visible=False), retrievalBox.update(visible=False), receiverBox.update(visible=False), backBtn.update(visible=False)]
    
    backBtn.click(backBtnHandler, inputs=radio ,outputs=[homeBox, senderBox, retrievalBox, receiverBox, backBtn], cancels=[runEvent, runEvent2])

demo.queue()


if __name__ == '__main__':
    demo.launch()