# Earnings Sell-Side Flash Templates

两套财报图模板，供财报预告和正式验证使用。页面尺寸固定为 1080×1920，默认霞鹜文楷风格。

## 模板

- [单公司模板](./single-company/template.html) / [raw](https://raw.githubusercontent.com/iroryagame-afk/earnings-templates/main/single-company/template.html)
- [多公司合并模板](./combined/template.html) / [raw](https://raw.githubusercontent.com/iroryagame-afk/earnings-templates/main/combined/template.html)

## 固定字段

每家公司都必须独立展示：

1. 卖方预估 / 一致预期
2. 公开 Whisper（无可靠值时写“无可靠 Whisper”）
3. 正式实际值（未公布时写“待公布 / 待回读”）
4. 财报前锁定的真正 Beat 线
5. 核心经营指标
6. 前瞻指引
7. ✓ 达标 / △ 部分达标 / ✕ 未达标 / □ 待回读
8. 卖方预测修正方向
9. 已有仓位与新资金分栏
10. 上行催化、失效条件、三档目标价

合并图在逐公司模块之后增加横向排序、交叉读数和新资金优先级，不能用总括文字替代逐公司验收。

## 数据边界

- 正式实际值只认公司官方 IR、交易所、SEC 或法定披露。
- 不能用媒体、聚合页或传闻替代正式结果。
- Futu OpenD 未连接时，不填写猜测价格、目标位或提醒点位。
- 财报前锁定的 Beat 线在财报后不得移动。

文件中的 TTWO / ACMR 内容是排版示例，使用时替换公司、期间和数值，保留字段顺序与勾叉逻辑。
