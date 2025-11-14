import 'dotenv/config';
import fetch from 'node-fetch';

async function callTool(tool: string, params: any = {}) {
  const response = await fetch('http://localhost:8080/mcp', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Accept': 'application/json, text/event-stream'  // <-- MCP REQUIRED: Both types
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: tool,
      params
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }

  const data = await response.json();
  if (data.error) throw new Error(`MCP Error: ${data.error.message}`);
  return data.result;
}

// Test 1: Grok
(async () => {
  console.log('\n=== Testing Grok Trade Eval ===');
  try {
    const r = await callTool('evaluate_trade_grok', { value: 55 });
    console.log('SUCCESS:', JSON.stringify(r, null, 2));
  } catch (e: any) {
    console.error('FAILED:', e.message);
  }
})();

// Test 2: OpenAI
setTimeout(async () => {
  console.log('\n=== Testing OpenAI Fallback ===');
  try {
    const r = await callTool('fallback_consume');
    console.log('SUCCESS:', JSON.stringify(r, null, 2));
  } catch (e: any) {
    console.error('FAILED:', e.message);
  }
}, 2000);
