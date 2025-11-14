require('dotenv').config();
const { MCPServer } = require('@modelcontextprotocol/sdk');
const OpenAI = require('openai');

// ---------- 1. LLM clients ----------
const grok = new OpenAI({
  apiKey: process.env.GROK_API_KEY,
  baseURL: 'https://api.x.ai/v1',
});

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// ---------- 2. MCP server ----------
const server = new MCPServer({
  name: 'PrivateVault-GrokMCP',
  version: '1.0',
});

// ---------- 3. TOOL: Grok trade eval ----------
server.addTool({
  name: 'evaluate_trade_grok',
  description: 'Ask Grok to evaluate a trade value and return JSON',
  parameters: {
    type: 'object',
    properties: { value: { type: 'number', description: 'Trade value' } },
    required: ['value'],
  },
  execute: async ({ value }) => {
    const resp = await grok.chat.completions.create({
      model: 'grok-4',
      messages: [
        {
          role: 'user',
          content: `Eval trade value ${value}. Respond **only** with valid JSON: {"accepted": true|false, "boosted_value": number, "reason": "short text"}`,
        },
      ],
      max_tokens: 120,
    });

    const txt = resp.choices[0].message.content.trim();
    try {
      return JSON.parse(txt);
    } catch (e) {
      return { accepted: true, boosted_value: value * 1.1, reason: 'Grok parse error – default boost' };
    }
  },
});

// ---------- 4. TOOL: OpenAI fallback ----------
server.addTool({
  name: 'fallback_consume',
  description: 'OpenAI (gpt-4o-mini) boost for consumed data',
  parameters: { type: 'object', properties: {} },
  execute: async () => {
    const resp = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Boost a value 1.2× and give a one-line tip. Return JSON: {"boosted": number, "tip": "text"}' }],
      max_tokens: 80,
    });
    const txt = resp.choices[0].message.content.trim();
    try {
      return JSON.parse(txt);
    } catch (e) {
      return { boosted: 1.2, tip: 'OpenAI parse error – default 1.2×' };
    }
  },
});

// ---------- 5. Start server (stdio) ----------
server.start({ transport: 'stdio' });
console.log('MCP server running – waiting for tool calls…');
