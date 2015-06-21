__author__ = 'U0124075'



from BeautifulSoup import BeautifulSoup
import urllib2
import re



class YouKu(object):

    name = ""
    siteId = 0
    videos = []
    available = False

    def __int__(self):
        super(self,YouKu).__init__()


    def getList(self, url):
        response = urllib2.urlopen(url)
        content = response.read()
        bs = BeautifulSoup(content)
        #linkpanels site14
        video_name = bs.find("li", attrs={"class":"base_name"})
        self.name = video_name.h1.getText()
        video_div = bs.find("div", {"class":"linkpanels site14"})
        video_ul = video_div.ul
        for video_li in video_ul.findAll("li"):
            video_name = video_li.a.getText()
            video_url = video_li.a['href']
            self.videos.append((video_name, video_url))

    def clean(self):
        self.videos = []




if __name__ == "__main__":
    pass
#    youku = YouKu()
#    print dir(youku)
#    youku.getList("http://www.soku.com/detail/show/XMTAzNjc5Ng==")
#    for item in youku.videos:
#        print item[1]


