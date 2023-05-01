import gradio as gr
from peer_discovery.discoveryServiceInterface import DiscoveryServiceInterface
from services.key_handling_module import KeyHandlerUI

from ui.dataAccumlator import DataLogger
from ui.printer import Printer

from ui.pages.homePage import homePage
from ui.pages.peerPage import peerPage
from ui.pages.retreiverPage import retrievalPage
from ui.pages.senderPage import senderPage


with gr.Blocks(css='ui/main.css') as demo:
    DiscoveryServiceInterface()
    with gr.Row():
        with gr.Column(scale=6,):
            gr.Markdown("# Secure data storage and hiding (Group 74)")
        backBtn = gr.Button("Back", visible=False)

    homeBox, radio, redundancyRatio, startBtn, file, jsonFile, networkPassword = homePage()
    keyHandler = KeyHandlerUI()

    with gr.Box() as passwordBox:
        if keyHandler.is_password_created():
            password = gr.Textbox(
                label="Keystore Passphrase", placeholder='Enter keystore Passphrase')
            btn = gr.Button(value="Submit")
            btn.style(full_width=False)

            def retrieve_key(passwd):
                keyHandler.retrieve(password=passwd)
                return [passwordBox.update(visible=False), homeBox.update(visible=True)]

            btn.click(retrieve_key, inputs=password,
                      outputs=[passwordBox, homeBox])
        else:
            with gr.Row():
                password = gr.Textbox(
                    label="Keystore Passphrase", placeholder='Enter new Passphrase')
                confirmPassword = gr.Textbox(
                    label="Confirm Passphrase", placeholder='Confirm the Passphrase', type='password')
            btn = gr.Button(value="Confirm", visible=False)
            btn.style(full_width=False)

            def password_validation(passwd, passwd2):
                if len(passwd) > 0 and passwd == passwd2:
                    return btn.update(visible=True)
                else:
                    return btn.update(visible=False)

            password.change(password_validation, inputs=[
                            password, confirmPassword], outputs=btn)
            confirmPassword.change(password_validation, inputs=[
                                   password, confirmPassword], outputs=btn)

            def new_key_generate(passwd):
                keyHandler.generateKey(password=passwd)
                # keyHandler.save()

                return [passwordBox.update(visible=False), homeBox.update(visible=True)]

            btn.click(new_key_generate, inputs=password,
                      outputs=[passwordBox, homeBox])

    senderBox, runEvent = senderPage(redundancyRatio, networkPassword, file)
    retrievalBox, runEvent2 = retrievalPage(networkPassword, jsonFile)
    receiverBox = peerPage(redundancyRatio, networkPassword)

    def openPage(radio, jsonFile):
        if radio == 0:
            return [homeBox.update(visible=False), senderBox.update(visible=True), retrievalBox.update(visible=False), receiverBox.update(visible=False), backBtn.update(visible=True)]
        elif radio == 1:
            if jsonFile is not None and jsonFile.orig_name.lower().endswith(('.json')):
                return [homeBox.update(visible=False), senderBox.update(visible=False), retrievalBox.update(visible=True), receiverBox.update(visible=False), backBtn.update(visible=True)]
            else:
                return [homeBox, senderBox, retrievalBox, receiverBox, backBtn]
        elif radio == 2:
            return [homeBox.update(visible=False), senderBox.update(visible=False), retrievalBox.update(visible=False), receiverBox.update(visible=True), backBtn.update(visible=True)]

    startBtn.click(openPage, inputs=[radio, jsonFile], outputs=[
                   homeBox, senderBox, retrievalBox, receiverBox, backBtn])

    def backBtnHandler():
        printer = Printer()
        printer.flush()
        hostLogs = DataLogger()
        hostLogs.flush()
        return [homeBox.update(visible=True), senderBox.update(visible=False), retrievalBox.update(visible=False), receiverBox.update(visible=False), backBtn.update(visible=False)]

    backBtn.click(backBtnHandler, outputs=[
                  homeBox, senderBox, retrievalBox, receiverBox, backBtn], cancels=[runEvent, runEvent2])

demo.queue()

if __name__ == '__main__':
    demo.launch()