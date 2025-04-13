from mcp.server.fastmcp import FastMCP
import json
import datetime


mcp = FastMCP("ScheduleServer")
USER_AGENT = "ScheduleServer-app/1.0"


AGENDA = {}

async def gen_agenda(time: str, content):

    time = time.split(" ")
    Y_m_d, H_M_S = time[0], time[1]
    year, month, day = Y_m_d.replace("%", "").split("-")
    hour, minute, second = H_M_S.replace("%", "").split(":")
    time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)).isoformat()
    return {time: [content]}



@mcp.tool()
async def add_agenda(time, content):
    """
    添加日程,可批量添加。批量添加时时间必须和内容一一对应

    :param str, list[str] time: 时间, 字符串或字符串列表, 时间格式为%Y-%m-%d %H:%M:%S
    :param str, list[str] content: 日程内容, 字符串或字符串列表
    """
    agd = []
    if isinstance(time, str):
        time = [time]
    
    if isinstance(content, str):
        content = [content]
        
    for t, c in zip(time, content):
        item = await gen_agenda(t, c)
        if t not in AGENDA.keys():
            AGENDA.update(item)
        else: 
            AGENDA[time].append(content)
        agd.append(item)
    return json.dumps({"result": f"成功添加日程:{agd}"}, ensure_ascii=False)
    pass


@mcp.tool()
async def delete_agenda(time):
    """
    删除日程,可批量删除。如果你不知道时间可以先执行list_agenda()

    :param str, list[str] time: 时间, 字符串或字符串列表, 时间格式为%Y-%m-%d %H:%M:%S
    """
    agd = []
    if isinstance(time, str):
        time = [time]

    try:
        for t in time:
            item = AGENDA.pop(t)
            agd.append(item)
        return json.dumps({"result": f"成功删除日程:{agd}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"result": f"删除日程失败:{e}"}, ensure_ascii=False)
    pass


@mcp.tool()
async def update_agenda(time, content):
    """
    修改日程,可批量更改。更改已设定的时间的任务,若指定的时间不在日程中,该函数可执行添加指定的任务。批量更改时时间必须和内容一一对应
    如果你不知道时间可以先执行list_agenda()  

    :param str, list[str] time: 时间, 字符串或字符串列表, 时间格式为%Y-%m-%d %H:%M:%S
    :param str, list[str] content: 日程内容, 字符串或字符串列表
    """
    agd = []
    if isinstance(time, str):
        time = [time]

    if isinstance(content, str):
        content = [content]

    for t, c in zip(time, content):
        item = await gen_agenda(t, c)
        if t not in AGENDA.keys():
            AGENDA.update(item)
        else: 
            AGENDA[time] = content 
        agd.append(item)
    return json.dumps({"result": f"成功更改日程:{agd}"}, ensure_ascii=False)

    pass


@mcp.tool()
async def list_agenda():
    """
    查看所有日程
    """
    return json.dumps({"result": AGENDA}, ensure_ascii=False)
    pass

# @mcp.tool()
# async def set_remind_fixed_time(year: int, month: int, day: int, hour: int, minute: int, second: int) -> datetime.datetime:
#     """
#     设置日程提醒的时间,返回指定时间的 datetime.datetime 对象

#     :param int year: 年份
#     :param int month: 月份
#     :param int day: 日期
#     :param int hour: 小时
#     :param int minute: 分钟
#     :param int second: 秒
#     :return: 指定时间的 datetime.datetime 对象
#     """
#     fixed_time = datetime.datetime(year, month, day, hour, minute, second)
#     AGENDA.append(fixed_time)
#     return 


if __name__ == "__main__":
    mcp.run("stdio")