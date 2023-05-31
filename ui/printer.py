from utils.singleton_meta import SingletonMeta

class Printer(metaclass=SingletonMeta):
    html = '''
    <div style="height:10px;"></div>
    <div class=fakeMenu>
  <div class="fakeButtons fakeClose"></div>
  <div class="fakeButtons fakeMinimize"></div>
  <div class="fakeButtons fakeZoom"></div>
</div>
<div class="fakeScreen" id="style-2">
  '''
    
    logs = dict()

    htmlEnd = '''<p class="line4">><span class="cursor4">_</span></p>
        </div>'''
    
    def flush(self):
        self.logs = dict()

    def getHTML(self, log_name: str = "common"):
        if log_name not in self.logs:
          self.logs[log_name] = ""
        return self.html + self.logs[log_name] + self.htmlEnd

    def write(self, name: str, msg: str, log_name: str = "common"):
        if log_name not in self.logs:
          self.logs[log_name] = ""
        self.logs[log_name] += f"<p> <span class='line1'>{name}: </span> <span class='line4'>{msg}</span></p>"
