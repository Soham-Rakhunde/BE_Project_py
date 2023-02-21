import time
import gradio as gr

from printer import Printer
from key_handling_module import KeyHandlerUI

def wer_help():
    p = Printer()
    for i in range(15):
        p.write(name=f"{i%4 +1}", msg=str(i))
        time.sleep(0.4)


def terminalUI():
    gr.HTML(value=pr.getHTML, label="Terminal", every = 1)
    btsn = gr.Button("Run")
    btsn.click(fn=wer_help)


def mainTabs():
    with gr.Box(visible= False) as tabBox:
        with gr.Tabs():
            pass
    return tabBox

pr = Printer()
def passwordPage():
    keyHandler = KeyHandlerUI()

    tabBox = mainTabs()
    if keyHandler.is_password_created():
        password = gr.Textbox(label="Keystore Passphrase", placeholder='Enter keystore Passphrase')
        btn = gr.Button(value="Submit")
        btn.style(full_width=False)

        def retrieve_key(passwd):
            keyHandler.retrieve(password=passwd)
            return [btn.update(visible=False), password.update(visible=False), tabBox.update(visible=True)]

        btn.click(retrieve_key, inputs=password, outputs=[btn, password, tabBox])
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
            return [password.update(visible=False), confirmPassword.update(visible=False), btn.update(visible=False), tabBox.update(visible=True)]

        btn.click(password_generate, inputs= password, outputs=[password, confirmPassword, btn, tabBox])

        


# def main_tabs():
#     with gr.Box(visible= False):

with gr.Blocks(css='main.css') as demo:
    gr.Markdown(
    """
    # Secure data storage and hiding
    """)
    # passwordPage()
    mainTabs()
    # terminalUI()

# demo.queue()


demo.queue()


if __name__ == '__main__':
    demo.launch()