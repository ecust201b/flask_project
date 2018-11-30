# 数据库逻辑整理

## 表格属性及其关系

**Factory 工厂表**

|属性     |数据类型  | 是否主键或索引 | unique |
| --------| -----   | -----         | -----  |
| FID     | string  | 主键，索引     | 是     |
| address | string  | 否            | 是     |

**< FID > + EQP 工厂设备总览**

|属性        |数据类型  | 是否主键或索引 | unique |
| --------   | -----   | -----         | -----  |
| EID        | string  | 主键，索引     | 是     |
| supplier   | string  | 是            | 否     |

**< FID > + SUP 工厂供应商**

|属性        |数据类型  | 是否主键或索引 | unique |
| --------   | -----   | -----         | -----  |
| SID        | string  | 主键，索引     | 是     |
| info       | string  | 是            | 否     |
| contact    | string  | 否            | 是     |

**< FID > + < EID > + StateCount 工厂设备状态计数**

|属性        |数据类型   | 是否主键或索引 | unique |
| --------   | -----    | -----         | -----  |
| Timestamp  | datetime | 主键，索引     | 是     |
| fault      | int      | 否            | 否     |
| alarm      | int      | 否            | 否     |
| normal     | int      | 否            | 否     |

**< FID > + < EID > + SP 某工厂某设备设定值**

该表中有 * 表示数量可变，具体数量应与 SencerNum 一致

|属性        |数据类型  | 是否主键或索引 | unique |
| --------   | -----    | -----         | ----- |
| Timestamp  | datetime | 索引            | 否     |
| Temp  | float    | 否            | 否     |
| Wet  | float    | 否            | 否     |
| SencerNum  | int      | 否            | 否     |
| NoLoadSet*  | float    | 否            | 否     |
| EmptyLoadSet*  | float    | 否            | 否     |
| ExcV*  | float    | 否            | 否     |
| Sensitivity*  | float    | 否            | 否     |
| Resistance*  | float    | 否            | 否     |
| Standard*  | float    | 否            | 否     |
| ZreoPoint*  | float    | 否            | 否     |

**< FID > + < EID > + FaultList 某工厂某设备故障列表**

|属性        |数据类型  | 是否主键或索引 | unique |
| --------   | -----    | -----         | ----- |
| FaultTime  | datetime | 索引            | 否     |
| RecorverTime  | datetime | 否            | 否     |
| PeriodSecond  | int |     否        | 否     |
| FaultSencer  | string |     索引        | 否     |
| FaultCode  | int |     索引        | 否     |

**< FID > + < EID > + Operation 某工厂某设备操作列表**

|属性        |数据类型  | 是否主键或索引 | unique |
| --------   | -----    | -----         | ----- |
| Timestamp  | datetime | 索引            | 否     |
| Record  | string | 否            | 否     |

**< FID > + < EID > + Val + < Date > 某工厂某设备某天的读数**

该表为时间序列, 数据列 field 数量根据设备的传感器数量变化

|属性        |数据类型  | tag or field | unique |
| --------   | -----    | -----         | ----- |
| FieldTag*  | float | field            | 否     |

**< FID > + < EID > + State + < Date > 某工厂某设备某天的故障诊断数据**

该表为时间序列, 数据列 FalutCode 数量根据设备的传感器数量变化, 这两个属性应该为 tag 而不是 field

|属性        |数据类型  | tag or field | unique |
| --------   | -----    | -----         | ----- |
| FalutCode*  | int | tag            | 否     |
| EQPState  | int | tag            | 否     |

## 表格自动维护功能

1. 数据表自动创建（mongo 和 influxdb 向某个 collection 或 measurement 插入数据时自动生成该表）

2. 自动删除数据表：当删除一个设备后，自动地将与该设备相关联的数据表全部删除，同时还要在工厂级的表格中删除与该设备相关的全部信息

3. 每天凌晨 2 点自动统计每个设备前一天的运行状态，将该结果记录到对应设备的 StateCount 表中
