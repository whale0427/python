from django import template
from django.http import QueryDict
from urllib.parse import urlencode
#Django 模板系统的 “库” 类，用于注册自定义模板标签 / 过滤器，所有自定义模板功能都需要通过它来注册。
register=template.Library()
#Python 的装饰器语法，用来给函数添加额外功能。
#**kwargs是Python 的 “关键字参数收集” 语法，把调用时传递的键值对参数收集成一个字典
# （比如模板中传grade=1，这里kwargs就是{"grade":1}）。
@register.simple_tag
def search_url(request,**kwargs):
    #request.META是请求的元数据字典，QUERY_STRING对应当前 URL 的查询参数部分
    #Django 自定义的 “类字典” 类型，专门用于处理 URL 查询参数（支持一个键对应多个值，比如?hobby=book&hobby=sport）。
    # （比如 URL 是/student_list/?grade=1&search=张三，这里就是"grade=1&search=张三"）。
    #QueryDict默认是不可修改的，加这个参数mutable=True是为了让querydict可以被修改（后续要添加 / 删除参数）
    querydict=QueryDict(request.META["QUERY_STRING"],mutable=True)
    for key,value in kwargs.items():
        if value is None:
            #从query_params中删除key对应的参数。
            #第一个参数key：要删除的参数名（比如"grade"）。
            #第二个参数None：如果key不存在，不会报错（避免KeyError）。
            querydict.pop(key,None)
        else:
            querydict.setlist(key,[value])
    #将字典 / QueryDict 类型的参数转换成 URL 查询字符串
    # （比如把{"grade":1, "search":"张三"}转成"grade=1&search=%E5%BC%A0%E4%B8%89"）
    #第一个参数query_params：要转换的QueryDict对象。
    #doseq=True：表示如果QueryDict中一个键对应多个值（比如hobby: ["book", "sport"]），会转换成hobby=book&hobby=sport的格式
    # （否则会转成hobby=%5B%27book%27%2C+%27sport%27%5D，不符合 URL 规范）。
    # 最终返回的是拼接好的 URL 查询字符串（比如"grade=1&search=%E5%BC%A0%E4%B8%89"），可以直接拼在 URL 后面。
    return urlencode(querydict,doseq=True)