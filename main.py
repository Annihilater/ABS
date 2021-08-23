#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2021/3/30 7:59 下午
# @Author: PythonVampire
# @email : vampire@ivamp.cn
# @File  : main.py
import os

import requests
import json

from jsonpath import jsonpath

"""
从北金所爬取注册申请报告、发行说明书、受托机构报告，爬取流程基本都一样，不同的是 menuId
注册申请报告的menuId：141
发行说明书的menuId：142
受托机构报告的menuId：68
思路：
1.获取查询结果总页数
2.遍历所有查询结果页，遍历每一个查询结果页，获取访问详情页所需的 info_id
2.访问详情页，获取文件下载地址
3.下载文件
"""


class ABS_Cfae:
    def __init__(self):
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.list_url = 'https://www.cfae.cn/connector/selectAllInfoNew'  # 列表页访问URL
        self.detail_url = 'https://www.cfae.cn/connector/selectFileInfoById'  # 详情页URL
        self.download_url = 'https://www.cfae.cn/SFTP/download?'  # 下载文件URL
        self.info_ids = []  # 每一个查询结果页的 info_id 列表
        self.total_page = 1  # 查询结果页总页数
        self.file_name = ''  # 文件名，下载文件需要用
        self.file_add = ''  # 文件上传日期，下载文件需要用
        self.file_list = []  # 文件详情页可能有多个文件，这里用文件列表存储
        self.menuId_1 = '141'  # 注册申请报告
        self.menuId_2 = '142'  # 发行说明书
        self.menuId_3 = '68'  # 受托机构报告
        self.menuId = ''  # 当前所爬取内容的menuId
        self.timeStart = '2020-01-01'  # 搜索的开始时间
        self.timeEnd = '2021-03-30'  # 搜索的结束时间

        self.registration_application_report_path = os.path.join(self.current_dir, '注册申请报告')
        self.release_prospectus_path = os.path.join(self.current_dir, '发行说明书')
        self.trustee_report_path = os.path.join(self.current_dir, '受托机构报告')

        self.create_dir()

    def create_dir(self):
        """
        判断存放三种文件的目录是否存在，如果不存在就自动创建
        :return:
        """
        if not os.path.exists(self.registration_application_report_path):
            os.makedirs(self.registration_application_report_path)

        if not os.path.exists(self.release_prospectus_path):
            os.makedirs(self.release_prospectus_path)

        if not os.path.exists(self.trustee_report_path):
            os.makedirs(self.trustee_report_path)

    def get_total(self):
        """
        获取查询结果页数
        :return:
        """
        payload = f"title=&pageNumber=1&menuId={self.menuId}&bondType=201&timeStart={self.timeStart}&timeEnd={self.timeEnd}&bondFullName=&trusteeOrg=&disOrg=&leadManager="
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.cfae.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://www.cfae.cn/xxpl/abs/zcjd/zcsq.html',
            'Cookie': 'zh_choose=n; JSESSIONID=YPyC_B7CkQG2ydAIPp28h5PIJ65Gq0kA5EVWfhgKjX8-d1k0WVBB!-553896300'
        }

        response = requests.request("POST", self.list_url, headers=headers, data=payload)
        if response.status_code == 200:
            d = json.loads(response.text)

            self.total_page = jsonpath(d, '$.totalPage')
            if self.total_page: self.total_page = self.total_page[0]

            self.total_count = jsonpath(d, '$.totalCount')
            if self.total_count: self.total_count = self.total_count[0]
            print(f'查询结果数量: {self.total_count}')

    def get_info_ids(self, page_no):
        """
        获取 info_id 列表
        :param page_no: 页码
        :return:
        """
        payload = f"title=&pageNumber={page_no}&menuId={self.menuId}&bondType=201&timeStart={self.timeStart}&timeEnd={self.timeEnd}&bondFullName=&trusteeOrg=&disOrg=&leadManager="
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.cfae.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://www.cfae.cn/xxpl/abs/zcjd/zcsq.html',
            'Cookie': 'zh_choose=n; JSESSIONID=YPyC_B7CkQG2ydAIPp28h5PIJ65Gq0kA5EVWfhgKjX8-d1k0WVBB!-553896300'
        }

        response = requests.request("POST", self.list_url, headers=headers, data=payload)
        if response.status_code == 200:
            d = json.loads(response.text)

            self.total_page = jsonpath(d, '$.totalCount')
            if self.total_page: self.total_page = self.total_page[0]

            self.info_ids = jsonpath(d, '$..info_id')

    def detail(self, id):
        """
        获取每个注册申请报告的详情页面
        :param id: id
        :return:
        """
        payload = f"infoId={id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://www.cfae.cn',
            'Connection': 'keep-alive',
            'Referer': 'https://www.cfae.cn/connector/selectOnePortalView?infoId=201182',
            'Cookie': 'zh_choose=n; JSESSIONID=YPyC_B7CkQG2ydAIPp28h5PIJ65Gq0kA5EVWfhgKjX8-d1k0WVBB!-553896300',
            'Cache-Control': 'max-age=0'
        }

        response = requests.request("POST", self.detail_url, headers=headers, data=payload)

        if response.status_code == 200:
            self.file_list = json.loads(response.text)
        else:
            print('Error: 详情页请求失败')

    def download(self, path):
        """
        下载文件，并保存在 path 文件夹下
        :param path: 保存的路径
        :return:
        """
        for file in self.file_list:
            self.file_name = file['FILE_NAME']
            self.file_add = file['FILE_ADDRESS']
            if self.menuId == self.menuId_2 and "发行说明书" not in self.file_name:
                continue
            file_path = os.path.join(path, self.file_name)
            url_path = f'fileName={self.file_name}&fileAdd={self.file_add}'
            url = self.download_url + url_path
            payload = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:87.0) Gecko/20100101 Firefox/87.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://www.cfae.cn',
                'Connection': 'keep-alive',
                'Referer': 'https://www.cfae.cn/connector/selectOnePortalView?infoId=201182',
                'Cookie': 'zh_choose=n; JSESSIONID=YPyC_B7CkQG2ydAIPp28h5PIJ65Gq0kA5EVWfhgKjX8-d1k0WVBB!-553896300',
                'Cache-Control': 'max-age=0'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                print('访问成功！')
                if os.path.exists(file_path):
                    print(f'文件已存在，不用下载：{self.file_name}')
                else:
                    print(f'文件不存在，开始创建文件：{self.file_name}')
                    with open(file_path, mode='wb') as f:
                        print('开始写入文件！')
                        for chunk in response.iter_content(chunk_size=10240):  # 每次加载10240字节
                            f.write(chunk)
                    print(f'创建成功：{self.file_name}')
            else:
                print('Error!')

    def go(self, menuId, path):
        """
        根据不同的 menuId 爬取不同阶段的文件，存放在 path 目录下
        :param path: 路径
        :param menuId: menuId
        :return:
        """
        self.menuId = menuId
        self.get_total()
        for page_no in range(1, self.total_page + 1):
            self.get_info_ids(page_no)
            for id in self.info_ids:
                self.detail(id)
                self.download(path)

    def main(self):
        """
        启动方法
        :return:
        """
        self.go(self.menuId_1, self.registration_application_report_path)  # 爬申请注册报告
        self.go(self.menuId_2, self.release_prospectus_path)  # 爬发行说明书
        self.go(self.menuId_3, self.trustee_report_path)  # 爬受托机构报告


if __name__ == '__main__':
    c = ABS_Cfae()
    c.main()
