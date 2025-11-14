require('dotenv').config();
const { spawn } = require('child_process');

async function callTool(tool, params = {}) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', ['mcp_server.js'], { stdio: ['pipe', 'pipe', 'pipe'] });
    let out = '', err = '';

    proc.stdout.on('data', d => out += d);
    proc.stderr.on('data', d => err += d);

    const req = JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: tool,
      params
    }) + '\n';
    proc.stdin.write(req);
    proc.stdin.end();

    proc.on('close', code => {
      if (code === 0 && out.trim()) {
        try { resolve(JSON.parse(out.trim())); }
        catch (e) { reject(new Error('Parse error: ' + e.message)); }
      } else {
        reject(new Error('MCP error: ' + err));
      }
    });
  });
}

// ---- Test 1: Grok ----
(async () => {
  console.log('\n=== Grok Trade Eval ===');
  try {
    const r = await callTool('evaluate_trade_grok', { value: 55 });
    console.log('Success:', JSON.stringify(r, null, 2));
  } catch (e) { console.error('Failed:', e.message); }
})();

// ---- Test 2: OpenAI ----
setTimeout(async () => {
  console.log('\n=== OpenAI Fallback ===');
  try {
    const r = await callTool('fallback_consume');
    console.log('Success:', JSON.stringify(r, null, 2));
  } catch (e) { console.error('Failed:', e.message); }
}, 1500);
