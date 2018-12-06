# -*- coding: utf-8 -*-
'''
平台秤类V4_5

修改日志：

· 在V4_5基础上加入logging，去除一些print输出

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
--------------------------------------------
mysql -p -uroot

truncate table 表名;

influx -username ecust -password 123456
mongo -p -u ecust  --authenticationDatabase "admin"

mongo
use weighting
db.auth("siemens", "siemens")
--------------------------------------------
#####################################################################################
'''
import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as C
from sklearn.gaussian_process.kernels import RationalQuadratic
from sklearn.externals import joblib
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import time
import os
import re
import gc
from mongo import mongo_service
from mongoengine import *
import logging


class MongoCollection(Document):
    FaultTime = DateTimeField()  # 故障时间
    RecoverTime = DateTimeField()  # 恢复时间
    PeriodSecond = IntField()  # 间隔时间(s)
    FaultSensor = StringField()  # 故障传感器
    FaultCode = IntField()  # 故障代码
    EQP_State = IntField()  # 设备状态


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

        self.LoggingInit(logPath)   # 初始化logging设置

        self.GRModelPath_123To4 = GRModelPath_123To4
        self.GRModelPath_124To3 = GRModelPath_124To3
        self.GRModelPath_134To2 = GRModelPath_134To2
        self.GRModelPath_234To1 = GRModelPath_234To1
        self.GRModelPath_123To5 = GRModelPath_123To5
        self.GRModelPath_124To5 = GRModelPath_124To5
        self.GRModelPath_134To5 = GRModelPath_134To5
        self.GRModelPath_234To5 = GRModelPath_234To5

        self.flagDict = {}
        self.flagDict["partialLoadFlag"] = 0  # 偏载标志位
        self.flagDict["SensorTag1"] = 0  # 传感器1号的状态
        self.flagDict["SensorTag2"] = 0  # 传感器2号的状态
        self.flagDict["SensorTag3"] = 0  # 传感器3号的状态
        self.flagDict["SensorTag4"] = 0  # 传感器4号的状态
        self.flagDict["EQP_State"] = 0  # 设备状态标志位
        self.flagDict["Normal"] = 0
        self.flagDict["Alert"] = 0
        self.flagDict["Alarm"] = 0

    def LoggingInit(self, logPath):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler(logPath)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s '
                                      '- %(process)d - %(thread)d - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def JugeOverAndLose(self, W1List, W2List, W3List, W4List, overThred=9):
        '''
        判别信号丢失 或 过载
        :param W1List:
        :param W2List:
        :param W3List:
        :param W4List:
        :param overThred:
        :return:
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

        losCnt_1, losCnt_2, losCnt_3, losCnt_4 = 0, 0, 0, 0
        OverCnt_1, OverCnt_2, OverCnt_3, OverCnt_4 = 0, 0, 0, 0
        iterN = len(W1List)
        for i in range(iterN):
            if W1List[i] == 0:
                losCnt_1 += 1
            elif W1List[i] >= overThred:
                OverCnt_1 += 1
            if W2List[i] == 0:
                losCnt_2 += 1
            elif W2List[i] >= overThred:
                OverCnt_2 += 1
            if W3List[i] == 0:
                losCnt_3 += 1
            elif W3List[i] >= overThred:
                OverCnt_3 += 1
            if W4List[i] == 0:
                losCnt_4 += 1
            elif W4List[i] >= overThred:
                OverCnt_4 += 1

        if losCnt_1 >= iterN - 1:  # 1 号丢失信号
            self.flagDict["SensorTag1"] = 1
            self.flagDict["EQP_State"] = 1  # 说明设备出现问题
            # print(W1List)
            # self.logger.info("No.1 Sensor lose signal!")
        if losCnt_2 >= iterN - 1:  # 2 号丢失信号
            self.flagDict["SensorTag2"] = 1
            self.flagDict["EQP_State"] = 1  # 说明设备出现问题
            # print(W2List)
            # self.logger.info("No.2 Sensor lose signal!")
        if losCnt_3 >= iterN - 1:  # 3 号丢失信号
            self.flagDict["SensorTag3"] = 1
            self.flagDict["EQP_State"] = 1
            # print(W3List)
            # self.logger.info("No.3 Sensor lose signal!")
        if losCnt_4 >= iterN - 1:  # 4 号丢失信号
            self.flagDict["SensorTag4"] = 1
            self.flagDict["EQP_State"] = 1
            # print(W4List)
            # self.logger.info("No.4 Sensor lose signal!")

        if OverCnt_1 >= iterN - 1:  # 1 号过载
            self.flagDict["SensorTag1"] = 2
            self.flagDict["EQP_State"] = 1  # 说明设备出现问题
            # print(W1List)
            # self.logger.info("No.1 Sensor over load!")
        if OverCnt_2 >= iterN - 1:  # 2 号过载
            self.flagDict["SensorTag2"] = 2
            self.flagDict["EQP_State"] = 1
            # print(W2List)
            # self.logger.info("No.2 Sensor over load!")
        if OverCnt_3 >= iterN - 1:  # 3 号过载
            self.flagDict["SensorTag3"] = 2
            self.flagDict["EQP_State"] = 1
            # print(W3List)
            # self.logger.info("No.3 Sensor over load!")
        if OverCnt_4 >= iterN - 1:  # 4 号过载
            self.flagDict["SensorTag4"] = 2
            self.flagDict["EQP_State"] = 1
            # print(W4List)
            # self.logger.info("No.4 Sensor over load!")

    def FaultDiagnosis(self, W1, W2, W3, W4, threshold=5):
        '''
        检测传感器是否有故障（当前仅判断单个）
        :param W1:
        :param W2:
        :param W3:
        :param W4:
        :param threshold
        :return:
        '''

        # 若文件存在，自动加载模型
        try:
            xData123 = np.array([[W1, W2, W3]])
            GRModel_123To5 = joblib.load(self.GRModelPath_123To5)
            Pred_123To5 = GRModel_123To5.predict(xData123)  # 4号预估值
            del GRModel_123To5
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_123To5)")
            raise e

        try:
            xData124 = np.array([[W1, W2, W4]])
            GRModel_124To5 = joblib.load(self.GRModelPath_124To5)
            Pred_124To5 = GRModel_124To5.predict(xData124)  # 3号预估值
            del GRModel_124To5
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_124To5)")
            raise e

        try:
            xData134 = np.array([[W1, W3, W4]])
            GRModel_134To5 = joblib.load(self.GRModelPath_134To5)
            Pred_134To5 = GRModel_134To5.predict(xData134)  # 2号预估值
            del GRModel_134To5
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_134To5)")
            raise e

        try:
            xData234 = np.array([[W2, W3, W4]])
            GRModel_234To5 = joblib.load(self.GRModelPath_234To5)
            Pred_234To5 = GRModel_234To5.predict(xData234)  # 1号预估值
            del GRModel_234To5
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_134To5)")
            raise e

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

        # 123To5 与其他明显不同，说明传感器4读数有问题
        if ((abs(Pred_123To5 - Pred_124To5) > threshold)
            and (abs(Pred_123To5 - Pred_134To5) > threshold)
            and (abs(Pred_123To5 - Pred_234To5) > threshold)):
            self.flagDict["SensorTag4"] = 3
            self.flagDict["EQP_State"] = 2  # 设备有2级问题
            # print('No.4 Sensor Maybe Failure!')
            return Pred_123To5  # 将预测值返回

        # 124To5 与其他明显不同，说明传感器3读数有问题
        elif ((abs(Pred_124To5 - Pred_123To5) > threshold)
              and (abs(Pred_124To5 - Pred_134To5) > threshold)
              and (abs(Pred_124To5 - Pred_234To5) > threshold)):
            self.flagDict["SensorTag3"] = 3
            self.flagDict["EQP_State"] = 2  # 设备有2级问题
            # print('No.3 Sensor Maybe Failure!')
            return Pred_124To5

        # 134To5 与其他明显不同，说明传感器2读数有问题
        elif ((abs(Pred_134To5 - Pred_123To5) > threshold)
              and (abs(Pred_134To5 - Pred_124To5) > threshold)
              and (abs(Pred_134To5 - Pred_234To5) > threshold)):
            self.flagDict["SensorTag2"] = 3
            self.flagDict["EQP_State"] = 2  # 设备有2级问题
            # print('No.2 Sensor Maybe Failure!')
            return Pred_134To5

        # 234To5 与其他明显不同，说明传感器1读数有问题
        elif ((abs(Pred_234To5 - Pred_123To5) > threshold)
              and (abs(Pred_234To5 - Pred_124To5) > threshold)
              and (abs(Pred_234To5 - Pred_134To5) > threshold)):
            self.flagDict["SensorTag1"] = 3
            self.flagDict["EQP_State"] = 2  # 设备有2级问题
            # print('No.1 Sensor Maybe Failure!')
            return Pred_234To5
        else:
            # print('No problem...')
            return None

    def JugePartialLoad(self, W1, W2, W3, W4,
                        threshold_To4=5, threshold_To3=5, threshold_To2=5, threshold_To1=5):

        '''
        判别平台秤的偏载情况
        :param W1: W1的读数
        :param W2: W2的读数
        :param W3: W3的读数
        :param W4: W4的读数
        :param threshold_To4: 判别阈值
        :param threshold_To3: 判别阈值
        :param threshold_To2: 判别阈值
        :param threshold_To1: 判别阈值
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

        try:
            xData123 = np.array([[W1, W2, W3]])
            # 加载模型 4
            GRModel_123To4 = joblib.load(self.GRModelPath_123To4)
            Pred4 = GRModel_123To4.predict(xData123)  # 4号预估值
            del GRModel_123To4
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_123To4)")
            raise e

        try:
            xData124 = np.array([[W1, W2, W4]])
            # 加载模型 3
            GRModel_124To3 = joblib.load(self.GRModelPath_124To3)
            Pred3 = GRModel_124To3.predict(xData124)  # 3号预估值
            del GRModel_124To3
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_124To3)")
            raise e

        try:
            xData134 = np.array([[W1, W3, W4]])
            # 加载模型 2
            GRModel_134To2 = joblib.load(self.GRModelPath_134To2)
            Pred2 = GRModel_134To2.predict(xData134)  # 2号预估值
            del GRModel_134To2
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_134To2)")
            raise e

        try:
            xData234 = np.array([[W2, W3, W4]])
            # 加载模型 1
            GRModel_234To1 = joblib.load(self.GRModelPath_234To1)
            Pred1 = GRModel_234To1.predict(xData234)  # 1号预估值
            del GRModel_234To1
            gc.collect()  # 回收
        except Exception as e:
            self.logger.error("Loading model error...(GRModel_234To1)")
            raise e

        # 当3号或4号的实际值明显比预测值重 -> 左倾
        if ((W4 - Pred4 > threshold_To4) and (W3 - Pred3 > threshold_To3)):
            self.flagDict["partialLoadFlag"] = 1
            # print("<<<<<---...Left!")
        # 当1号或2号的实际值比预测值重  -> 右倾
        elif ((W1 - Pred1 > threshold_To1) and (W2 - Pred2 > threshold_To2)):
            self.flagDict["partialLoadFlag"] = 3
            # print("--->>>>>...Right!")
        # 当1号或4号的实际值比预测值重   -> 前侧
        elif ((W1 - Pred1 > threshold_To1) and (W4 - Pred4 > threshold_To4)):
            self.flagDict["partialLoadFlag"] = 4
            # print("↑↑↑↑↑↑↑↑...Forward!")
        # 当2号或3号的实际值比预测值重  -> 后仰
        elif ((W2 - Pred2 > threshold_To2) and (W3 - Pred3 > threshold_To3)):
            self.flagDict["partialLoadFlag"] = 2
            # print("↓↓↓↓↓↓↓↓...Back!")
        else:
            self.flagDict["partialLoadFlag"] = 0
            # print("Center")

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

        self.LoggingInit(logPath)
        self.FID = FID if isinstance(FID, str) else str(FID)  # 工厂ID号
        self.EID = EID if isinstance(EID, str) else str(EID)  # 设备ID号
        self.influx_client = InfluxDBClient(Host, Port, User, Pwd, DB_Name)
        self.PlatformScale = PlatformScale()

    def LoggingInit(self, logPath):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler(logPath)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s '
                                      '- %(process)d - %(thread)d - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def ReadVal(self):
        # print('Connecting to the database...')
        try:
            connect('weighting', username='siemens', password='siemens')
            CollectionName = self.FID + '_' + self.EID + '_FaultList'
            MG_Service = mongo_service(MongoCollection, CollectionName)
        except Exception as e:
            self.logger.warning("Mongo connecet error!.")
            raise e
        else:
            # print("Mongo connect success!")
            pass

        while True:
            startTime = datetime.now()
            # =============================这获取数据部分要更改为influxdb=========================
            utcNow = datetime.utcnow()
            Previous = utcNow - timedelta(seconds=5)
            Now = utcNow.strftime('%Y-%m-%dT%H:%M:%SZ')
            Previous = Previous.strftime('%Y-%m-%dT%H:%M:%SZ')

            measurementName = self.FID + "_" + self.EID + "_Val"  # 从此处读取数据

            # ===========================此处Query语句还有问题
            # 获取最新的5秒的数据
            getDataQuery = "SELECT * FROM " + measurementName + " WHERE time >= '" + Previous + "' and time <='" + Now + "'"

            SensorNum = 0  # 先归零
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
                SensorNum = len(item) - 2  # 表中有(时间，传感器，总)；故 (长度-时间-总) 即为传感器数量 # ======================!
                if (SensorNum == 4):
                    if isinstance(item['WeightTag1'], (float, int)):
                        Weight1List.append(item['WeightTag1'])
                    else:
                        readErrorFlag = 1
                        # print(item['WeightTag1'])
                        self.logger.info("Read Error! WeightTag1: " + str(item['WeightTag1']))
                        break
                    if isinstance(item['WeightTag2'], (float, int)):
                        Weight2List.append(item['WeightTag2'])
                    else:
                        readErrorFlag = 1
                        # print(item['WeightTag2'])
                        self.logger.info("Read Error! WeightTag2: " + str(item['WeightTag2']))
                        break
                    if isinstance(item['WeightTag3'], (float, int)):
                        Weight3List.append(item['WeightTag3'])
                    else:
                        readErrorFlag = 1
                        # print(item['WeightTag3'])
                        self.logger.info("Read Error! WeightTag3: " + str(item['WeightTag3']))
                        break
                    if isinstance(item['WeightTag4'], (float, int)):
                        Weight4List.append(item['WeightTag4'])
                    else:
                        readErrorFlag = 1
                        # print(item['WeightTag4'])
                        self.logger.info("Read Error! WeightTag4: " + str(item['WeightTag4']))
                        break
                if readErrorFlag == 1:
                    # print("Read data error..Wait...")
                    self.logger.warning("InfluxDB Read data error..Wait...")
                    time.sleep(5)  # 出现错误5秒后再继续查询
                    readErrorFlag = 0
                    continue

            # print("SensorNum: ", SensorNum)

            if (SensorNum == 4):  # 当传感器数量为4时：
                try:
                    Weight1 = np.mean(np.array(Weight1List))  # 求均值
                    Weight2 = np.mean(np.array(Weight2List))
                    Weight3 = np.mean(np.array(Weight3List))
                    Weight4 = np.mean(np.array(Weight4List))
                    WeightSum = Weight1 + Weight2 + Weight3 + Weight4
                except Exception as e:
                    self.logger.error('Weight calculating mean error!!!!!!!!')
                    self.logger.info("Weight1: " + str(Weight1List))
                    self.logger.info("Weight2: " + str(Weight1List))
                    self.logger.info("Weight3: " + str(Weight1List))
                    self.logger.info("Weight4: " + str(Weight1List))
                    raise e

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
                # =======================================================

                '''mongo'''
                rst = MG_Service.find_object()  # 先看表是否为空
                if len(rst) == 0:  # 为空表，说明是第一次插入
                    # 若设备不正常
                    if FlagDict['EQP_State'] != 0:
                        if FlagDict['SensorTag1'] != 0:
                            MG_Service.create_obj(FaultTime=utcNow,
                                                  FaultSensor='SensorTag1',
                                                  FaultCode=FlagDict['SensorTag1'],
                                                  EQP_State=FlagDict['EQP_State'])
                        if FlagDict['SensorTag2'] != 0:
                            MG_Service.create_obj(FaultTime=utcNow,
                                                  FaultSensor='SensorTag2',
                                                  FaultCode=FlagDict['SensorTag2'],
                                                  EQP_State=FlagDict['EQP_State'])
                        if FlagDict['SensorTag3'] != 0:
                            MG_Service.create_obj(FaultTime=utcNow,
                                                  FaultSensor='SensorTag3',
                                                  FaultCode=FlagDict['SensorTag3'],
                                                  EQP_State=FlagDict['EQP_State'])
                        if FlagDict['SensorTag4'] != 0:
                            MG_Service.create_obj(FaultTime=utcNow,
                                                  FaultSensor='SensorTag4',
                                                  FaultCode=FlagDict['SensorTag4'],
                                                  EQP_State=FlagDict['EQP_State'])
                    # 若设备正常
                    else:
                        MG_Service.create_obj(RecoverTime=utcNow,
                                              FaultSensor='SensorTag1',
                                              FaultCode=FlagDict['SensorTag1'],
                                              EQP_State=FlagDict['EQP_State'])
                        MG_Service.create_obj(RecoverTime=utcNow,
                                              FaultSensor='SensorTag2',
                                              FaultCode=FlagDict['SensorTag2'],
                                              EQP_State=FlagDict['EQP_State'])
                        MG_Service.create_obj(RecoverTime=utcNow,
                                              FaultSensor='SensorTag3',
                                              FaultCode=FlagDict['SensorTag3'],
                                              EQP_State=FlagDict['EQP_State'])
                        MG_Service.create_obj(RecoverTime=utcNow,
                                              FaultSensor='SensorTag4',
                                              FaultCode=FlagDict['SensorTag4'],
                                              EQP_State=FlagDict['EQP_State'])
                else:  # 为非空表
                    if FlagDict['EQP_State'] == 0:  # 设备正常，则所有传感器正常
                        for item in MG_Service.find_object(EQP_State=1):
                            old_dic = {"EQP_State": 1,
                                       "FaultSensor": item.FaultSensor}  # 找到EQP为1的传感器
                            new_dic = {"FaultCode": 0,  # 在更新其状态为正常
                                       "EQP_State": 0,
                                       "RecoverTime": utcNow,
                                       "PeriodSecond": (utcNow - item.FaultTime).seconds}
                            MG_Service.update_obj(old_dic, new_dic)  # 更新
                        for item in MG_Service.find_object(EQP_State=2):
                            old_dic = {"EQP_State": 2,
                                       "FaultSensor": item.FaultSensor}  # 找到EQP为2的传感器
                            new_dic = {"FaultCode": 0,  # 在更新其状态为正常
                                       "EQP_State": 0,
                                       "RecoverTime": utcNow,
                                       "PeriodSecond": (utcNow - item.FaultTime).seconds}
                            MG_Service.update_obj(old_dic, new_dic)  # 更新

                    elif FlagDict['EQP_State'] != 0:  # 设备不正常，需要先确定那个传感器不正常，同时记录原先正常的
                        for item in MG_Service.find_object(EQP_State=0):
                            if FlagDict['SensorTag1'] != 0:  # 如果是传感器1号不正确
                                old_dic = {"EQP_State": 0,
                                           "FaultSensor": "SensorTag1"}
                                new_dic = {"FaultCode": FlagDict['SensorTag1'],
                                           "EQP_State": FlagDict['EQP_State'],
                                           "FaultTime": utcNow}
                                MG_Service.update_obj(old_dic, new_dic)  # 更新
                            if FlagDict['SensorTag2'] != 0:  # 如果是传感器2号不正确
                                old_dic = {"EQP_State": 0,
                                           "FaultSensor": "SensorTag2"}
                                new_dic = {"FaultCode": FlagDict['SensorTag2'],
                                           "EQP_State": FlagDict['EQP_State'],
                                           "FaultTime": utcNow}
                                MG_Service.update_obj(old_dic, new_dic)  # 更新
                            if FlagDict['SensorTag3'] != 0:  # 如果是传感器2号不正确
                                old_dic = {"EQP_State": 0,
                                           "FaultSensor": "SensorTag3"}
                                new_dic = {"FaultCode": FlagDict['SensorTag3'],
                                           "EQP_State": FlagDict['EQP_State'],
                                           "FaultTime": utcNow}
                                MG_Service.update_obj(old_dic, new_dic)  # 更新
                            if FlagDict['SensorTag4'] != 0:  # 如果是传感器2号不正确
                                old_dic = {"EQP_State": 0,
                                           "FaultSensor": "SensorTag4"}
                                new_dic = {"FaultCode": FlagDict['SensorTag4'],
                                           "EQP_State": FlagDict['EQP_State'],
                                           "FaultTime": utcNow}
                                MG_Service.update_obj(old_dic, new_dic)  # 更新

                endTime = datetime.now()
                UseTime = (endTime - startTime).total_seconds()
                # print("Using time:", UseTime)
                if UseTime <= 5:
                    time.sleep(5 - UseTime)
                else:
                    # print("Runtime error!")
                    self.logger.debug("Runtime error! It used time:" + str(UseTime))
                # print('***********************')


if __name__ == '__main__':
    newSever = PlatformScaleSever()
    newSever.ReadVal()



