在生物信息学报告整合工具 **MultiQC**（自 v1.27 版本起）中，官方引入了 **AI 报告摘要（AI summaries）** 功能。该功能允许通过大语言模型（LLM）API 对质控数据、图表和表格进行分析，自动生成精简的“执行摘要”或“深度建议”。

MultiQC 支持接入的底层大模型服务商包括 **Seqera AI**、**OpenAI**、**Anthropic** 和 **AWS Bedrock**。以下是其具体的 API 接入与配置方法：

---

## 1. 认证配置（配置 API 密匙）

MultiQC 需要通过环境变量读取对应平台的 API 密钥（Key）来调取大模型。在运行 MultiQC 之前，你需要在终端中导出对应服务商的系统变量：

* **Seqera AI** (默认服务商):
```bash
export SEQERA_AI_BASE_URL="https://..." # 如果使用私有部署
# 或是通过 Seqera 平台的认证接入

```


* **OpenAI**:
```bash
export OPENAI_API_KEY="sk-...你的OpenAI密钥"
export OPENAI_BASE_URL="https://api.openai.com/v1" # 支持配置自定义/代理端点

```


* **Anthropic**:
```bash
export ANTHROPIC_API_KEY="sk-ant-...你的Anthropic密钥"

```


* **AWS Bedrock**:
需要配置 AWS 的标准凭证环境（如 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_DEFAULT_REGION`）。

---

## 2. 方式一：在命令行（CLI）中直接接入

在执行 `multiqc` 命令扫描日志并生成报告时，可以直接附加 AI 相关的参数：

```bash
# 示例 1：使用默认的 Seqera AI 生成简短摘要
multiqc . --ai

# 示例 2：使用 OpenAI 生成包含深度分析与建议的完整报告摘要
multiqc . --ai-summary-full --ai-provider openai

```

**常用命令行参数说明：**

| 参数 | 说明 |
| --- | --- |
| `--ai` / `--ai-summary` | 快速生成简短摘要，展示在 HTML 报告的最上方。 |
| `--ai-summary-full` | 生成包含问题排查、推荐优化动作的详细版本（耗时稍长）。 |
| `--ai-provider <provider>` | 指定模型供应商。可选：`seqera`, `openai`, `anthropic`, `aws_bedrock`（默认：`seqera`）。 |
| `--no-ai` | 完全禁用报告中的 AI 工具箱及任何在线交互按钮。 |

---

## 3. 方式二：在配置文件中持久化接入

如果不想每次都输入命令行参数，可以在 MultiQC 的配置文件 `multiqc_config.yaml` 中进行如下声明：

```yaml
# multiqc_config.yaml
ai_summary: true        # 开启简短摘要生成（对应 --ai）
ai_summary_full: false  # 是否开启深度全量摘要
ai_provider: "openai"   # 指定服务商
# 可选：如果你使用 OpenAI，还可以指定具体的模型
openai_model: "gpt-4o"  
no_ai: false            # 是否完全隐藏前端 AI 组件

```

---

## 4. 方式三：在 HTML 报告前端动态接入（交互式）

即使在运行 MultiQC 时没有在后台调用 API 生成静态文本，MultiQC 也会默认在生成的 HTML 报告右侧工具栏（Toolbox）中嵌入一个 AI 面板。

1. **按需生成**：报告查看者可以打开右侧的 AI 选项卡。
2. **输入密钥**：直接在网页端输入自己的 OpenAI/Anthropic API Key（该 Key 仅保存在浏览器的 `localStorage` 中，不会上传至 MultiQC 官方服务器）。
3. **点击生成**：页面会自动将报告中的 `General Statistics` 等关键表格转化为 Prompt，动态请求大模型并在前端渲染出分析结果。

---

## 5. 提示词（Prompt）与数据隐私优化

由于大模型的 Context 窗口限制及数据隐私考虑，MultiQC 在调用 API 接入时做了以下工程化处理：

* **Prompt 裁剪优化**：如果报告中的样本极多导致数据量过大，MultiQC 会自动启动裁剪逻辑。它会优先尝试打包全量数据；若超出 Token 限制，则退化为仅打包 `General Statistics` 表格；若依然超限，则移除隐藏列或终止请求。
* **样本匿名化**：支持在向大模型发送请求前，自动模糊或匿名化（Anonymize）图表及表格中的真实样本名称（如转为 `Sample_1`, `Sample_2`），以防实验室敏感数据泄露。