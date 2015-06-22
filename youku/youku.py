__author__ = 'U0124075'



from BeautifulSoup import BeautifulSoup
import urllib2
import re



class YouKu(object):

    def __int__(self):
        super(self,YouKu).__init__()
        self.url = None
        self.name = None
        self.videos = None


    def getList(self, url):
        self.url = url
        m = re.search("siteId=14$", self.url)
        if m:
            pass
        else:
            self.url = "%s?siteId=14" % (self.url)

        response = urllib2.urlopen(self.url)
        content = response.read()
        bs = BeautifulSoup(content)
        #linkpanels site14
        video_name = bs.find("li", attrs={"class":"base_name"})
        self.name = video_name.h1.getText()
        video_div = bs.find("div", {"class":"linkpanels site14"})
        video_ul = video_div.ul
        self.videos = []
        for video_li in video_ul.findAll("li"):
            video_name = video_li.a.getText()
            video_url = video_li.a['href']
            if video_name and video_url:
                self.videos.append((video_name, video_url))


if __name__ == '__main__':
    youku = YouKu()
    youku.getList("http://www.soku.com/detail/show/XMTAzNjc5Ng==")
    for item in youku.videos:
        print item[1]


