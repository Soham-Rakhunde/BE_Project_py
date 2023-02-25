import time
import gradio as gr
# from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from services.network_services.peerTLSInterface import PeerTLSInterface

from ui.printer import Printer
from services.key_handling_module import KeyHandlerUI




pr = Printer()
visibleBox = None
invisibleBox = None



def terminalUI(callFunc):
    progressBar = gr.Markdown(value="")
    gr.HTML(value=pr.getHTML, label="Terminal", every = 1)
    btsn = gr.Button("Run")
    btsn.click(fn=callFunc, inputs=progressBar,outputs=progressBar)


def upload_file(files):
    file_paths = [file.name for file in files]
    print(file_paths)
    print(files.name)
    return files.name

def homePage():
    with gr.Box(visible= True) as box:
        with gr.Row():
            with gr.Column(scale=8):
                file_output = gr.File()
                uploadButton = gr.UploadButton(value="Browse Files to Send or Tracker file to retrieve")
                uploadButton.upload(upload_file, uploadButton, file_output)
            with gr.Column(scale=6, variant='panel'):
                gr.Markdown('## <center>Menu Options</center>')
                sendBtn = gr.Button(value="Send", elem_id='homeBtn1')
                retrBtn = gr.Button(value="Retrieve", elem_id='homeBtn2')
                recvBtn = gr.Button(value="Receiver Mode", elem_id='homeBtn3')
            
    return box


def receiverBox():
    # DiscoveryServiceInterface()
    peerInterface = PeerTLSInterface(remoteAddress = '192.168.0.103', localPort= 11111)

    with gr.Box() as tabBox:
        gr.Markdown("### <center> Receiver Mode </center>")    
        gr.DataFrame(headers=peerInterface.getHeaders, value=peerInterface.getRowValues, datatype=["str"]*5, wrap=True, every=1)
        

        def callFunc(progressBar, progress=gr.Progress(track_tqdm=True)):
            peerInterface.progress = progress
            peerInterface.connectToRemoteClient(keypasswd='G00dP@ssw0rd', hostpassword ='P@ssw0rd',remotepassword ='P@ssw0rd')
            return progressBar.update(value="<center> # Sucessfully Completed </center>")
        
        terminalUI(callFunc=callFunc)
    
    return tabBox




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

        


# def main_tabs():
#     with gr.Box(visible= False):


def backBtnHandler():
    if visibleBox != None and invisibleBox != None:
        visibleBox, invisibleBox = invisibleBox, visibleBox
        return [visibleBox.update(visible=True), invisibleBox.update(visible=False)]
    else:
        return [visibleBox, invisibleBox]

def receiverPage(progress= gr.Progress(track_tqdm=True)):
    with gr.Box():
        receiverBox()
        terminalUI()


with gr.Blocks(css='ui/main.css') as demo:
    # discovery = DiscoveryServiceInterface()
    with gr.Row():
        with gr.Column(scale=6,): 
            gr.Markdown("# Secure data storage and hiding")
        backBtn = gr.Button("Back")
        # backBtn.click(backBtnHandler, outputs= [visibleBox, invisibleBox])
    # passwordPage()
    receiverBox()
    # homePage()


demo.queue()


if __name__ == '__main__':
    demo.launch()