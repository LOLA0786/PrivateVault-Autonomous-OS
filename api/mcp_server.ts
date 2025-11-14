import 'dotenv/config';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import OpenAI from 'openai';
import { z } from 'zod';
import express from 'express';

// ---------- 1. LLM clients ----------
const grok = new OpenAI({
  apiKey: process.env.GROK_API_KEY,
  baseURL: 'https://api.x.ai/v1',
});

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// ---------- 2. MCP server ----------
const server = new McpServer({
  name: 'PrivateVault-GrokMCP',
  version: '1.0',
});

// ---------- 3. TOOL: Grok trade eval ----------
server.registerTool(
  'evaluate_trade_grok',
  {
    title: 'Grok Trade Evaluator',
    description: 'Ask Grok to evaluate a trade value',
    inputSchema: z.object({ value: z.number() }),
    outputSchema: z.object({
      accepted: z.boolean(),
      boosted_value: z.number(),
      reason: z.string(),
    }),
  },
  async (input) => {
    const resp = await grok.chat.completions.create({
      model: 'grok-4',
      messages: [
        { role: 'user', content: `Eval trade ${input.value}. JSON only: {"accepted": true, "boosted_value": 60.5, "reason": "strong"}` }
      ],
      max_tokens: 100,
    });
    try {
      return JSON.parse(resp.choices[0].message.content.trim());
    } catch {
      return { accepted: true, boosted_value: input.value * 1.1, reason: 'Grok fallback' };
    }
  }
);

// ---------- 4. TOOL: OpenAI fallback ----------
server.registerTool(
  'fallback_consume',
  {
    title: 'OpenAI Booster',
    description: 'Boost data with OpenAI',
    inputSchema: z.object({}),
    outputSchema: z.object({ boosted: z.number(), tip: z.string() }),
  },
  async () => {
    const resp = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: 'Return: {"boosted": 1.2, "tip": "AI tip"}' }],
    });
    try {
      return JSON.parse(resp.choices[0].message.content.trim());
    } catch {
      return { boosted: 1.2, tip: 'OpenAI fallback' };
    }
  }
);

// ---------- 5. HTTP Server ----------
const app = express();
app.use(express.json());

app.post('/mcp', async (req, res) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });
  res.on('close', () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`MCP HTTP server running on http://localhost:${PORT}/mcp`);
  console.log(`Tools: evaluate_trade_grok, fallback_consume`);
});
