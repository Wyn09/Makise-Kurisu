import os
import httpx
import json
from dotenv import load_dotenv, find_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv(find_dotenv())
mcp = FastMCP("SearchServer")
USER_AGENT = "SearchServer-app/1.0"


@mcp.tool()
async def google_search(query: str, num_results: int = 10, site_url: str = None) -> list:
    """
    谷歌搜索,可以指定搜索网站

    :param query: 搜索内容
    :param num_results: 返回搜索结果数量（默认10）
    :param site_url: 指定搜索网站（可选）
    :return: 包含标题、链接、摘要的字典列表
    """
    # 检查环境变量
    google_search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cse_id = os.getenv("CSE_ID")
    if not google_search_key or not cse_id:
        raise ValueError("Missing required environment variables: GOOGLE_SEARCH_API_KEY or CSE_ID")

    # 构建请求参数
    params = {
        "q": query,
        "key": google_search_key,
        "cx": cse_id,
        "num": num_results
    }
    if site_url:
        params.update({
            "siteSearch": site_url,
            "siteSearchFilter": "i"
        })

    # 发送异步请求
    async with httpx.AsyncClient(timeout=10.0) as client:  # 设置超时时间
        try:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"Google API request failed: {str(e)}") from e

    # 解析响应
    data = response.json()
    if "items" not in data:
        return []
    
    return json.dumps(
        {
            "results": 
            [
                {
                    "title": item.get("title", "No Title"),
                    "link": item.get("link", "#"),
                    "snippet": item.get("snippet", "")
                } for item in data["items"]
            ]
        }, ensure_ascii=False
    )






@mcp.tool()
async def news_search_NewsAPI(query: str, pageSize: int = 10, page=1):
    """
    使用NewsAPI进行新闻搜索

    :param str query: 一个搜索关键词(需要输入英文单词)
    :param int pageSize: 可选参数,默认为10.返回搜索结果每页的数量
    :param int page: 可选参数,默认为1.返回第几页的结果
    :return: 包含标题、描述、内容、新闻链接、发布时间的字典列表
    """
    # 检查环境变量
    apiKey = os.getenv("NewsAPI_API_KEY")

    if not apiKey:
        raise ValueError("Missing required environment variables: apiKey")

    # 构建请求
    url = "https://newsapi.org/v2/everything"

    # 设置查询参数
    params = {
        "q": query,
        "apiKey": apiKey,
        "pageSize": pageSize,
        "page": page
    }


    # 发送异步请求
    async with httpx.AsyncClient(timeout=10.0) as client:  # 设置超时时间
        try:
            response = await client.get(
                url,
                params=params
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"News API request failed: {str(e)}") from e

    # 解析响应
    data = response.json()
    if "articles" not in data:
        return []
    
    return json.dumps(
        {
            "results": 
            [
                {
                    "title": item.get("title", "No Title"),
                    "description": item.get("description", "No Description"),
                    "content": item.get("content", "No Content"),
                    "url": item.get("url", "No Url"),
                    "publishedAt": item.get("publishedAt", "No PublishedAt")
                } for item in data["articles"]
            ]
        }
    )




@mcp.tool()
async def news_search_GNews(query: str, lang :str = "zh", num_results: int = 10):
    """
    使用GNews进行新闻搜索
    
    :param str query: 一个搜索关键词(需要输入英文单词)
    :param str lang: 某种语言的新闻,可选:zh ja en,某种语言搜索结果较少时可试试其他语言
    :param int num_results: 可选参数,默认为10.返回搜索结果的数量
    :return: 包含标题、描述、内容、新闻链接、发布时间的字典列表
    """
    # 配置参数校验
    if not query or num_results <= 0:
        raise ValueError("Invalid query or result count")

    # API密钥配置
    apikey = "607567ed101cdc58829a3eb643cf98e4"  # 建议从环境变量读取
    if not apikey:
        raise ValueError("Missing required API key")

    # 构建请求URL
    url = f"https://gnews.io/api/v4/search?q={query}&lang={lang}&max={num_results}&apikey={apikey}"

    # 发送异步请求
    async with httpx.AsyncClient(timeout=10.0) as client:  # 设置10秒超时
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"GNews API请求失败: {str(e)}") from e

        # 解析响应数据
        data = response.json()
        articles = data.get("articles", [])

        # 结构化返回数据
    return json.dumps(
        {
            "results": 
            [
                {
                    "title": item.get("title", "No Title"),
                    "description": item.get("description", "No Description"),
                    "content": item.get("content", "No Content")[:500] + "..." if item.get("content") else "No Content",
                    "url": item.get("url", "#"),
                    "publishedAt": item.get("publishedAt", "Unknown Date")
                } for item in articles
            ]
        }
    )



if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')