# coding:utf-8

from django.shortcuts import render
from django.http import HttpResponse,Http404
from bs4 import BeautifulSoup
import requests,json,time,execjs,pymongo,urllib,re
from django.contrib.auth.decorators import login_required
from .models import translate as Translate
import sqlite3,jieba
from pyecharts import Line,Pie,WordCloud


# Create your views here.

# @login_required(login_url = "/account/new-login/")
def translate(request):
    if request.method == "GET":
        # print("here")
        Real_ip = request.META['REMOTE_ADDR']
        if Real_ip in IP_whitelist:
            minute = int(time.strftime("%M"))
            return render(request,"mytest/translate.html",{"context_show":True if Real_ip in ["10.9.232.75","10.9.224.66"] else False,"motto":motto[minute if minute <= len(motto) else minute%10 ],"love":love,"cathy":cathy})
        else:
            raise Http404("The page you visited does not exist!") 
    if request.method == "POST":
        # tran_coll = Mongo_conn("test_Berg","translate")
        type_ = request.POST['type']
        #print(request.META['REMOTE_ADDR'])
        if type_ == 'translate':
            text = request.POST['text']
            tk = Get_TK()
            url = buildUrl(text,tk.getTk(text))      
            r=requests.get(url,proxies = proxy)
            result=json.loads(r.text)
            try:
                Real_ip = request.META['REMOTE_ADDR']
                # t = re.sub(ur'[^0-9a-zA-Z\u4e00-\u9fa5]',"",text)
                if  not Translate.objects.filter(word=text):
                    Translate.objects.create(word=text,translate=result[0][0][0],ip=Real_ip)
                    # print(t)
                    # tran_coll.insert_one({
                    #         "word":text,
                    #         "translate":result[0][0][0],
                    #         "from":Real_ip
                    #     })
            except:
                pass
            return HttpResponse(json.dumps({"result":result}))
        if type_ == 'story':
            text = request.POST['text']
            index = motto.index(text)
            # print(request.POST['to'])
            if request.POST['to'] == 'next':
                return HttpResponse(json.dumps({"result":motto[0 if index == 18 else index + 1]}))
            if request.POST['to'] == 'last':               
                return HttpResponse(json.dumps({"result":motto[18 if index == 0 else index - 1]}))


def translate_char(requests):
    context = ""
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    if requests.POST["type"] == "Line":
        str_sql = "select date(updated) as d ,count(*) as c from Mytest_translate group by d"
        cursor = c.execute(str_sql)
        data_arr = []
        data_num_arr = []
        for row in cursor:
            # result[row[0]] = row[1]
            data_arr.append(row[0])
            data_num_arr.append(row[1])
        line = Line("歷史查詢統計","單位： 次")
        line.add("times",data_arr,data_num_arr,mark_point=["max","min"],is_label_show=True,is_datazoom_show=True,xaxis_rotate=30,xaxis_interval=2,datazoom_extra_type = "both",xaxis_margin=20,is_more_utils=True)
        # line.add("times",data_arr,data_num_arr)
        context = line.render_embed()
    elif requests.POST["type"] == "Cloud":    
        str_sql = "select word,translate from Mytest_translate"
        cursor = c.execute(str_sql)
        en = ""
        zh_CN = ""
        en_result={}
        zh_result = {}
        for row in cursor:
            word = row[0].encode("utf-8")
            word_tr = row[1].encode("utf-8")
            for ch in r'!"@#$%^&\*()_\?:;,<>\\/\|{}':
                word.replace(ch,"")
                word_tr.replace(ch,"")
            if u'\u4e00' <= row[0][0] <= u'\u9fff':
                zh_CN += word 
                en += word_tr + " "
            else:  
                zh_CN += word_tr
                en += word + " "
        # 英文統計        
        word_arr = en.split()
        for e in word_arr:
            en_result[e] = en_result.get(e,0) + 1
        en_res = list(en_result.items())
        en_res.sort(key=lambda x:x[1],reverse=True)

        # 中文統計
        zh_CN_arr = jieba.cut(zh_CN,cut_all=False)
        zh_CN_res = {}
        for d in zh_CN_arr:
            zh_CN_res[d] = zh_CN_res.get(d,0) + 1
        zh_CN_res = list(zh_CN_res.items())
        zh_CN_res.sort(key=lambda x:x[1],reverse=True)
        en_name_arr = []
        en_num_arr = []
        zh_CN_name_arr = []
        zh_CN_num_arr = []
        for i in en_res[:100]:
            en_name_arr.append(i[0])
            en_num_arr.append(i[1])
        for d in zh_CN_res[10:110]:
            zh_CN_name_arr.append(d[0])
            zh_CN_num_arr.append(d[1])

        en_char = WordCloud()
        # ,word_size_range=[20,100]
        try:
            if requests.POST["k"] == u"漢字":
                en_char.add("zh_CN",zh_CN_name_arr,zh_CN_num_arr,shape=requests.POST["t"])
            else:
                en_char.add("En",en_name_arr,en_num_arr,shape=requests.POST["t"])
        except:
            en_char.add("En",en_name_arr,en_num_arr,shape="diamond")
        
        context = en_char.render_embed()
        # return HttpResponse(json.dumps({"context":{"en_name":en_name_arr,"en_num":en_num_arr,"zh_CN_name":zh_CN_name_arr,"zh_CN_num":zh_CN_num_arr}}))    
        # return HttpResponse(json.dumps({"context":en_res[:10]}))    
        
    else:
        pass
    return HttpResponse(json.dumps({"context":context}))
######################################Class defined##############

class Get_TK:
    def __init__(self):  
        self.ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072;       
        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f";    
        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    };      
    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)

    def getTk(self,text):  
        # print(text)
        return self.ctx.call("TL",text)

######################################Function defined##############
def Mongo_conn(dbname,collame):
    conn = pymongo.MongoClient("10.10.0.96",27017)
    db = conn[dbname]  
    coll = db[collame]
    return coll

def buildUrl(text,tk):
    for ch in text:
        if u'\u4e00' <= ch <= u'\u9fff':
            from_ = 'zh-CN'
            to_ = 'en'
            break
        else:
            from_ = 'en'
            to_ = 'zh-CN'
    baseUrl='https://translate.google.cn/translate_a/single'
    baseUrl+='?client=t&'
    baseUrl+='sl='+from_+ '&'
    baseUrl+='tl='+ to_ +'&'
    baseUrl+='h1=zh-CN&'
    baseUrl+='dt=at&'
    baseUrl+='dt=bd&'
    baseUrl+='dt=ex&'
    baseUrl+='dt=ld&'
    baseUrl+='dt=md&'
    baseUrl+='dt=qca&'
    baseUrl+='dt=rw&'
    baseUrl+='dt=rm&'
    baseUrl+='dt=ss&'
    baseUrl+='dt=t&'
    baseUrl+='ie=UTF-8&'
    baseUrl+='oe=UTF-8&'
#   baseUrl+='otf=1&'
    baseUrl+='pc=1&'
#   baseUrl+='otf=1&'
    baseUrl+='source=btn&'
    baseUrl+='ssel=3&'
    baseUrl+='tsel=3&'
    baseUrl+='kc=2&'
    baseUrl+='tk='+str(tk)+'&'
    baseUrl+='q='+ urllib.quote_plus(text.encode('utf-8')) 
    return baseUrl

######################################Variable defined##############
cathy = "親愛的周純，"

proxy = {"http":"http://berg.qiu:9608769171@10.10.1.7:18263","https":"https://berg.qiu:9608769171@10.10.1.7:18263"}
IP_whitelist = ["10.9.232.75","10.9.224.66","10.10.1.77","10.10.1.7","10.9.232.74","10.9.232.92"]
header={    
        'authority':'translate.google.cn',
        'method':'GET',    
        'path':'',    
        'scheme':'https',    
        'accept':'*/*',    
        'accept-encoding':'gzip, deflate, br',    
        'accept-language':'zh-CN,zh;q=0.9',    
        'cookie':'',    
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'x-client-data':'CIa2yQEIpbbJAQjBtskBCPqcygEIqZ3KAQioo8oBGJGjygE='
    }
motto = [
    "To the world you may be one person, but to one person you may be the world",
    "Life is compared to a voyage",
    "love at first sight",
    "Life is a leaf of paper white, there on each of us may write his word or two",
    "you're uinique, nothing can replace you",
    "All that truly matters in the end is that you loved",
    "You know i love you, but you don`t know how much i love you",
    "It is better bo have love and lost than never to have loved at all",
    "Love's mysteries in souls do grow, but yet the body in his book",
    "Wherever you go, whatever you do, i will be right here waiting for you",
    "But soft! What lightthrough yonder windows breaks? It`s the east and cathy is thu sun",
    "Grow old along with me! The best is yet to be",
    "I love you not because of who you are, but because of who i am when  i am with you",
    "You complete me",
    "No matter the ending is perfect or not, you cannot disappear from my world",
    "If i know what love is,it is because of you",
    "If you don`t  let me go, i will love you forever",
    u"What you meet is fate, and all you have is luck(遇見都是天意，擁有都是幸運)",
    u"Do you want to drink and reach old age together, The vast snow, even if rain, whole life only for you(想陪你白頭到老，共飲風霜。就算夏雨洪荒，冬雪蒼茫，窮及一生也只為你)"    
]

love = [
        u"　　大千世界，茫茫人海。一個人與另一個人牽手的概率，微乎其微。",
        u"　　這是怎樣一個緣分，前世種了多大的因，才有今生的手手相牽。",
        u"　　此生歲月，都用一顆感恩的心，去對待這份感情。",
        u"　　親愛的，請原諒我的不善言辭，但請相信我會用行動證明。",
        u"　　佛家說：“無論你遇到誰，她都是對的人，無論發生什麼事，那都是唯一會發生的事，不管事情開始與哪個時刻，都是對的時刻”。就像我喜歡你，曾經的你和現在的你還有未來的你，不管是在未知的天之涯，海之角，我希望将来老到掉牙的那一天，陪我牵手看夕阳的看云舒云卷的还是你。",    
        u"　　有你，我什麼都不缺！"
]
