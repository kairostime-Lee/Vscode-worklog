# 专家 A — 支付与账号注册指南
> 主体：香港注册企业（Opula Technology）
> 版本：v1.0 | 日期：2026-04-21

---

## 一、香港公司的核心优势

```
✅ Stripe 香港：直接可用，USD结算，无需美国实体
✅ PayPal 香港商业账户：直接可用
✅ 支付宝 Global：香港企业申请远比大陆简单
✅ 微信支付 Global：香港企业可直接申请
✅ 无外汇管制：资金进出自由，美元直接结算
✅ 香港银行（汇丰/恒生）：可开多币种账户（USD/HKD/RMB）
✅ 税务优势：境外来源收入香港免税（需要税务师确认）
```

---

## 二、Shopify 建站账号注册

```
注册信息填写：
├── Business Country: Hong Kong
├── Business Type: Company
├── Company Name: （你的香港公司名）
├── Store Currency: USD（！重要，不要选HKD，售价是美元）
└── Email: 建议用公司邮件（info@opulatech.com）

Shopify Payments 在香港：
└── ⚠️ Shopify Payments 不支持香港 → 不影响！直接用 Stripe 替代
    效果完全一样，费用相同

Shopify 套餐：
└── Basic：$39/月（1-2个员工账号，够用）
    或趁活动期用 $1/月首月优惠
```

---

## 三、支付账号注册完整清单

### 第一步：银行账户（Day 1，最重要的基础）

```
推荐开户银行（香港）：
├── 首选：汇丰香港（HSBC HK）商业账户
│   ├── 优点：全球认可度最高，Stripe/PayPal对接零问题
│   ├── 开户：网上申请（BusinessConnect），约1-2周
│   └── 需要：BR（商业登记证）+ 公司章程 + 董事ID
│
├── 次选：恒生银行商业账户
│   └── 比汇丰快，约3-5天
│
└── 替代方案（最快，1天内）：
    ├── Airwallex（跨境支付神器）
    │   ├── 可开美国/香港虚拟账户
    │   ├── 直接收 Stripe/PayPal 美元结算
    │   ├── 转人民币汇率好
    │   └── 申请：airwallex.com/hk，香港公司1个工作日审批
    └── Wise Business（同类方案）
        └── 可开美元/港元账户，出海首选

建议：先开 Airwallex，边等汇丰审批边开始运营
```

### 第二步：Stripe（信用卡收款，Day 2）

```
注册地址：dashboard.stripe.com
选择：Hong Kong

需要材料：
├── 香港公司 BR（Business Registration）
├── 董事护照 / HKID
├── 公司银行账户（或 Airwallex 美元账户）
└── 网站地址（Shopify 店铺地址）

费率：
├── 国际信用卡（Visa/MC）：2.9% + $0.30 USD
└── American Express：3.4% + $0.30 USD

审批时间：约 1-2 个工作日
结算：每日自动，T+2 到账美元账户
```

### 第三步：PayPal Business（Day 2）

```
注册地址：paypal.com/hk/business
选择：Business Account（不是 Personal）

需要材料：
├── 香港公司 BR
├── 董事信息
└── 银行账户

重要设置：
├── 提现到美元账户（不要转港元，有汇损）
└── 开启"货款预留"豁免（新账户PayPal会预留资金，需要申请解除）

费率：
└── 接收国际付款：4.4% + 固定费用（较贵，但PayPal用户多）
```

### 第四步：支付宝 Global（Week 2，针对华裔市场）

```
申请渠道（香港公司两种方式）：

方式A：通过 Stripe 集成（最简单！）
├── Stripe 在香港已集成支付宝+微信支付
├── 在 Stripe Dashboard → Payment Methods → 开启 Alipay/WeChat Pay
└── 无需单独申请支付宝商家号！直接用！

费率（通过Stripe）：
├── 支付宝：1.5%（Stripe代收）
└── 微信支付：1.5%（Stripe代收）

方式B：支付宝商家直连（费率更低，流程更复杂）
├── 申请：global.alipay.com/solution/isv.htm
├── 需要：香港营业执照 + 银行证明 + 网站
└── 费率：0.6-1%，到账更快

建议：先用 Stripe 集成（方式A），快速上线，后期再申请直连降低费率
```

### 第五步：微信支付 Global（Week 2）

```
同支付宝，通过 Stripe 直接开启微信支付 
（Stripe 在香港同时支持支付宝和微信支付）

具体操作：
├── Stripe Dashboard
├── Settings → Payment Methods
├── 开启 Alipay → 保存
├── 开启 WeChat Pay → 保存
└── 完成！Shopify 结账页自动出现这两个选项
```

---

## 四、Shopify + Stripe 完整接入步骤

```
Step 1：Shopify 安装 Stripe
├── Shopify Admin → Settings → Payments
├── 点击 "Add payment provider"
├── 选择 Stripe
└── 授权 Stripe 账户

Step 2：在 Stripe 开启支付宝/微信
├── Stripe Dashboard → Settings → Payment Methods
├── Alipay → Enable
└── WeChat Pay → Enable

Step 3：测试结账
├── 用 Shopify 测试模式下单
├── 分别测试：信用卡 / PayPal / 支付宝 / 微信支付
└── 确认收款到 Airwallex/汇丰账户

完成后，你的结账页将同时支持：
✅ Visa / Mastercard / Amex（全球信用卡）
✅ PayPal（约70%美国用户有账户）
✅ Apple Pay / Google Pay（通过Stripe自动支持）
✅ 支付宝（华裔市场）
✅ 微信支付（华裔市场）
```

---

## 五、资金流转路径

```
美国买家付款 → Stripe → Airwallex美元账户 → 按需换汇
华裔买家（支付宝）→ Stripe → Airwallex美元账户
华裔买家（微信支付）→ Stripe → Airwallex美元账户
PayPal买家 → PayPal账户 → 转账到银行

汇丰香港主账户：
├── 日常运营资金
├── 工厂付款（人民币/港元）
└── 税务账期备用金

建议不要全部放在 Stripe/PayPal，定期转到银行
（Stripe 持有大量资金有被冻结风险，特别是新账户）
```

---

## 六、注册时间线

```
Day 1（今天）：
□ 注册 Airwallex 香港商业账户（1天审批）
□ 注册 Shopify（立即可用）

Day 2：
□ 注册 Stripe HK，连接 Airwallex 账户
□ 注册 PayPal Business HK
□ Shopify 安装 Stripe，开启支付宝+微信支付

Day 3-7：
□ 建站、上传产品
□ 全支付方式测试

Week 2：
□ 申请汇丰商业账户（做长期主账户）
□ 如需要，申请支付宝商家直连降低费率
```

---

*香港公司主体非常理想，整个支付体系可在 3 天内搭建完成。*
*更新时间：2026-04-21*
