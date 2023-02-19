from singleton_meta import SingletonMeta

class Printer(metaclass=SingletonMeta):
    html = '''
    <script>
        window.setInterval(function() {
        var elem = document.getElementById("style-2");
        elem.scrollTop = elem.scrollHeight;
        }, 2000);
    </script>
    <div style="height:10px;"></div>
    <div class=fakeMenu>
  <div class="fakeButtons fakeClose"></div>
  <div class="fakeButtons fakeMinimize"></div>
  <div class="fakeButtons fakeZoom"></div>
</div>
<div class="fakeScreen" id="style-2">
  '''

    htmlEnd = '''<p class="line4">><span class="cursor4">_</span></p>
        </div>'''

    def getHTML(self):
        return self.html + self.htmlEnd
    
    def write(self, name: str, msg: str):
        self.html += f"<p> <span class='line3'>Chunk-{name}: </span> <span class='line4'>{msg}</span></p>"