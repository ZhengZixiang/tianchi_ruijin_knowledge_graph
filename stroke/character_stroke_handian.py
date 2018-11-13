# -*- conding:utf-8 -*-
from stroke.handian import Handian
import urllib.request as urllib2
import urllib
from bs4 import BeautifulSoup

# solve encoding
from imp import reload
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


class Stroke(object):
    dictionary_stroke_filepath = "./stroke/default_stroke.txt"
    dictionary_wubi_filepath = "./stroke/default_wubi.txt"
    dictionary_cangjie_filepath = "./stroke/default_cangjie.txt"
    dictionary_zheng_filepath = "./stroke/default_zheng.txt"
    dictionary_sijiao_filepath = "./stroke/default_sijiao.txt"
    handian_url = None

    def __init__(self):
        self.dictionary = {}
        self.dictionary_stroke = {}
        self.dictionary_wubi = {}
        self.dictionary_cangjie = {}
        self.dictionary_zheng = {}
        self.dictionary_sijiao = {}
        self.read_dictionary()
        self.handian = Handian()

    def read_dictionary(self):
        with open(self.dictionary_stroke_filepath, encoding="UTF-8") as f:
            for line in f:
                line = line.strip("\n")
                line = line.split(" ")
                self.dictionary_stroke[line[0]] = line[1:]
        f.close()
        with open(self.dictionary_wubi_filepath, encoding="UTF-8") as f:
            for line in f:
                line = line.strip("\n")
                line = line.split(" ")
                self.dictionary_wubi[line[0]] = line[1:]
        f.close()
        with open(self.dictionary_cangjie_filepath, encoding="UTF-8") as f:
            for line in f:
                line = line.strip("\n")
                line = line.split(" ")
                self.dictionary_cangjie[line[0]] = line[1:]
        f.close()
        with open(self.dictionary_zheng_filepath, encoding="UTF-8") as f:
            for line in f:
                line = line.strip("\n")
                line = line.split(" ")
                self.dictionary_zheng[line[0]] = line[1:]
        f.close()
        with open(self.dictionary_sijiao_filepath, encoding="UTF-8") as f:
            for line in f:
                line = line.strip("\n")
                line = line.split(" ")
                self.dictionary_sijiao[line[0]] = line[1:]
        f.close()

    def write_dictionary(self, word, char_info, kind):
        with open(getattr(self, 'dictionary_'+kind +'_filepath'), 'a', encoding='UTF-8') as f:
            f.write(word + ' ' + ' '.join(char_info) + '\n')
        f.close()

    def get_info(self, word, kind):
        self.dictionary = getattr(self, 'dictionary_' + kind)
        if word in self.dictionary:
            return self.dictionary[word]
        else:
            # print("From handian:    word {}".format(word), end=" ")
            self.handian_url = self.handian.get_url(word=word)
            word_utf = word
            word = hex((ord(word)))[2:]
            word = urllib.parse.quote(word)
            return self.get_info_from_handian(word_utf, kind)

    def get_info_from_handian(self, word, kind):
        url = self.handian_url
        # print("url", url)
        if url == "http://www.zdic.net/sousuo/":
            return None

        html = self.post_baidu(url)
        if html is None:
            return None
        char_info = self.anlysis_info_from_html(html, kind)
        if char_info is not None:
            self.dictionary[word] = char_info
            self.write_dictionary(word, char_info, kind)
        return char_info

    def anlysis_info_from_html(self, html_doc, kind):
        soup = BeautifulSoup(html_doc, 'html.parser')
        l = []
        if kind == 'stroke':
            zh_stoke = soup.find(id="z_i_t2_bis")
            contents = zh_stoke.contents
        elif kind == 'wubi':
            encoding = soup.find_all(attrs={'class': 'diczx7'})
            contents = encoding[0].contents
        elif kind == 'cangjie':
            encoding = soup.find_all(attrs={'class': 'diczx7'})
            contents = encoding[1].contents
        elif kind == 'zheng':
            encoding = soup.find_all(attrs={'class': 'diczx7'})
            if len(encoding) == 3:
                contents = encoding[2].contents
            else:
                return None
        elif kind == 'sijiao':
            encoding = soup.find_all(attrs={'class': 'diczx6'})
            contents = encoding[0].contents
        else:
            return None
        for st in contents[0]:
            l.append(st)
        return l

    def post_baidu(self, url):
        try:
            timeout = 10
            # request = urllib2.Request(url)
            request = urllib2.Request(url)
            request.add_header('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36')
            request.add_header('connection','keep-alive')
            request.add_header('referer', url)
            response = urllib2.urlopen(request, timeout=timeout)
            html = response.read()
            response.close()
            return html
        except Exception as e:
            print('URL Request Error:', e)
            return None


if __name__ == "__main__":
    print("extract character stoke from [http://www.zdic.net/]")

    stroke = Stroke()
    print("中", stroke.get_info("中", 'stoke'))
    print("王", stroke.get_info("王", 'wubi'))
    print("吋", stroke.get_info("吋", 'cangjie'))
    print("緉", stroke.get_info("緉", 'zheng'))
    print("知", stroke.get_info("緉", 'sijiao'))
    print("。", stroke.get_info("。", 'sijiao'))





