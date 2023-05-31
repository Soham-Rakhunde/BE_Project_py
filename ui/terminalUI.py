import gradio as gr
from ui.printer import Printer


def terminalUI(log_name: str = None):
    pr = Printer()
    if log_name == None:
        term = gr.HTML(value=pr.getHTML, label="Terminal", every=1)
    else:
        def callSpecialLogs():
            return pr.getHTML(log_name=log_name)
        term = gr.HTML(value=callSpecialLogs, label="Terminal", every=1)
    return term
