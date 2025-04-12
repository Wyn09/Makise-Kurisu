import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
import json
from dotenv import load_dotenv, find_dotenv
from mcp.server.fastmcp import FastMCP
load_dotenv(find_dotenv())

mcp = FastMCP("EmailServer")
USER_AGENT = "EmailServer-app/1.0"

@mcp.tool()
async def send_QQmail(subject, message_text, to="eyfen.wyn@qq.com", file_paths=None, attachment_folder=None):
    """
    发送QQ邮件, 支持多个附件及附件文件夹

    :param str subject: 邮件主题
    :param str message_text: 邮件正文,内容丰富一些,可以加入emoji表情
    :param str to: 收件人邮箱地址,默认参数是user的邮箱地址
    :param str, list file_paths: 可选参数, 字符串或列表, 附件的路径
    :param str attachment_folder: 可选参数, 附件文件夹路径, 该文件夹下所有文件将作为附件
    :return: 执行结果
    """
    sender = 'm.akise-kurisu@qq.com'
    token = os.getenv("QQEMAIL_API_KEY")

    try:
        msg = MIMEMultipart()
        msg['From'] = formataddr(["🐱", sender])
        msg['To'] = formataddr(["acc", to])
        msg['Subject'] = subject

        text_part = MIMEText(message_text, 'plain', 'utf-8')
        msg.attach(text_part)

        # 收集所有附件路径
        all_attachments = []
        if file_paths is not None:
            if isinstance(file_paths, (list, tuple)):
                all_attachments.extend(file_paths)
            else:
                all_attachments.append(file_paths)
        if attachment_folder is not None:
            if not os.path.isdir(attachment_folder):
                return json.dumps({"result": f"附件文件夹路径无效：{attachment_folder}"}, ensure_ascii=False)
            for filename in os.listdir(attachment_folder):
                file_path = os.path.join(attachment_folder, filename)
                if os.path.isfile(file_path):
                    all_attachments.append(file_path)

        # 添加所有附件（同步读取文件，适合小文件）
        if all_attachments:
            for file_path in all_attachments:
                with open(file_path, 'rb') as file:
                    attachment = MIMEApplication(file.read())
                    filename = os.path.basename(file_path)
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=('utf-8', '', filename)
                    )
                    msg.attach(attachment)

        # 异步发送邮件
        async with aiosmtplib.SMTP(hostname="smtp.qq.com", port=465, use_tls=True) as server:
            await server.login(sender, token)
            await server.send_message(msg)
        
    except Exception as e:
        return json.dumps({"result": f"发送失败! {e}"}, ensure_ascii=False)
    
    return json.dumps({"result": f"已成功发送邮件{to} !"}, ensure_ascii=False)

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')