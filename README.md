# 链上筹码分析 Skill

面向 Solana Meme / 事件币的资金流与筹码结构分析技能。

输入一个 CA 后，技能会结合实时市场数据、固定钱包群余额变化、钱包资金路径和 AMM 数学，回答：

- 谁在卖、谁在接；
- 原始大户是在派发还是继续锁仓；
- 新大户是真实方向资金、自动建仓、做市库存，还是潜在协同操盘钱包；
- 筹码正在集中、分散，还是发生换庄；
- “新庄吸筹”和“资金快车”需要哪些证据才能成立；
- 后续上涨、震荡和下跌分别由什么链上信号触发。

## 核心原则

- 资金变化优先于静态 Top 持仓。
- 固定追踪同一批旧大户，掉出 Top 榜不等于余额清零。
- Organic 不等于散户，Fresh 不等于项目方。
- 公共 relayer、solver 或 co-signer 不证明钱包属于同一控制人。
- 池子变化只用于衡量净流和价格冲击，不能证明是谁在卖。
- 必须同时找出卖方与承接方，区分原始巨鲸、旧中型鲸鱼、新战略鲸鱼和高频库存。
- “新庄”“隐藏项目方”属于待验证假设，不能写成已确认身份。

## 使用

在 Codex 中直接调用：

```text
用 $analyze-meme-coin-capital-flow 分析这个 CA 现在谁在卖、谁在接、是否换庄吸筹。
```

技能也会在用户询问 Meme 币资金流、筹码结构、Fresh 钱包、机器人、项目方钱包、鲸鱼换手或 AMM 冲击时被自动发现。

## 安装

将仓库克隆到个人 Codex 技能目录：

```powershell
git clone https://github.com/zexichen1407-code/onchain-chip-analysis-skill.git "$env:USERPROFILE\.codex\skills\analyze-meme-coin-capital-flow"
```

技能入口为 `SKILL.md`。`scripts/chip_flow.py` 用于确定性计算固定钱包群的增减仓、集中度变化及常数乘积池价格冲击。

## 计算脚本

运行内置自测：

```powershell
py scripts/chip_flow.py --self-test
```

分析准备好的两期快照：

```powershell
py scripts/chip_flow.py snapshot.json --sell-size 5000000 --sell-size 10000000 --buy-size 5000000
```

脚本要求每个跟踪钱包同时提供 `previous` 和 `current` 余额，避免把缺失钱包误判为清仓。

## 边界

该技能分析链上行为，不证明钱包的现实身份，也不提供确定性收益承诺。实时结论必须标明数据截止时间，并区分已确认事实、行为推断、假设和未知项。
