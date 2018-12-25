# -*- coding: utf-8 -*-
'''
用来生成测试数据

'''
import numpy as np
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import re
from socket import socket, AF_INET, SOCK_STREAM
from flask_project.platform.log import log


class GenerateDataSever(object):
    def __init__(self, influx_client, FID='ecust01', EID='scale01', logPath="..\log\Log_GenerateDataSever.txt"):
        super(GenerateDataSever, self).__init__()
        self.BUFSIZ = 2048
        self.ADDR = ('', 1123)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.FID = FID if isinstance(FID, str) else str(FID)
        self.EID = EID if isinstance(EID, str) else str(EID)
        self.influx_client = influx_client
        self.measurementName = self.FID + "_" + self.EID + "_Val"
        self.logger = log(logPath)

    def ReadVal(self):
        self.sock.bind(self.ADDR)
        self.sock.listen(5)

        print('wait and binding: 1123')
        try:
            tcpClientSock, addr = self.sock.accept()
        except Exception as e:
            self.logger.error("Client connected error!")
            raise e
        else:
            print('accepted, client address is：', addr)

        while True:
            try:
                data_str = tcpClientSock.recv(self.BUFSIZ)
                listdata = re.findall(b"\d+\.?\d*", data_str)
                listread = [float(x) / 100 for x in listdata]
            except Exception as e:
                self.logger.error("Get data error from tcpClientSock...")
                raise e

            if not len(listread) // 4:
                self.logger.warnnig("Read data can not // 4 ...")
                continue
            else:
                pass

            json_body = []
            for i in range(len(listread) // 4):
                newWeight1 = listread[4 * (i - 1)]
                newWeight2 = listread[4 * (i - 1) + 1]
                newWeight3 = listread[4 * (i - 1) + 2]
                newWeight4 = listread[4 * (i - 1) + 3]
                Weight = newWeight1 + newWeight2 + newWeight3 + newWeight4

                Now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                json_body.append({
                    "measurement": self.measurementName,
                    "time": Now,
                    "fields": {
                        "WeightTag1": newWeight1,
                        "WeightTag2": newWeight2,
                        "WeightTag3": newWeight3,
                        "WeightTag4": newWeight4,
                        "Weight": Weight
                    }
                })

            try:
                self.influx_client.write_points(json_body)
            except Exception as e:
                self.logger.error("Influx_client write data error!")
                raise e
                # print('success')


if __name__ == "__main__":
    influx_client = InfluxDBClient('localhost', 8086, 'ecust', '123456', 'PlatformScale')
    newSever = GenerateDataSever(influx_client)
    while True:
        try:
            newSever.ReadVal()
        except:
            continue
