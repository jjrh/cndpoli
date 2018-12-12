import json
import re
import datetime
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as bs

from lib import util
from lib import vt100_colors

# because I forget this:
# import pdb; pdb.set_trace()
# import bpdb; bpdb.set_trace()

vt100=vt100_colors.colors
class nocolors(vt100_colors.colors):
    """
    Silly hack to to override the colorize function
    that is defined with a global variable vt100=colors
    This lets us do:
        vt100=nocolors
    if we don't want to output colors.
    """
    def colorize(s,*props):
        return s

class video_item:
    def __init__(self,tag):
        self.title = None
        self.title_alt = None

        self.start_time = None
        self.end_time = None
        self.cpac_url = None

        self.live = None

        self.m3u8_url = None
        self.m3u8_json = None
        self.video_attrs = None
        self.init_from_tag(tag)


    def init_from_tag(self,tag):
        self.title = tag.attrs['data-title']
        self.title_alt =tag.select("a.video-block__catlink")[0].text

        self.start_time = util.unix_to_datetime(tag['data-start_time'])
        self.end_time = util.unix_to_datetime(tag['data-end_time'])
        self.cpac_url = tag.select('a.video-block__titlelink')[0].attrs['href']

        self.live = self.is_live()

    def init_from_dict(self,din):
        self.title = din.get('title')
        self.title_alt = din.get('title_alt')

        self.start_time = din.get('start_time').strptime(s,"%Y-%m-%dT%H:%M:%S")
        self.end_time = din.get('end_time').strptime(s,"%Y-%m-%dT%H:%M:%S")
        self.cpac_url = din.get('cpac_url')
        self.live = din.get('live')

        self.m3u8_url = din.get('m3u8_url')
        self.m3u8_json = din.get('m3u8_json')
        self.video_attrs = din.get('video_attrs')



    def is_live(self):
        """ True if stream is live """
        now = datetime.datetime.now()
        return (self.start_time < now) and (self.end_time > now)

    def is_over(self):
        now = datetime.datetime.now()
        return (now > self.start_time) and (now > self.end_time)
    def get_m3u8(self):
        """
        Process to get a m3u8 stream link is as follows:
        self.load_video_url()
          Visit a video's page for example:
                  http://www.cpac.ca/en/direct/cpac2/224861/fisheries-minister-makes-announcement-on-aquaculture-industry/
          Grab the video dom element which gives us:
              'acct'      : attrs['data-account'],
              'video_id'  : attrs['data-video-id'],
              'player_id' : attrs['data-player']

        Next, get policykey with self.get_policy_key(attrs)
              add policy_key to attrs
        Use get_video_stream_url(attrs) to make the request to get the json data which contains the m3u8 url

        ----

        we then set: self.video_attrs, self.m3u8_json, and self.m3u8_url
        Only thing we really need is the m3u8_url, but the other info may be useful
        down the road.

        Haven't looked to see if policy_key is consistant or if it varies per video or per day.
        May only need to do it once.

        """
        if self.is_live() and self.m3u8_url == None:
            attrs = self.load_video_url()
            if(attrs == None): # sometimes it says it's live but it's really not
                return

            attrs['policy_key'] = self.get_policy_key(attrs)
            self.video_attrs = attrs

            m3u8_json = self.get_video_stream_url(attrs)
            self.m3u8_json = m3u8_json
            self.m3u8_url = self.m3u8_json['sources'][0]['src']

    def load_video_url(self):
        contents = urlopen(self.cpac_url).read()
        soup=bs(contents,features="lxml")
        videos = soup.findAll('video')
        attrs = None
        if len(videos) == 1:
            video = videos[0]
            attrs = video.attrs
        if attrs == None:
            return None

        return {
            'acct'      : attrs['data-account'],
            'video_id'  : attrs['data-video-id'],
            'player_id' : attrs['data-player']
            }

    def get_policy_key(self,attrs):
        """
        Get the policy key for the video.
        attrs = { 'acct'      : ...
                  'video_id'  : ...
                  'player_id' : ...
                }

        Get attrs from self.load_video_url()
        Returns policy_key

        Policy key is tucked away in the a minified javascript file,
        we grab the file and use a crappy regex to yank it out.
        """
        contents = urlopen("http://players.brightcove.net/%s/%s_default/index.min.js" % (attrs['acct'],attrs['player_id'])).read().decode('utf-8')
        m = re.search('(policyKey:\".*"\}\);)', contents) # crummy rexex
        policy_key = m.group(0).split('"')[1] # compensation for crummy regex
        return policy_key

    def get_video_stream_url(self,attrs):
        """
        get the json response with the m3u8 stream information
        We need a policy key to access the api - see self.get_policy_key(attrs)


        attrs = { 'acct'      : ...
                  'video_id'  : ...
                  'player_id' : ...
                  'policy_key': ...
                }

        Use self.load_video_url() for 'acct','video_id','player_id'
            self.get_policy_key(attrs) for 'policy_key'


        ------------

        Example JSON returned.

        Replaced for brevity
        -------------------------------
        ACCTID/PUBID  1242843915001
        VIDID         5027924874001

          "description": null,
          "poster_sources": [
            {
              "src": "http://f1.media.brightcove.com/8/$ACCTID/$ACCTID_5822499218001_$VIDID-vs.jpg?pubId=$ACCTID&videoId=$VIDID"
            },
            {
              "src": "https://f1.media.brightcove.com/8/$ACCTID/$ACCTID_5822499218001_$VIDID-vs.jpg?pubId=$ACCTID&videoId=$VIDID"
            }
          ],
          "tags": [],
          "cue_points": [],
          "custom_fields": {},
          "account_id": "$ACCTID",
          "sources": [
            {
              "type": "application/vnd.apple.mpegurl",
              "src": "https://bcoveliveios-i.akamaihd.net/hls/live/248519/$ACCTID_1/master.m3u8",
              "asset_id": "5027944997001"
            }
          ],
          "name": "CPAC 1 English 2016 HLS",
          "reference_id": "cpac1-english-2016-hls",
          "long_description": null,
          "duration": 0,
          "economics": "FREE",
          "published_at": "2016-07-08T16:52:35.950Z",
          "text_tracks": [],
          "updated_at": "2018-10-31T18:48:41.513Z",
          "thumbnail": "http://f1.media.brightcove.com/8/$ACCTID/$ACCTID_5822499215001_$VIDID-th.jpg?pubId=$ACCTID&videoId=$VIDID",
          "poster": "http://f1.media.brightcove.com/8/$ACCTID/$ACCTID_5822499218001_$VIDID-vs.jpg?pubId=$ACCTID&videoId=$VIDID",
          "offline_enabled": false,
          "link": null,
          "id": "$VIDID",
          "ad_keys": null,
          "thumbnail_sources": [
            {
              "src": "http://f1.media.brightcove.com/8/$ACCTID/$ACCTID_5822499215001_$VIDID-th.jpg?pubId=$ACCTID&videoId=$VIDID"
            },
            {
              "src": "https://f1.media.brightcove.com/8/$ACCTID/$ACCTID_5822499215001_$VIDID-th.jpg?pubId=$ACCTID&videoId=$VIDID"
            }
          ],
          "created_at": "2016-07-08T16:52:35.950Z"
        }
        """
        url = "https://edge.api.brightcove.com/playback/v1/accounts/%s/videos/%s" % (attrs['acct'],attrs['video_id'])
        q = Request(url)
        q.add_header('Accept',"application/json;pk=%s" % attrs['policy_key'])
        out = urlopen(q).read()
        return json.loads(out)

    def pretty_print(self):
        if(self.is_live()):
            if(self.m3u8_url == None):
                LIVE=vt100.colorize("LIVE ",vt100.FG_LIGHT_GRAY)
            else:
                LIVE=vt100.colorize("LIVE ",vt100.FG_RED)
        else:
            LIVE=vt100.colorize("%s"%util.time_from_now(self.start_time).format("%H:%M"),vt100.FG_WHITE)
        print("%s [%s - %s] %s:%s" % (LIVE,
                                      self.start_time.strftime("%H:%M"),
                                      self.end_time.strftime("%H:%M"),
                                      vt100.colorize(self.title_alt,vt100.BOLD),
                                      vt100.colorize(self.title,vt100.FG_WHITE),
                                    ))
        if(self.m3u8_url or self.is_live()):
            padding = "                      "
            print("%s%s" % (padding,self.m3u8_url))
            print("")

    def toJSON(self,**kwargs):
        """
        return this as a json object - most likely for writing to a file log
        """
        return json.dumps(self.__dict__(), **kwargs)

    def __dict__(self):
        return {
            'title'        : self.title,
            'title_alt'    : self.title_alt,
            'start_time'   : self.start_time.isoformat(),
            'end_time'     : self.end_time.isoformat(),
            'cpac_url'     : self.cpac_url,
            'live'         : self.live,
            'm3u8_url'     : self.m3u8_url,
            'm3u8_json'    : self.m3u8_json,
            'video_attrs'  : self.video_attrs
            }

    def __eq__(self,art):
        return (
            (self.title == art.title) and
            (self.cpac_url == art.cpac_url)
            )

    def __str__(self):
        return "%s:%s,[ %s - %s ] %s" % (self.title_alt,self.title,self.start_time,self.end_time,self.cpac_url)


CPAC_HEADER_URL="http://www.cpac.ca/api/header_nav/en-US/"
class cpac:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.noresolve = False
        if(kwargs):
            if(kwargs.get('usecolors') == False):
                # if we don't want to use colors we reassign the global vt100 to a overrided class
                global vt100
                vt100 = nocolors
            if(kwargs.get('noresolve') == True):
                self.noresolve = True

        self.videos = []


    def load_header(self):
        contents = json.loads(urlopen(CPAC_HEADER_URL).read())
        header_soup = bs(contents['data']['html2'], features="lxml")

        articles = header_soup.findAll('article')
        for art in articles:
            v = video_item(art)
            if not v in self.videos:
                self.videos.append(v)

    def update(self):
        remove_list = []
        for v in self.videos:
            if(not self.noresolve):
                v.get_m3u8() # only updates if it's live and hasn't already happened
            if(v.is_over()):
                remove_list.append(v)
        for v in remove_list:
            # print("---- removing: %s" % v)
            self.videos.remove(v)


    def live(self):
        vids = []
        for v in self.videos:
            if v.is_live():
                vids.append(v)
        return vids

    def not_live(self):
        vids = []
        for v in self.videos:
            if not v.is_live():
                vids.append(v)
        return vids
    def toJSON(self,**kwargs):
        """
        return this as a json object - most likely for writing to a file log
        """

        videos_json = []
        for v in self.videos:
            videos_json.append(v.__dict__())
        jout = {
            'args' : self.kwargs,
            'videos' : videos_json
            }
        return json.dumps(jout, **kwargs)

    def __dict__(self):
        return { 'videos' : self.videos }

    def __getitem__(self,k):
        return self.videos[k]

    def __delitem__(self,k):
        del self.videos[k]

    def __len__(self):
        return len(self.videos)
