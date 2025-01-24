import requests
import os
import sys
from multiprocessing import Pool
import time
import random

# 获取程序运行路径
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def download_file(args):
    try:
        file_info, ti, title, headers, cookies = args
        fileName = f'文件/{ti}/{title}/' + str(file_info['fileName']).replace('/', '_')
        fileUrl = file_info['fileUrl']
        wj_rank = 0
        while 1:
            try:
                wj_rank += 1
                if wj_rank == 5:
                    break
                # 添加随机延时
                time.sleep(random.uniform(0, 0.8))
                res = requests.get(fileUrl, headers=headers, cookies=cookies)
                if res.status_code == 200:
                    with open(fileName, 'wb') as f:
                        f.write(res.content)
                    print(f"正在下载: {fileName}")
                break
            except Exception as e:
                print(f"下载重试 {fileName}: {e}")
                # 出错后等待更长时间
                time.sleep(random.uniform(0, 0.5))
    except Exception as e:
        print(f"下载出错: {e}")

def process_item(args):
    try:
        i, headers, cookies, j, k = args
        title = str(i['title']).replace('/', '_')
        ti = str(i['addtimeStr']).split(' ')[0]
        
        if k > int(str(ti).replace('-', '')):
            return True
            
        if j >= int(str(ti).replace('-', '')):
            print(f'当前采集：{title} 时间：{ti}')
            os.makedirs(f"文件/{ti}/{title}", exist_ok=True)
            
            content = i['content']
            ur = i['id']
            urls = f'http://plap.mil.cn/freecms/rest/v1/notice/selectNoticeDocInfo.do?currPage=1&pageSize=10&id={ur}'
            
            # 添加随机延时
            time.sleep(random.uniform(0, 0.1))
            
            while 1:
                try:
                    res_html = requests.get(url=urls, timeout=(5,5)).json()
                    break
                except:
                    time.sleep(random.uniform(0, 0.1))
                    pass
            
            if res_html.get('data'):
                downloaded_count = 0
                for file_info in res_html['data']:
                    download_file((file_info, ti, title, headers, cookies))
                    downloaded_count += 1
                    # 每下载3个文件暂停一下
                    if downloaded_count % 10 == 0:
                        time.sleep(random.uniform(0, 1))
            
            with open(f"文件/{ti}/{title}/{title}.html", "w", encoding='utf-8') as file:
                file.write(content)
            
            return False
    except Exception as e:
        print(f"处理项目出错: {e}")
        return False

def main():
    print("欢迎使用军队采购网下载器")
    print("="*100)
    
    token = input('请输入token：')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        # 添加更多请求头，模拟真实浏览器
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'http://plap.mil.cn/'
    }
    cookies = {
        'access_token': token
    }
    
    if not os.path.exists("文件"):
        os.makedirs("文件")
    k = int(input('请输入开始日期如（20230801）全部采集模式输0就可：'))
    j = int(input('请输入结束日期如（20230802）全部采集模式输当天日期就可如（20230802）：'))
    
    # 减少并发进程数
    with Pool(processes=2) as pool:
        page = 0
        while True:
            try:
                page += 1
                url = f'http://plap.mil.cn/freecms/rest/v1/notice/selectInfoMoreChannel.do?&siteId=404bb030-5be9-4070-85bd-c94b1473e8de&channel=c5bff13f-21ca-4dac-b158-cb40accd3035&currPage={page}&pageSize=10&noticeType=&regionCode=&purchaseManner=&title=&openTenderCode=&operationStartTime=&operationEndTime=&selectTimeName=&cityOrArea='
                
                # 每页请求前添加随机延时
                time.sleep(random.uniform(0, 1))
                
                rank = 0
                while 1:
                    try:
                        rank += 1
                        if rank == 5:
                            break
                        res = requests.get(url=url, timeout=(5,5)).json()
                        break
                    except:
                        time.sleep(random.uniform(0, 1))
                        pass

                args_list = [(item, headers, cookies, j, k) for item in res['data']]
                results = pool.map(process_item, args_list)
                
                if True in results:
                    break
                
                # 每页处理完后添加较长延时
                time.sleep(random.uniform(0, 2))
                    
            except Exception as e:
                print(f"发生错误: {e}")
                time.sleep(random.uniform(0, 5))
                break
                
    print("="*50)
    print("下载完成！按任意键退出...")
    input()

if __name__ == '__main__':
    main()
