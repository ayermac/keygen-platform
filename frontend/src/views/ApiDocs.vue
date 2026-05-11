<template>
  <div class="docs-root">
    <!-- Standalone Header -->
    <header class="docs-header">
      <div class="docs-header-inner">
        <div class="docs-logo">
          <div class="logo-icon">K</div>
          <span class="logo-text">Keygen Platform</span>
        </div>
        <div class="docs-nav">
          <span class="docs-nav-active">接入文档</span>
          <a href="/login" class="docs-nav-link">管理后台</a>
        </div>
      </div>
    </header>

    <div class="docs-page">
      <div class="kg-page-header">
        <h1 class="kg-page-title">C 端接入文档</h1>
        <div class="header-actions">
          <el-tag type="success" effect="plain" size="small">v1</el-tag>
          <el-tag type="info" effect="plain" size="small">Base URL: /api/v1</el-tag>
        </div>
      </div>

    <!-- Overview -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><InfoFilled /></el-icon>
          概览
        </h2>
        <div class="section-body">
          <p class="doc-text">
            Keygen Platform 提供 RESTful API 供 C 端业务接入。所有接口通过 <code>X-API-Key</code> 请求头进行认证，
            每个产品拥有独立的 API Key。接口返回统一 JSON 格式，包含 <code>code</code>、<code>message</code>、<code>data</code> 三个字段。
          </p>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">协议</span>
              <span class="info-value">HTTPS / HTTP</span>
            </div>
            <div class="info-item">
              <span class="info-label">编码</span>
              <span class="info-value">UTF-8</span>
            </div>
            <div class="info-item">
              <span class="info-label">Content-Type</span>
              <span class="info-value">application/json</span>
            </div>
            <div class="info-item">
              <span class="info-label">认证方式</span>
              <span class="info-value">X-API-Key Header</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Response Format -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><Document /></el-icon>
          统一响应格式
        </h2>
        <div class="section-body">
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">JSON</span>
              <span class="code-desc">成功响应</span>
            </div>
            <pre><code>{
  "code": 0,
  "message": "success",
  "data": { ... }
}</code></pre>
          </div>
          <div class="code-block error">
            <div class="code-header">
              <span class="code-lang">JSON</span>
              <span class="code-desc">错误响应</span>
            </div>
            <pre><code>{
  "code": 1001,
  "message": "兑换码不存在或不属于该产品",
  "data": null
}</code></pre>
          </div>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>code</code></td>
                  <td>int</td>
                  <td>0 = 成功，非 0 = 错误码</td>
                </tr>
                <tr>
                  <td><code>message</code></td>
                  <td>string</td>
                  <td>成功时为 "success"，失败时为错误描述</td>
                </tr>
                <tr>
                  <td><code>data</code></td>
                  <td>object/null</td>
                  <td>成功时返回业务数据，失败时为 null</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- Auth -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><Lock /></el-icon>
          认证
        </h2>
        <div class="section-body">
          <p class="doc-text">
            所有 C 端接口必须在请求头中携带 <code>X-API-Key</code>。API Key 在后台「产品管理」中创建产品时自动生成，
            格式为 <code>kg_</code> 前缀 + 64 位十六进制字符串。每个 API Key 绑定一个产品，只能操作该产品下的兑换码。
          </p>
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">HTTP</span>
              <span class="code-desc">请求头示例</span>
            </div>
            <pre><code>X-API-Key: kg_2d8dbaea5d49e9ff70ec99566c8af63bac30c7d4ee5457e4c24b130fd475747c</code></pre>
          </div>
          <div class="warning-box">
            <el-icon><Warning /></el-icon>
            <span>API Key 请妥善保管，不要暴露在前端代码或公开仓库中。</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Error Codes -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><WarningFilled /></el-icon>
          错误码一览
        </h2>
        <div class="section-body">
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>错误码</th>
                  <th>含义</th>
                  <th>触发条件</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>0</code></td>
                  <td class="text-success">成功</td>
                  <td>请求正常处理</td>
                </tr>
                <tr>
                  <td><code>1001</code></td>
                  <td class="text-danger">通用错误</td>
                  <td>兑换码不存在、不属于该产品、或其他兑换异常</td>
                </tr>
                <tr>
                  <td><code>1002</code></td>
                  <td class="text-warning">已兑换</td>
                  <td>兑换码已被使用过，重复兑换</td>
                </tr>
                <tr>
                  <td><code>1003</code></td>
                  <td class="text-muted">已过期</td>
                  <td>兑换码已超过有效期</td>
                </tr>
                <tr>
                  <td><code>1004</code></td>
                  <td class="text-danger">已禁用</td>
                  <td>兑换码被管理员禁用</td>
                </tr>
                <tr>
                  <td><code>1101</code></td>
                  <td class="text-danger">消耗通用错误</td>
                  <td>消耗时兑换码异常（未兑换、不存在等）</td>
                </tr>
                <tr>
                  <td><code>1102</code></td>
                  <td class="text-warning">额度不足</td>
                  <td>消耗数量大于剩余额度</td>
                </tr>
                <tr>
                  <td><code>1103</code></td>
                  <td class="text-warning">系统繁忙</td>
                  <td>消耗时获取锁失败，请稍后重试</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- API: Redeem -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><Key /></el-icon>
          兑换兑换码
        </h2>
        <div class="section-body">
          <div class="endpoint-badge">
            <span class="method post">POST</span>
            <code>/api/v1/codes/redeem</code>
          </div>
          <p class="doc-text">兑换一个未使用的兑换码，将其状态变为「已兑换」并记录兑换时间。兑换后才能进行额度消耗。</p>

          <h4 class="sub-title">请求参数</h4>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>必填</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>code</code></td>
                  <td>string</td>
                  <td>是</td>
                  <td>兑换码，格式 <code>XXXX-XXXX-XXXX-XXXX</code></td>
                </tr>
                <tr>
                  <td><code>metadata</code></td>
                  <td>object</td>
                  <td>否</td>
                  <td>自定义上报数据（如设备信息、用户 ID 等）</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 class="sub-title">请求示例</h4>
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">cURL</span>
              <button class="copy-btn" @click="copyCode('redeem-curl')">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
            <pre id="redeem-curl"><code>curl -X POST http://localhost/api/v1/codes/redeem \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "code": "A1B2-C3D4-E5F6-G7H8",
    "metadata": {
      "user_id": "u_12345",
      "device": "iPhone 15"
    }
  }'</code></pre>
          </div>

          <h4 class="sub-title">成功响应</h4>
          <div class="code-block success">
            <div class="code-header">
              <span class="code-lang">JSON</span>
              <span class="code-desc">200 OK</span>
            </div>
            <pre><code>{
  "code": 0,
  "message": "success",
  "data": {
    "code": "A1B2-C3D4-E5F6-G7H8",
    "credit_unit": "积分",
    "total_credits": 100,
    "remaining_credits": 100,
    "expires_at": "2027-05-09T00:00:00"
  }
}</code></pre>
          </div>

          <h4 class="sub-title">响应字段</h4>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>code</code></td>
                  <td>string</td>
                  <td>兑换码</td>
                </tr>
                <tr>
                  <td><code>credit_unit</code></td>
                  <td>string</td>
                  <td>额度单位（如"积分"、"次数"）</td>
                </tr>
                <tr>
                  <td><code>total_credits</code></td>
                  <td>int</td>
                  <td>初始额度总量</td>
                </tr>
                <tr>
                  <td><code>remaining_credits</code></td>
                  <td>int</td>
                  <td>剩余额度</td>
                </tr>
                <tr>
                  <td><code>expires_at</code></td>
                  <td>string|null</td>
                  <td>过期时间，null 表示永不过期</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- API: Consume -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><TrendCharts /></el-icon>
          消耗额度
        </h2>
        <div class="section-body">
          <div class="endpoint-badge">
            <span class="method post">POST</span>
            <code>/api/v1/codes/consume</code>
          </div>
          <p class="doc-text">对已兑换的兑换码消耗指定数量的额度。消耗操作是原子性的，支持并发调用。使用 Redis 分布式锁保证数据一致性。</p>

          <h4 class="sub-title">请求参数</h4>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>必填</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>code</code></td>
                  <td>string</td>
                  <td>是</td>
                  <td>兑换码</td>
                </tr>
                <tr>
                  <td><code>amount</code></td>
                  <td>int</td>
                  <td>是</td>
                  <td>消耗数量，必须 &gt; 0</td>
                </tr>
                <tr>
                  <td><code>metadata</code></td>
                  <td>object</td>
                  <td>否</td>
                  <td>自定义上报数据</td>
                </tr>
                <tr>
                  <td><code>request_id</code></td>
                  <td>string</td>
                  <td>否</td>
                  <td>幂等请求 ID（最长 128 字符）。相同 ID 仅扣减一次，防止客户端重试导致重复扣减</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 class="sub-title">请求示例</h4>
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">cURL</span>
              <button class="copy-btn" @click="copyCode('consume-curl')">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
            <pre id="consume-curl"><code>curl -X POST http://localhost/api/v1/codes/consume \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "code": "A1B2-C3D4-E5F6-G7H8",
    "amount": 10,
    "request_id": "order-20260511-001",
    "metadata": {
      "action": "generate_image",
      "model": "dall-e-3"
    }
  }'</code></pre>
          </div>

          <h4 class="sub-title">成功响应</h4>
          <div class="code-block success">
            <div class="code-header">
              <span class="code-lang">JSON</span>
              <span class="code-desc">200 OK</span>
            </div>
            <pre><code>{
  "code": 0,
  "message": "success",
  "data": {
    "remaining_credits": 90
  }
}</code></pre>
          </div>

          <h4 class="sub-title">响应字段</h4>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>remaining_credits</code></td>
                  <td>int</td>
                  <td>消耗后的剩余额度</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="warning-box">
            <el-icon><Warning /></el-icon>
            <span>消耗数量必须大于 0，否则返回 422 参数校验错误。消耗大于剩余额度时返回错误码 1102。传递 <code>request_id</code> 可防止重试导致的重复扣减。</span>
          </div>
        </div>
      </div>
    </section>

    <!-- API: Balance -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><Wallet /></el-icon>
          查询余额
        </h2>
        <div class="section-body">
          <div class="endpoint-badge">
            <span class="method post">POST</span>
            <code>/api/v1/codes/balance</code>
          </div>
          <p class="doc-text">查询兑换码的当前状态和剩余额度。即使未兑换的码也可以查询（返回初始额度）。此接口会检查过期状态并懒更新。</p>

          <h4 class="sub-title">请求参数</h4>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>必填</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>code</code></td>
                  <td>string</td>
                  <td>是</td>
                  <td>兑换码</td>
                </tr>
                <tr>
                  <td><code>metadata</code></td>
                  <td>object</td>
                  <td>否</td>
                  <td>自定义上报数据</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 class="sub-title">请求示例</h4>
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">cURL</span>
              <button class="copy-btn" @click="copyCode('balance-curl')">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
            <pre id="balance-curl"><code>curl -X POST http://localhost/api/v1/codes/balance \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "code": "A1B2-C3D4-E5F6-G7H8"
  }'</code></pre>
          </div>

          <h4 class="sub-title">成功响应</h4>
          <div class="code-block success">
            <div class="code-header">
              <span class="code-lang">JSON</span>
              <span class="code-desc">200 OK</span>
            </div>
            <pre><code>{
  "code": 0,
  "message": "success",
  "data": {
    "code": "A1B2-C3D4-E5F6-G7H8",
    "credit_unit": "积分",
    "total_credits": 100,
    "remaining_credits": 90,
    "status": "activated",
    "expires_at": "2027-05-09T00:00:00"
  }
}</code></pre>
          </div>

          <h4 class="sub-title">响应字段</h4>
          <div class="field-table">
            <table>
              <thead>
                <tr>
                  <th>字段</th>
                  <th>类型</th>
                  <th>说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>code</code></td>
                  <td>string</td>
                  <td>兑换码</td>
                </tr>
                <tr>
                  <td><code>credit_unit</code></td>
                  <td>string</td>
                  <td>额度单位</td>
                </tr>
                <tr>
                  <td><code>total_credits</code></td>
                  <td>int</td>
                  <td>初始额度总量</td>
                </tr>
                <tr>
                  <td><code>remaining_credits</code></td>
                  <td>int</td>
                  <td>剩余额度</td>
                </tr>
                <tr>
                  <td><code>status</code></td>
                  <td>string</td>
                  <td>unused / activated / expired / disabled</td>
                </tr>
                <tr>
                  <td><code>expires_at</code></td>
                  <td>string|null</td>
                  <td>过期时间</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>

    <!-- Integration Guide -->
    <section class="doc-section">
      <div class="section-card">
        <h2 class="section-title">
          <el-icon><Connection /></el-icon>
          接入指南
        </h2>
        <div class="section-body">
          <h3 class="sub-title">典型业务流程</h3>
          <div class="flow-steps">
            <div class="flow-step">
              <div class="flow-num">1</div>
              <div class="flow-content">
                <div class="flow-title">用户获得兑换码</div>
                <div class="flow-desc">通过购买、发放等渠道获取 <code>XXXX-XXXX-XXXX-XXXX</code> 格式的兑换码</div>
              </div>
            </div>
            <div class="flow-arrow">
              <el-icon><ArrowDown /></el-icon>
            </div>
            <div class="flow-step">
              <div class="flow-num">2</div>
              <div class="flow-content">
                <div class="flow-title">调用兑换接口</div>
                <div class="flow-desc">用户在你的产品中输入兑换码，后端调用 <code>POST /codes/redeem</code> 完成兑换</div>
              </div>
            </div>
            <div class="flow-arrow">
              <el-icon><ArrowDown /></el-icon>
            </div>
            <div class="flow-step">
              <div class="flow-num">3</div>
              <div class="flow-content">
                <div class="flow-title">业务消费时消耗</div>
                <div class="flow-desc">用户每次使用付费功能时，调用 <code>POST /codes/consume</code> 消耗对应额度</div>
              </div>
            </div>
            <div class="flow-arrow">
              <el-icon><ArrowDown /></el-icon>
            </div>
            <div class="flow-step">
              <div class="flow-num">4</div>
              <div class="flow-content">
                <div class="flow-title">查询剩余额度</div>
                <div class="flow-desc">可随时调用 <code>POST /codes/balance</code> 展示用户剩余额度</div>
              </div>
            </div>
          </div>

          <h3 class="sub-title" style="margin-top: 32px;">Python 接入示例</h3>
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">Python</span>
              <button class="copy-btn" @click="copyCode('python-example')">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
            <pre id="python-example"><code>import httpx

API_BASE = "http://localhost/api/v1"
API_KEY = "kg_your_api_key_here"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}

def redeem_code(code: str) -> dict:
    """兑换一个兑换码"""
    resp = httpx.post(
        f"{API_BASE}/codes/redeem",
        json={"code": code},
        headers=headers,
    )
    return resp.json()

def consume_credits(code: str, amount: int, request_id: str | None = None) -> dict:
    """消耗额度，request_id 可防止重试重复扣减"""
    payload = {"code": code, "amount": amount}
    if request_id:
        payload["request_id"] = request_id
    resp = httpx.post(
        f"{API_BASE}/codes/consume",
        json=payload,
        headers=headers,
    )
    return resp.json()

def get_balance(code: str) -> dict:
    """查询余额"""
    resp = httpx.post(
        f"{API_BASE}/codes/balance",
        json={"code": code},
        headers=headers,
    )
    return resp.json()

# 使用示例
result = redeem_code("A1B2-C3D4-E5F6-G7H8")
if result["code"] == 0:
    print(f"兑换成功，剩余额度: {result['data']['remaining_credits']}")
else:
    print(f"兑换失败: {result['message']}")</code></pre>
          </div>

          <h3 class="sub-title" style="margin-top: 32px;">JavaScript / Node.js 接入示例</h3>
          <div class="code-block">
            <div class="code-header">
              <span class="code-lang">JavaScript</span>
              <button class="copy-btn" @click="copyCode('js-example')">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
            <pre id="js-example"><code>const API_BASE = "http://localhost/api/v1";
const API_KEY = "kg_your_api_key_here";

const headers = {
  "X-API-Key": API_KEY,
  "Content-Type": "application/json",
};

async function redeemCode(code) {
  const resp = await fetch(`${API_BASE}/codes/redeem`, {
    method: "POST",
    headers,
    body: JSON.stringify({ code }),
  });
  return resp.json();
}

async function consumeCredits(code, amount, requestId) {
  const payload = { code, amount };
  if (requestId) payload.request_id = requestId;
  const resp = await fetch(`${API_BASE}/codes/consume`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  return resp.json();
}

async function getBalance(code) {
  const resp = await fetch(`${API_BASE}/codes/balance`, {
    method: "POST",
    headers,
    body: JSON.stringify({ code }),
  });
  return resp.json();
}

// 使用示例
const result = await redeemCode("A1B2-C3D4-E5F6-G7H8");
if (result.code === 0) {
  console.log(`兑换成功，剩余额度: ${result.data.remaining_credits}`);
} else {
  console.error(`兑换失败: ${result.message}`);
}</code></pre>
          </div>

          <h3 class="sub-title" style="margin-top: 32px;">Agent 接入要点</h3>
          <div class="agent-notes">
            <div class="agent-note">
              <div class="note-icon">1</div>
              <div class="note-content">
                <strong>认证：</strong>所有请求必须携带 <code>X-API-Key</code> 头，值为产品的 API Key
              </div>
            </div>
            <div class="agent-note">
              <div class="note-icon">2</div>
              <div class="note-content">
                <strong>幂等性：</strong>兑换接口非幂等（重复调用返回 1002）。消耗接口支持通过 <code>request_id</code> 实现幂等：相同 ID 仅扣减一次并返回首次结果，适合网络重试场景。不传 <code>request_id</code> 则保持原行为
              </div>
            </div>
            <div class="agent-note">
              <div class="note-icon">3</div>
              <div class="note-content">
                <strong>错误处理：</strong>先检查 <code>code === 0</code>，再读取 <code>data</code>；非 0 时根据错误码决定重试策略
              </div>
            </div>
            <div class="agent-note">
              <div class="note-icon">4</div>
              <div class="note-content">
                <strong>并发安全：</strong>消耗接口使用 Redis 分布式锁，可安全并发调用；遇到 1103 错误时可重试
              </div>
            </div>
            <div class="agent-note">
              <div class="note-icon">5</div>
              <div class="note-content">
                <strong>metadata：</strong>所有接口支持 <code>metadata</code> 字段，可用于传递上下文信息（用户 ID、设备、操作类型等），便于审计追踪
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'

function copyCode(elementId: string) {
  const el = document.getElementById(elementId)
  if (el) {
    navigator.clipboard.writeText(el.textContent || '')
    ElMessage.success('已复制到剪贴板')
  }
}
</script>

<style scoped>
.docs-root {
  min-height: 100vh;
  background: var(--kg-bg);
}

/* ---- Standalone Header ---- */
.docs-header {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
}

.docs-header-inner {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.docs-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.docs-logo .logo-icon {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 800;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.docs-logo .logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.025em;
}

.docs-nav {
  display: flex;
  align-items: center;
  gap: 24px;
}

.docs-nav-active {
  font-size: 14px;
  font-weight: 600;
  color: #a5b4fc;
}

.docs-nav-link {
  font-size: 14px;
  font-weight: 500;
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s ease;
}

.docs-nav-link:hover {
  color: #e2e8f0;
}

/* ---- Page Content ---- */
.docs-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 32px 64px;
}

.docs-page .kg-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.docs-page .kg-page-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--kg-text);
  letter-spacing: -0.03em;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* ---- Section ---- */
.doc-section {
  margin-bottom: 20px;
}

.section-card {
  background: var(--kg-surface);
  border: 1px solid var(--kg-border);
  border-radius: 14px;
  overflow: hidden;
  animation: fadeInUp 0.4s ease both;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 700;
  color: var(--kg-text);
  padding: 20px 24px;
  border-bottom: 1px solid var(--kg-border);
  margin: 0;
}

.section-title .el-icon {
  color: var(--kg-primary);
}

.section-body {
  padding: 24px;
}

.sub-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--kg-text);
  margin: 0 0 12px 0;
}

/* ---- Text ---- */
.doc-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--kg-text-secondary);
  margin-bottom: 16px;
}

.doc-text code,
.field-table code,
.flow-desc code,
.note-content code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  background: var(--kg-primary-bg);
  color: var(--kg-primary);
  padding: 2px 6px;
  border-radius: 4px;
}

/* ---- Info Grid ---- */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.info-item {
  background: var(--kg-bg);
  border-radius: 10px;
  padding: 14px;
  text-align: center;
}

.info-label {
  display: block;
  font-size: 12px;
  color: var(--kg-text-muted);
  margin-bottom: 6px;
}

.info-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--kg-text);
}

/* ---- Code Block ---- */
.code-block {
  border: 1px solid var(--kg-border);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 16px;
  background: #1e293b;
}

.code-block.success {
  border-color: rgba(16, 185, 129, 0.2);
}

.code-block.error {
  border-color: rgba(239, 68, 68, 0.2);
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.code-lang {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.code-desc {
  font-size: 12px;
  color: #64748b;
}

.copy-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
}

.copy-btn:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.06);
}

.code-block pre {
  margin: 0;
  padding: 16px;
  overflow-x: auto;
}

.code-block code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #e2e8f0;
}

/* ---- Field Table ---- */
.field-table {
  overflow-x: auto;
  margin-bottom: 16px;
}

.field-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.field-table th {
  text-align: left;
  padding: 10px 14px;
  background: var(--kg-bg);
  color: var(--kg-text-secondary);
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  border-bottom: 1px solid var(--kg-border);
}

.field-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--kg-border);
  color: var(--kg-text);
}

.field-table tr:last-child td {
  border-bottom: none;
}

.text-success { color: var(--kg-success); font-weight: 500; }
.text-danger { color: var(--kg-danger); font-weight: 500; }
.text-warning { color: var(--kg-warning); font-weight: 500; }
.text-muted { color: var(--kg-text-muted); font-weight: 500; }

/* ---- Endpoint Badge ---- */
.endpoint-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--kg-bg);
  border: 1px solid var(--kg-border);
  border-radius: 8px;
  padding: 8px 14px;
  margin-bottom: 16px;
}

.method {
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.method.post {
  background: #dcfce7;
  color: #16a34a;
}

.method.get {
  background: #dbeafe;
  color: #2563eb;
}

.endpoint-badge code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--kg-text);
  background: transparent;
  padding: 0;
}

/* ---- Warning Box ---- */
.warning-box {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 13px;
  color: #92400e;
  line-height: 1.5;
}

.warning-box .el-icon {
  color: #f59e0b;
  margin-top: 1px;
  flex-shrink: 0;
}

/* ---- Flow Steps ---- */
.flow-steps {
  display: flex;
  flex-direction: column;
}

.flow-step {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  background: var(--kg-bg);
  border-radius: 10px;
  transition: all 0.2s ease;
}

.flow-step:hover {
  background: var(--kg-primary-bg);
}

.flow-num {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.flow-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--kg-text);
  margin-bottom: 4px;
}

.flow-desc {
  font-size: 13px;
  color: var(--kg-text-secondary);
  line-height: 1.5;
}

.flow-arrow {
  display: flex;
  justify-content: center;
  padding: 4px 0;
  color: var(--kg-text-muted);
}

/* ---- Agent Notes ---- */
.agent-notes {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.agent-note {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  background: var(--kg-bg);
  border-radius: 8px;
  border-left: 3px solid var(--kg-primary);
}

.note-icon {
  width: 24px;
  height: 24px;
  background: var(--kg-primary-bg);
  color: var(--kg-primary);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.note-content {
  font-size: 13px;
  color: var(--kg-text);
  line-height: 1.6;
}

.note-content strong {
  color: var(--kg-text);
}

/* ---- Animation ---- */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.doc-section:nth-child(1) .section-card { animation-delay: 0ms; }
.doc-section:nth-child(2) .section-card { animation-delay: 60ms; }
.doc-section:nth-child(3) .section-card { animation-delay: 120ms; }
.doc-section:nth-child(4) .section-card { animation-delay: 180ms; }
.doc-section:nth-child(5) .section-card { animation-delay: 240ms; }
.doc-section:nth-child(6) .section-card { animation-delay: 300ms; }
.doc-section:nth-child(7) .section-card { animation-delay: 360ms; }
.doc-section:nth-child(8) .section-card { animation-delay: 420ms; }

/* ---- Responsive ---- */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
