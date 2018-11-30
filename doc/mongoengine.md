# mongoengine 使用问题

## 切换 collection 名字查询和插入

1. 查询

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mongoengine.queryset import QuerySet

def switch_table_and_return_query_set(collection, new_name):
    new_collection = collection.switch_collection(collection(), new_name)
    new_objects = QuerySet(collection,new_collection._get_collection())
    return new_objects
```

该函数输入为 mongoengine.document 对象和新 collection 的名字

返回值为 mongoengine.queryset.QuerySet 对象, 可以调用该对象的 API 进行查询和过滤

2. 插入

```python
collection = Collection()
collection.switch_collection('<collection_name>')
collection.save()
```

3. 删除

```python
collection = Collection(**collecyion_property)
collection.switch_collection('<collection_name>')
collection.delete()
```

4. 更新

首先用查询语句获取要更新的对象或者对象列表，获取结果为 result 的话，进行如下操作:

```python
result.switch_collection('<collection_name>')
result.update(**u_dic)
result.reload()
```

其中 Collection 为 mongoengine.document 的子类, collection 为 Collection 的实现

## mongoengine 的 ReferenceField

ReferenceField 类似于 sql 中的外键的作用, 当 collections 之间有固定的关系时可以使用 ReferenceField 将关系引入， 通过设定 reverse_delete_rule 属性可以进行关联删除

不适用情况:

collection 名字会变化的情况: 例如在我们的项目中, 每个工厂的 eqp collection 命名为 <FID> + eqp ;每个工厂设备供应商的 sup collection 命名为 <FID> + sup ;如果每次有新工厂创建时，就会创建新的 eqp 和 sup collection, 导致 eqp 中对 sup 的 ReferenceField 失效。

暂时没有更好的解决办法，解决方案是: 在 eqp 中只存 sup 的 SID, 再拿查询到的 SID 去处查询 sup 的相关信息


