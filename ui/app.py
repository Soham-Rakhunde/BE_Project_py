import time
import gradio as gr

from printer import Printer


# demo.launch()
def wer_help():
    p = Printer()
    for i in range(15):
        p.write(name=f"{i%4 +1}", msg=str(i))
        time.sleep(0.4)


pr = Printer()
with gr.Blocks(css='main.css') as demo:
    gr.HTML(value=pr.getHTML, label="Terminal", every = 1)
    # btn = gr.Button("show output")
    # btn.click(fn=pr.eventLoop, outputs=out)
    btsn = gr.Button("Run")
    btsn.click(fn=wer_help)
demo.queue()


if __name__ == '__main__':
    demo.launch()