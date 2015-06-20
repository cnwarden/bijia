__author__ = 'U0124075'



from BeautifulSoup import BeautifulSoup
import urllib2



class YouKu(object):

    name = ""
    videos = []

    def __int__(self):
        super(self,YouKu).__init__()

    def getList(self, url):
        response = urllib2.urlopen(url)
        content = response.read()
        bs = BeautifulSoup(content)
        video_name = bs.find("li", attrs={"class":"base_name"})
        self.name = video_name.h1.getText()
        video_ul = bs.find("ul", attrs={"class":"linkpanel"})
        for video_li in video_ul.findAll("li"):
            video_name = video_li.a.getText()
            video_url = video_li.a['href']
            self.videos.append((video_name, video_url))




if __name__ == "__main__":
    youku = YouKu()
    print dir(youku)
    youku.getList("http://www.soku.com/detail/show/XMTE2MDAzMg==?siteId=14")
    for item in youku.videos:
        print item[1]


