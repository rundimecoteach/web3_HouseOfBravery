import os
import signal

import requests
from bs4 import BeautifulSoup
import justext
from boilerpipe.extract import Extractor

def main():
    killer = GracefulKiller()
    
    dir = "./data/html"
    print(os.listdir(dir))
    nb_files = len([name for name in os.listdir(dir) if os.path.isfile(name)])
    print(nb_files)
    parserArray = [
        JTParser("./ex1/JT"),
        BPParser("./ex1/BP"),
        BSParser("./ex1/BS")
    ]
    i = 0
    for file in os.listdir(dir):
        if killer.kill_now:
            break
        if not os.path.isdir(os.path.join(dir, file)):
            i+=1
            os.system('clear')
            print('Calcul en cours : {}%'.format(i/nb_files))
            for parseObj in parserArray:
                parseObj.parse(os.path.join(dir, file))
    
    print('\n')
    for parseObj in parserArray:
        inputNbLines, inputNbLinesMoy, inputNbChar, inputNbCharMoy, outputNbLines, outputNbLinesMoy, outputNbChar, outputNbCharMoy = parseObj.stats()
        print(parseObj.dir)
        print('inputNbLines: {}/{}, inputNbChar: {}/{}, outputNbLines: {}/{}, outputNbChar: {}/{}'.format(inputNbLines, inputNbLinesMoy, inputNbChar, inputNbCharMoy, outputNbLines, outputNbLinesMoy, outputNbChar, outputNbCharMoy))

class Parser:
    def __init__(self, dir):
        self.dir = dir

    def parse(self, url):
        raise NotImplementedError( "Should have implemented this" )
    def output(self, url, output):
        (path, filename) = os.path.split(url)
        outfilename = os.path.join(self.dir, filename)
        with open(outfilename,"w+") as file:
            if output != '':
                file.write(output)
                file.close()
                self.outputs.append((url,outfilename))
    
    def stats(self):
        totalInputLines = 0
        totalOutputLines = 0
        totalInputChar = 0
        totalOutputChar = 0
        for (input, output) in self.outputs:
            try:
                content = ''
                tmp = 0
                with open(input,"r") as infile:
                    for i, l in enumerate(infile):
                        content+= l
                        tmp = i
                    totalInputLines += tmp
                    totalInputChar += len(content)
                content = ''
                with open(output,"r") as outfile:
                    for i, l in enumerate(outfile):
                        content+= l
                        tmp = i
                    totalOutputLines += tmp;
                    totalOutputChar += len(content);
            except:
                pass
        return totalInputLines, totalInputLines/len(self.outputs), totalInputChar, totalInputChar/len(self.outputs), totalOutputLines, totalOutputLines/len(self.outputs), totalOutputChar, totalOutputChar/len(self.outputs)

class JTParser(Parser):
    outputs = []
    def __init__(self, dir):
        super().__init__(dir)

    def parse(self, url):
        with open(url, "r") as file:
            try:
                input = file.read()
                output = ''
                paragraphs = justext.justext(input, justext.get_stoplist('English'))
                for paragraph in paragraphs:
                    if paragraph.is_boilerplate:
                        if '<p>' in paragraph.text:
                            output+= paragraph.text
                        else: output+= '<p>'+paragraph.text+'</p>\n'
                self.output(url, output)
            except:
                pass 
            file.close()

class BPParser(Parser):
    outputs = []
    def __init__(self, dir):
        super().__init__(dir)

    def parse(self, url):
        os.rename(os.path.abspath(url), os.path.abspath(url)+'.html')
        try:
            extractor = Extractor(extractor='ArticleExtractor', url='file://'+os.path.abspath(url)+'.html')
            output = '';
            for paragraph in extractor.getText().split('\n'):
                if '<p>' in paragraph:
                    output += paragraph+'\n'
                else: output += '<p>'+paragraph+'</p>\n'
            self.output(url, output)
        except:
            pass
        finally:
            os.rename(os.path.abspath(url)+'.html', os.path.abspath(url))

class BSParser(Parser):
    outputs = []
    def __init__(self, dir):
        super().__init__(dir)

    def parse(self, url):
        with open(url, "r") as file:
            try:
                input = file.read()
                soup = BeautifulSoup(input, 'html.parser')
                output = ''
                for paragraph in soup.find('p').get_text():
                    if '<p>' in paragraph:
                        output += paragraph
                    else: output += '<p>'+paragraph+'</p>\n'
                self.output(url, output)
            except:
                pass
            file.close()

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self,signum, frame):
    self.kill_now = True

if __name__ == '__main__':
    main()
