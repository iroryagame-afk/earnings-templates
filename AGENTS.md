# earnings-templates 云端开发说明

本仓只有静态财报图模板。云端环境给三个人分工用：铲钱官在这里改模板，鸡蛋独立看图，总管协调。不负责其他仓库，不部署，不连接行情或持仓。

## 职责

- 铲钱官：改 `single-company/` 与 `combined/` 的模板。改正式模板前，先用 `fixtures/demo/` 的虚构公司看尺寸和溢出。演示数字不能写进正式模板。
- 鸡蛋：独立审图。看预览图和 `python3 scripts/accept-demo.py` 的结果，核对宽度、高度、文字是否溢出、页面是否报错、图上是否仍标着演示数据。审图不代替铲钱官改业务文案。
- 总管：协调分支和验收顺序。默认不合并。没有用户明确要求时，不合并拉取请求，不改 GitHub 默认分支。

## 默认分支

GitHub 默认分支是 `agent/earnings-templates`。功能分支从这里拉出。不要把默认分支改成 `main` 或其他名字，也不要直接向默认分支推送。

## 实际命令

依赖只有系统自带的 `python3`、桌面入口 `/usr/local/bin/google-chrome`，以及无头验收用的 `/usr/bin/google-chrome-stable`。不安装 npm 包，不引入前端框架。

`/usr/local/bin/google-chrome` 是云端镜像上的桌面包装：它固定远程调试端口 9222 和共享配置目录。计算机操作走这个入口。无头验收不要调用它，否则进程不会退出。`scripts/accept-demo.py` 调用 `google-chrome-stable`。

```bash
bash scripts/cloud-install.sh
bash scripts/cloud-install.sh
bash scripts/cloud-start.sh
```

第二条 install 用来确认可以重复执行。`cloud-start.sh` 会占住前台，在 `0.0.0.0:8765` 提供当前目录的静态文件。端口已经开着时，脚本直接退出 0。

另开一个终端做验收：

```bash
python3 scripts/accept-demo.py --out /tmp/earnings-demo-preview
curl -fsS http://127.0.0.1:8765/fixtures/demo/single-poster.html | head
```

验收只打开临时夹具：

- 移动海报视口 `1080×1920`，海报本体 `1080×1920`
- 桌面视口 `1440×1920`，海报仍是 `1080×1920` 并水平居中，两侧留出页边

夹具公司是虚构的「云渚纸鸢 DEMO-YZ」和「北泽灯塔 DEMO-BZ」。金额、目标价、仓位都是合成演示，页面上有「演示数据」。正式模板 `single-company/template.html` 和 `combined/template.html` 不在验收打开范围内。

## 安全边界

- 不读取、不索取、不提交密钥、令牌或私钥。本环境不需要密钥。
- 不连接真实行情、持仓、Futu OpenD 或任何付费接口。
- 不复制其他仓库、Grok Bot 备份或记忆。
- 不运行 `wrangler deploy`，不做外部发布，不建定时任务，不发推送。
- 不安装外部 MCP，不改模型、全局默认仓库、账户支出上限或其他账户设置。
- 不改 GitHub 默认分支，不删除用户已有模板内容。
- 截图和夹具必须能看出是演示数据。正式实际值仍只认公司官方披露；夹具里的数字不是披露。

## Cursor Cloud specific instructions

当前这个个人环境是数据库托管的，`environmentJsonPath` 为空，所以仅仅把 `.cursor/environment.json` 放进仓库不会自动生效。文件按 [Cloud Environment Setup](https://cursor.com/docs/cloud-agent/setup) 的 schema 编写，字段只有 `name`、`install`、`start`、`ports`、`chromeExecutablePath`。没有 snapshot 编号，没有密钥，没有 egress 修改。

`install` 在脚本还不在该修订上时会跳过，避免默认分支还没包含本分支文件时构建失败。脚本存在时只做语法检查和文件存在检查，不装依赖，不跑测试。`start` 只拉起静态预览。构建不会执行 `start`。

计算机操作用默认镜像里的 `/usr/local/bin/google-chrome`。无头验收用 `/usr/bin/google-chrome-stable`。官方 schema 没有单独的字段可以钉死 Chrome 的补丁版本；版本以 `google-chrome-stable --version` 的输出为准。本次不新增 Dockerfile。
