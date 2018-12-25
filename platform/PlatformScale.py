# -*- coding: utf-8 -*-
'''
#####################################################################################
======================================
针对4个传感器
--------------------------------------
分布
4    1
3    2
--------------------------------------
self.partialLoadFlag  偏载标志位
0 -> 中间
1 -> 左倾
2 -> 后仰
3 -> 右倾
4 -> 前侧
--------------------------------------
self.SensorTagX (X=1,2,3,4;表示4个传感器序号)
0 -> 无问题
1 -> 丢失信号
2 -> 过载
3 -> 传感器故障（读数有问题）
--------------------------------------
self.EQP_State   设备状态标志
0 -> 正常运行    当且仅当 (self.partialLoadFlag == 0) && (self.SensorTagX == 0)
1 -> 短路或过载
2 -> 其他出现问题

0----> normal
1----> alert
2----> alarm
======================================

#####################################################################################
'''
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import time
import os
import re
import gc
from mongoengine import connect
from flask_project.app.util.db.mongo import mongo_service
from flask_project.platform.MongoCollection import MongoFaultCollection
from flask_project.platform.log import log


class PlatformScale(object):
    def __init__(self,
                 GRModelPath_123To4="../model/GR_train_model_123to4.m",
                 GRModelPath_124To3="../model/GR_train_model_124to3.m",
                 GRModelPath_134To2="../model/GR_train_model_134to2.m",
                 GRModelPath_234To1="../model/GR_train_model_234to1.m",
                 GRModelPath_123To5="../model/GR_train_model_123to5.m",
                 GRModelPath_124To5="../model/GR_train_model_124to5.m",
                 GRModelPath_134To5="../model/GR_train_model_134to5.m",
                 GRModelPath_234To5="../model/GR_train_model_234to5.m",
                 logPath="..\log\Log_PlatformScale.txt"):

        self.logger = log(logPath)  # 初始化logging设置

        self.GRModelPath_123To4 = GRModelPath_123To4
        self.GRModelPath_124To3 = GRModelPath_124To3
        self.GRModelPath_134To2 = GRModelPath_134To2
        self.GRModelPath_234To1 = GRModelPath_234To1
        self.GRModelPath_123To5 = GRModelPath_123To5
        self.GRModelPath_124To5 = GRModelPath_124To5
        self.GRModelPath_134To5 = GRModelPath_134To5
        self.GRModelPath_234To5 = GRModelPath_234To5

        self.flagDict = dict()
        self.flagDict["partialLoadFlag"] = 0  # 偏载标志位
        self.flagDict["SensorTag1"] = 0  # 传感器1号的状态
        self.flagDict["SensorTag2"] = 0  # 传感器2号的状态
        self.flagDict["SensorTag3"] = 0  # 传感器3号的状态
        self.flagDict["SensorTag4"] = 0  # 传感器4号的状态
        self.flagDict["EQP_State"] = 0  # 设备状态标志位
        self.flagDict["Normal"] = 0
        self.flagDict["Alert"] = 0
        self.flagDict["Alarm"] = 0

        # 列表第一位为哨兵，这样索引号即对应传感器号
        self.sensorList = ["Guard", "SensorTag1", "SensorTag2", "SensorTag3", "SensorTag4"]

    def Predict(self, *W_List, ModelPath):
        try:
            xData = np.array([W_List])
            GRModel = joblib.load(ModelPath)
            predVal = GRModel.predict(xData)
            del GRModel  # 释放内存，视情况是否添加
            gc.collect()
            return predVal
        except Exception as e:
            self.logger.error("Loading model error...")
            raise e

    def JugeOverAndLose(self, *W_List, overThred=9):
        '''
        判别信号丢失 或 过载
        '''
        # 重新归零
        self.flagDict["SensorTag1"] = 0  # 传感器1号的状态
        self.flagDict["SensorTag2"] = 0  # 传感器2号的状态
        self.flagDict["SensorTag3"] = 0  # 传感器3号的状态
        self.flagDict["SensorTag4"] = 0  # 传感器4号的状态
        self.flagDict["EQP_State"] = 0  # 设备状态标志位
        self.flagDict["Normal"] = 0
        self.flagDict["Alert"] = 0
        self.flagDict["Alarm"] = 0

        losCntList = ["Guard", 0, 0, 0, 0]
        overCntList = ["Guard", 0, 0, 0, 0]

        sensorX = 1  # 对应传感器
        for WxList in W_List:
            for i in range(len(WxList)):
                if WxList[i] == 0:
                    losCntList[sensorX] += 1
                elif WxList[i] >= overThred:
                    overCntList[sensorX] += 1
            sensorX += 1

        sensorX = 1
        for WxList in W_List:
            if losCntList[x] >= len(WxList) - 1:
                self.flagDict[self.sensorList[sensorX]] = 1
                self.flagDict["EQP_State"] = 1
            if overCntList[x] >= len(WxList) - 1:
                self.flagDict[self.sensorList[sensorX]] = 2
                self.flagDict["EQP_State"] = 1
            sensorX += 1

    def FaultDiagnosis(self, *Wx, threshold=5):
        '''
        检测传感器是否有故障（当前仅判断单个）
        '''
        Pred_123To5 = self.Predict(Wx[0], Wx[1], Wx[2], ModelPath=self.GRModelPath_123To5)
        Pred_124To5 = self.Predict(Wx[0], Wx[1], Wx[3], ModelPath=self.GRModelPath_124To5)
        Pred_134To5 = self.Predict(Wx[0], Wx[2], Wx[3], ModelPath=self.GRModelPath_134To5)
        Pred_234To5 = self.Predict(Wx[1], Wx[2], Wx[3], ModelPath=self.GRModelPath_234To5)

        if self.flagDict["EQP_State"] != 0:
            if self.flagDict["SensorTag1"] != 0:  # 说明1号已经过载或无信号了，不需要再进行下面的判断了
                return Pred_234To5
            if self.flagDict["SensorTag2"] != 0:
                return Pred_134To5
            if self.flagDict["SensorTag3"] != 0:
                return Pred_124To5
            if self.flagDict["SensorTag4"] != 0:
                return Pred_123To5
        else:
            pass

        if ((abs(Pred_123To5 - Pred_124To5) > threshold)
            and (abs(Pred_123To5 - Pred_134To5) > threshold)
            and (abs(Pred_123To5 - Pred_234To5) > threshold)):
            self.flagDict["SensorTag4"] = 3
            self.flagDict["EQP_State"] = 2
            # print('No.4 Sensor Maybe Failure!')
            return Pred_123To5
        elif ((abs(Pred_124To5 - Pred_123To5) > threshold)
              and (abs(Pred_124To5 - Pred_134To5) > threshold)
              and (abs(Pred_124To5 - Pred_234To5) > threshold)):
            self.flagDict["SensorTag3"] = 3
            self.flagDict["EQP_State"] = 2
            # print('No.3 Sensor Maybe Failure!')
            return Pred_124To5
        elif ((abs(Pred_134To5 - Pred_123To5) > threshold)
              and (abs(Pred_134To5 - Pred_124To5) > threshold)
              and (abs(Pred_134To5 - Pred_234To5) > threshold)):
            self.flagDict["SensorTag2"] = 3
            self.flagDict["EQP_State"] = 2
            # print('No.2 Sensor Maybe Failure!')
            return Pred_134To5
        elif ((abs(Pred_234To5 - Pred_123To5) > threshold)
              and (abs(Pred_234To5 - Pred_124To5) > threshold)
              and (abs(Pred_234To5 - Pred_134To5) > threshold)):
            self.flagDict["SensorTag1"] = 3
            self.flagDict["EQP_State"] = 2
            # print('No.1 Sensor Maybe Failure!')
            return Pred_234To5
        else:
            # print('No problem...')
            return None

    def JugePartialLoad(self, W1, W2, W3, W4,
                        threshold_To4=5, threshold_To3=5,
                        threshold_To2=5, threshold_To1=5):

        '''
        判别平台秤的偏载情况
        :return: 注意，返回的预测值为：np.array([data]) 格式
        '''
        Pred = self.FaultDiagnosis(W1, W2, W3, W4)

        if (Pred is not None):  # 表示传感器读数有问题
            if (self.flagDict["SensorTag4"] == 3):
                W4 = Pred - W1 - W2 - W3  # 修正故障传感器读数   # 修正方法后面应该改成LSTM预测
            elif (self.flagDict["SensorTag3"] == 3):
                W3 = Pred - W1 - W2 - W4
            elif (self.flagDict["SensorTag2"] == 3):
                W2 = Pred - W1 - W3 - W4
            elif (self.flagDict["SensorTag1"] == 3):
                W1 = Pred - W2 - W3 - W4
        else:
            pass

        Pred4 = self.Predict(W1, W2, W3, ModelPath=self.GRModelPath_123To4)
        Pred3 = self.Predict(W1, W2, W4, ModelPath=self.GRModelPath_124To3)
        Pred2 = self.Predict(W1, W3, W4, ModelPath=self.GRModelPath_134To2)
        Pred1 = self.Predict(W2, W3, W4, ModelPath=self.GRModelPath_234To1)

        # -> 左倾
        if ((W4 - Pred4 > threshold_To4) and (W3 - Pred3 > threshold_To3)):
            self.flagDict["partialLoadFlag"] = 1
        # -> 右倾
        elif ((W1 - Pred1 > threshold_To1) and (W2 - Pred2 > threshold_To2)):
            self.flagDict["partialLoadFlag"] = 3
        # -> 前侧
        elif ((W1 - Pred1 > threshold_To1) and (W4 - Pred4 > threshold_To4)):
            self.flagDict["partialLoadFlag"] = 4
        # -> 后仰
        elif ((W2 - Pred2 > threshold_To2) and (W3 - Pred3 > threshold_To3)):
            self.flagDict["partialLoadFlag"] = 2
        else:
            self.flagDict["partialLoadFlag"] = 0

        if self.flagDict['EQP_State'] == 0:
            self.flagDict['Normal'] = 1
        elif self.flagDict['EQP_State'] == 1:
            self.flagDict['Alert'] = 1
        elif self.flagDict['EQP_State'] == 2:
            self.flagDict['Alarm'] = 1
        else:
            pass

        W = Pred1 + Pred2 + Pred3 + Pred4
        return Pred1[0][0], Pred2[0][0], Pred3[0][0], Pred4[0][0], W[0][0], self.flagDict


class PlatformScaleSever(object):
    def __init__(self, FID='ecust01', EID='scale01', DB_Name='PlatformScale',
                 User='ecust', Pwd='123456', Host='localhost', Port=8086,
                 logPath="..\log\Log_PlatformScaleSever.txt"):
        super(PlatformScaleSever, self).__init__()

        self.FID = FID if isinstance(FID, str) else str(FID)
        self.EID = EID if isinstance(EID, str) else str(EID)
        self.influx_client = InfluxDBClient(Host, Port, User, Pwd, DB_Name)
        self.PlatformScale = PlatformScale()
        self.logger = log(logPath)

    def Run(self):
        # print('Connecting to the database...')
        try:
            connect('weighting', username='siemens', password='siemens')
            CollectionName = self.FID + '_' + self.EID + '_FaultList'
            MG_Service = mongo_service(MongoFaultCollection, CollectionName)
        except Exception as e:
            self.logger.error("Mongo connecet error!.")
            raise e
        else:
            # print("Mongo connect success!")
            pass

        while True:
            startTime = datetime.now()

            utcNow = datetime.utcnow()
            Previous = utcNow - timedelta(seconds=5)
            Now = utcNow.strftime('%Y-%m-%dT%H:%M:%SZ')
            Previous = Previous.strftime('%Y-%m-%dT%H:%M:%SZ')

            measurementName = self.FID + "_" + self.EID + "_Val"  # 从此处读取数据

            # 获取最新的5秒的数据
            getDataQuery = "SELECT * FROM " + measurementName \
                           + " WHERE time >= '" + Previous + "' and time <='" + Now + "'"

            SensorNum = 0  # 传感器数量初始化
            Weight1List, Weight2List, Weight3List, Weight4List = [], [], [], []

            # 发送请求并获取数据生成器
            try:
                res = self.influx_client.query(getDataQuery)
            except Exception as e:
                self.logger.error("Influx_client query error!")
                raise e

            if len(res) == 0:  # 说明无数据返回
                self.logger.info("Influx no data had read... Please wait...")
                time.sleep(5)  # 如果没数据，则5秒后再继续查询
                continue

            readErrorFlag = 0
            for item in res.get_points():
                '''================ 视情况这里要改！=============='''
                SensorNum = len(item) - 2  # 表中有(时间，传感器，总)；故 (长度-时间-总) 即为传感器数量
                if SensorNum == 4:
                    if isinstance(item['WeightTag1'], (float, int)):
                        Weight1List.append(item['WeightTag1'])
                    else:
                        readErrorFlag = 1
                        self.logger.warning("Read Error! WeightTag1: " + str(item['WeightTag1']))
                        break
                    if isinstance(item['WeightTag2'], (float, int)):
                        Weight2List.append(item['WeightTag2'])
                    else:
                        readErrorFlag = 1
                        self.logger.warning("Read Error! WeightTag2: " + str(item['WeightTag2']))
                        break
                    if isinstance(item['WeightTag3'], (float, int)):
                        Weight3List.append(item['WeightTag3'])
                    else:
                        readErrorFlag = 1
                        self.logger.warning("Read Error! WeightTag3: " + str(item['WeightTag3']))
                        break
                    if isinstance(item['WeightTag4'], (float, int)):
                        Weight4List.append(item['WeightTag4'])
                    else:
                        readErrorFlag = 1
                        self.logger.warning("Read Error! WeightTag4: " + str(item['WeightTag4']))
                        break
                if readErrorFlag == 1:
                    self.logger.warning("InfluxDB Read data error..Wait...")
                    time.sleep(5)  # 出现错误5秒后再继续查询
                    readErrorFlag = 0
                    continue

            if (SensorNum == 4):  # 当传感器数量为4时：
                sensorList = ["SensorTag1", "SensorTag2", "SensorTag3", "SensorTag4"]
                try:
                    Weight1 = sum(Weight1List) / len(Weight1List)  # 求均值
                    Weight2 = sum(Weight2List) / len(Weight2List)
                    Weight3 = sum(Weight3List) / len(Weight3List)
                    Weight4 = sum(Weight4List) / len(Weight4List)
                    WeightSum = Weight1 + Weight2 + Weight3 + Weight4
                except Exception as e:
                    WList = [Weight1List, Weight2List, Weight3List, Weight4List]
                    self.logger.error('Weight calculating mean error: ' + str(WList))
                    continue

                self.PlatformScale.JugeOverAndLose(Weight1List, Weight2List, Weight3List, Weight4List)
                W1, W2, W3, W4, W, FlagDict = self.PlatformScale.JugePartialLoad(Weight1, Weight2, Weight3, Weight4)

                points = [
                    {
                        "measurement": self.FID + "_" + self.EID + "_State",
                        "time": Now,
                        "fields": {
                            "WeightTag1": Weight1,
                            "WeightTag2": Weight2,
                            "WeightTag3": Weight3,
                            "WeightTag4": Weight4,
                            "Weight": WeightSum,
                            "W1": W1,
                            "W2": W2,
                            "W3": W3,
                            "W4": W4,
                            "W": W,
                            "PartialLoadFlag": FlagDict['partialLoadFlag'],
                            "SensorTag1": FlagDict['SensorTag1'],
                            "SensorTag2": FlagDict['SensorTag2'],
                            "SensorTag3": FlagDict['SensorTag3'],
                            "SensorTag4": FlagDict['SensorTag4'],
                            "EQP_State": FlagDict['EQP_State'],
                            "Normal": FlagDict['Normal'],
                            "Alert": FlagDict['Alert'],
                            "Alarm": FlagDict['Alarm'],
                        }
                    }
                ]

                '''influx'''
                try:
                    self.influx_client.write_points(points)
                except Exception as e:
                    self.logger.error("Influx_client write data error!")
                    raise e

                '''mongo'''
                # 如果当前正常，查找不正常的记录
                if FlagDict['EQP_State'] == 0:
                    for item in MG_Service.find_object(EQP_State=1):
                        old_dic = {"EQP_State": 1}
                        new_dic = {"EQP_State": 0,
                                   "RecoverTime": utcNow,
                                   "PeriodSecond": (utcNow - item.FaultTime).seconds}
                        MG_Service.update_obj(old_dic, new_dic)  # 更新
                    for item in MG_Service.find_object(EQP_State=2):
                        old_dic = {"EQP_State": 2}
                        new_dic = {"EQP_State": 0,
                                   "RecoverTime": utcNow,
                                   "PeriodSecond": (utcNow - item.FaultTime).seconds}
                        MG_Service.update_obj(old_dic, new_dic)  # 更新
                else:  # 若当前不正常，则判断当前的不正常状态原库中是否存在，若不存在则添加信息
                    for SensorTag in sensorList:
                        rst = MG_Service.find_object(FaultSensor=SensorTag, EQP_State=FlagDict['EQP_State'])
                        if not rst:
                            MG_Service.create_obj(FaultTime=utcNow, FaultSensor=SensorTag,
                                                  FaultCode=FlagDict[SensorTag], EQP_State=FlagDict['EQP_State'])

                endTime = datetime.now()
                UseTime = (endTime - startTime).total_seconds()
                # print("Using time:", UseTime)
                if UseTime <= 5:
                    time.sleep(5 - UseTime)
                else:
                    self.logger.debug("Runtime error! It used time:" + str(UseTime))
                    # print('***********************')


if __name__ == '__main__':
    newSever = PlatformScaleSever()
    while True:
        try:
            newSever.Run()
        except:
            continue
