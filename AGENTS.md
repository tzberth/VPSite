::ILANG
[TYPE:agent-rules][PROJECT:vps-deals][LANG:zh]
::STATE{@PROJECT, purpose:公开来源的 VPS 优惠与官方价格入口, output:静态站}
::RULE{先读 .ilang/site.ilang；它是品牌、来源、域名的唯一配置}
::RULE{只使用厂商公开且 robots.txt 允许抓取的页面；每条数据保留 source_url 和 fetched_at}
::RULE{优惠与常规价格分开标注；价格、币种、截止日期只能来自可核验的源页面}
::RULE{修改后运行 scraper.py 和 build.py，检查生成的 HTML、JSON-LD 和 sitemap}
::BOUNDARY{never:编优惠 编价格 编佣金 绕过反爬 刷量 注入 cookie|scope:permanent}
