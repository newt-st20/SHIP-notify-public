        driver.get(
            "https://ship.sakae-higashi.jp/school_news/search.php?obj_id=&depth=&search=&s_y=2011&s_m=01&s_d=01&e_y=2030&e_m=12&e_d=31")
        schoolNews = driver.page_source
        schoolNewsSoup = BeautifulSoup(schoolNews, 'html.parser')
        schoolNewsTrs = schoolNewsSoup.find_all(class_='allc')[0].find_all('tr')
        schoolNewsTrs.pop(0)
        schoolNewsList = []
        for schoolNewsTr in schoolNewsTrs:
            time.sleep(1)
            eachschoolNewsList = []
            schoolNewsTrTds = schoolNewsTr.find_all('td')
            try:
                stage = schoolNewsTrTds[2].find('a').get('onclick')
                schoolNewsId = re.findall("'([^']*)'", stage)
            except Exception as e:
                print(str(e))
            if int(schoolNewsId[0]) not in getedList:
                try:
                    eachschoolNewsList.append(schoolNewsId)
                    driver.get(
                        "https://ship.sakae-higashi.jp/sub_window/?obj_id="+schoolNewsId[0]+"&t=4")
                    schoolNewsEachPageSoup = BeautifulSoup(
                        driver.page_source, 'html.parser')
                    schoolNewsPageMain = schoolNewsEachPageSoup.find_all(class_='ac')[0].find_all(class_='bg_w')[0]
                    schoolNewsPageDescription = schoolNewsPageMain.find_all(
                        "table")[-2].text.replace("\n", "")
                    eachschoolNewsList.append(schoolNewsPageDescription)
                    if schooltype == "high":
                        schoolNewsPageLinks = schoolNewsPageMain.find_all("a")
                        schoolNewsPageLinkList = []
                        for eachConPageLink in schoolNewsPageLinks:
                            driver.get("https://ship.sakae-higashi.jp" + eachConPageLink.get("href"))
                            result = re.match(".*name=(.*)&size.*", eachConPageLink.get("href"))
                            print(result.group(1))
                            time.sleep(5)
                            if os.environ['STATUS'] == "local":
                                filepath = 'D:\Downloads/' + result.group(1)
                            else:
                                filepath = DOWNLOAD_DIR + '/' + result.group(1)
                            storage = firebase.storage()
                            try:
                                storage.child(
                                    'pdf/high-schoolNews/'+str(eachschoolNewsList[0][0])+'/'+result.group(1)).put(filepath)
                                schoolNewsPageLinkList.append(storage.child(
                                    'pdf/high-schoolNews/'+str(eachschoolNewsList[0][0])+'/'+result.group(1)).get_url(token=None))
                            except Exception as e:
                                print(str(e))
                        eachschoolNewsList.append(schoolNewsPageLinkList)
                except Exception as e:
                    print(str(e))
                    eachschoolNewsList.append([0, 0])
                    eachschoolNewsList.append("")
                eachschoolNewsList.append(schoolNewsTrTds[0].text)
                try:
                    eachschoolNewsList.append(schoolNewsTrTds[1].find('span').get('title'))
                except:
                    eachschoolNewsList.append("")
                eachschoolNewsList.append(schoolNewsTrTds[2].text.replace("\n", ""))
                schoolNewsList.append(eachschoolNewsList)
        print(schoolNewsList)