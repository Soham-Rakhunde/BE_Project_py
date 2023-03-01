import json
import gradio as gr


def homePage():
    with gr.Box(visible=False) as homeBox:
        gr.Markdown('#### <center>Select a mode to continue</center>')
        with gr.Column(scale=8):
            with gr.Row():
                with gr.Column(scale=5, variant='panel'):
                    radio = gr.Radio(label="Modes", type="index",
                                     choices=["Send/Store files", "Retrieve file", "Peer Mode"])
                    file = gr.File(
                        interactive=True, label="Select File to Send or Tracker file to retrieve", visible=False)
                    jsonFile = gr.File(
                        interactive=True, label="Select File to Send or Tracker file to retrieve", visible=False, file_types=['.json'])

                with gr.Column(scale=5):
                    networkPassword = gr.Textbox(
                        label="Enter Network Passphrase", placeholder='Network Passphrase')

                    redundancyRatio = gr.Slider(minimum=1, step=1, maximum=10, value=2,
                                                label="Select a redundancy ratio", interactive=True, visible=False)
            startBtn = gr.Button(
                value="Continue", elem_id='homeBtn1', visible=False)
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

            radio.change(onRadioChange, inputs=radio, outputs=[
                         file, jsonFile, redundancyRatio, startBtn])

            def onFileChange(file, jsonFile):
                if file is not None and file.orig_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    return [preview.update(value=file.name, visible=True), jsonPreview.update(visible=False)]
                elif jsonFile is not None and jsonFile.orig_name.lower().endswith(('.json')):
                    with open(jsonFile.name, 'r') as openfile:
                        return [preview.update(visible=False), jsonPreview.update(value=json.load(openfile), visible=True)]
                else:
                    return [preview.update(visible=False), jsonPreview.update(visible=False)]

            file.change(onFileChange, inputs=[
                        file, jsonFile], outputs=[preview, jsonPreview])
            jsonFile.change(onFileChange, inputs=[
                            file, jsonFile], outputs=[preview, jsonPreview])
        return homeBox, radio, redundancyRatio, startBtn, file, jsonFile, networkPassword
