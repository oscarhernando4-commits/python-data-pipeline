const path = require('path');
process.env.DOTENV_KEY = '';
require('dotenv').config({ path: path.join(__dirname, '.env'), quiet: true });
// Ensure stdout is clean for MCP stdio protocol
console.log = (...args) => console.error(...args);

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const axios = require('axios');
const crypto = require('crypto');

function getApiKey() {
  return process.env.BINANCE_API_KEY;
}

function getApiSecret() {
  return process.env.BINANCE_API_SECRET;
}

function getBaseUrl() {
  return process.env.BINANCE_TESTNET === 'true'
    ? 'https://testnet.binance.vision'
    : 'https://api.binance.com';
}

function signQuery(queryString) {
  const secret = getApiSecret();
  if (!secret) {
    throw new Error('BINANCE_API_SECRET is missing from environment variables');
  }
  return crypto
    .createHmac('sha256', secret)
    .update(queryString)
    .digest('hex');
}

async function binancePublicRequest(endpoint, params = {}) {
  const url = `${getBaseUrl()}${endpoint}`;
  const response = await axios.get(url, { params });
  return response.data;
}

async function binanceSignedRequest(method, endpoint, params = {}) {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('BINANCE_API_KEY is missing from environment variables');
  }
  const timestamp = Date.now();
  const queryParams = { ...params, timestamp };
  const queryString = new URLSearchParams(queryParams).toString();
  const signature = signQuery(queryString);
  const fullQueryString = `${queryString}&signature=${signature}`;

  const url = `${getBaseUrl()}${endpoint}?${fullQueryString}`;
  const response = await axios({
    method,
    url,
    headers: {
      'X-MBX-APIKEY': apiKey,
    },
  });
  return response.data;
}

const server = new Server(
  {
    name: 'binance-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'binance_get_account_balance',
        description: 'Get spot account balances (shows balances greater than zero by default)',
        inputSchema: {
          type: 'object',
          properties: {
            showZeroBalances: {
              type: 'boolean',
              description: 'Whether to show assets with 0 balance (default false)',
            },
          },
        },
      },
      {
        name: 'binance_get_symbol_price',
        description: 'Get current ticker price for a symbol (e.g. USDCUSDT, BTCUSDT) or all symbols if omitted',
        inputSchema: {
          type: 'object',
          properties: {
            symbol: {
              type: 'string',
              description: 'Trading pair symbol (e.g. USDCUSDT, BTCUSDT)',
            },
          },
        },
      },
      {
        name: 'binance_get_order_book',
        description: 'Get order book bids and asks depth for a symbol',
        inputSchema: {
          type: 'object',
          properties: {
            symbol: {
              type: 'string',
              description: 'Trading pair symbol (e.g. USDCUSDT)',
            },
            limit: {
              type: 'number',
              description: 'Default 100; max 5000. Valid values: 5, 10, 20, 50, 100, 500, 1000, 5000',
            },
          },
          required: ['symbol'],
        },
      },
      {
        name: 'binance_get_klines',
        description: 'Get candlestick/OHLCV data for a symbol',
        inputSchema: {
          type: 'object',
          properties: {
            symbol: {
              type: 'string',
              description: 'Trading pair symbol (e.g. USDCUSDT)',
            },
            interval: {
              type: 'string',
              description: 'Interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M',
            },
            limit: {
              type: 'number',
              description: 'Default 500; max 1000',
            },
          },
          required: ['symbol', 'interval'],
        },
      },
      {
        name: 'binance_create_spot_order',
        description: 'Create a spot trading order (BUY or SELL)',
        inputSchema: {
          type: 'object',
          properties: {
            symbol: {
              type: 'string',
              description: 'Trading pair symbol (e.g. USDCUSDT)',
            },
            side: {
              type: 'string',
              enum: ['BUY', 'SELL'],
              description: 'Order side',
            },
            type: {
              type: 'string',
              enum: ['LIMIT', 'MARKET'],
              description: 'Order type',
            },
            quantity: {
              type: 'number',
              description: 'Quantity of base asset to buy/sell',
            },
            price: {
              type: 'number',
              description: 'Price (required for LIMIT orders)',
            },
            timeInForce: {
              type: 'string',
              enum: ['GTC', 'IOC', 'FOK'],
              description: 'Time in force for LIMIT orders (default GTC)',
            },
          },
          required: ['symbol', 'side', 'type', 'quantity'],
        },
      },
      {
        name: 'binance_get_open_orders',
        description: 'Get all open spot orders',
        inputSchema: {
          type: 'object',
          properties: {
            symbol: {
              type: 'string',
              description: 'Trading pair symbol (optional)',
            },
          },
        },
      },
      {
        name: 'binance_cancel_order',
        description: 'Cancel an active spot order',
        inputSchema: {
          type: 'object',
          properties: {
            symbol: {
              type: 'string',
              description: 'Trading pair symbol',
            },
            orderId: {
              type: 'number',
              description: 'Order ID to cancel',
            },
          },
          required: ['symbol', 'orderId'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'binance_get_account_balance') {
      const data = await binanceSignedRequest('GET', '/api/v3/account');
      let balances = data.balances;
      if (!args?.showZeroBalances) {
        balances = balances.filter(
          (b) => parseFloat(b.free) > 0 || parseFloat(b.locked) > 0
        );
      }
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({ accountType: data.accountType, balances }, null, 2),
          },
        ],
      };
    }

    if (name === 'binance_get_symbol_price') {
      const params = args?.symbol ? { symbol: args.symbol.toUpperCase() } : {};
      const data = await binancePublicRequest('/api/v3/ticker/price', params);
      return {
        content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
      };
    }

    if (name === 'binance_get_order_book') {
      const params = {
        symbol: args.symbol.toUpperCase(),
        limit: args.limit || 100,
      };
      const data = await binancePublicRequest('/api/v3/depth', params);
      return {
        content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
      };
    }

    if (name === 'binance_get_klines') {
      const params = {
        symbol: args.symbol.toUpperCase(),
        interval: args.interval,
        limit: args.limit || 100,
      };
      const data = await binancePublicRequest('/api/v3/klines', params);
      return {
        content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
      };
    }

    if (name === 'binance_create_spot_order') {
      const params = {
        symbol: args.symbol.toUpperCase(),
        side: args.side.toUpperCase(),
        type: args.type.toUpperCase(),
        quantity: args.quantity,
      };
      if (args.type.toUpperCase() === 'LIMIT') {
        if (!args.price) {
          throw new Error('Price is required for LIMIT orders');
        }
        params.price = args.price;
        params.timeInForce = args.timeInForce || 'GTC';
      }
      const data = await binanceSignedRequest('POST', '/api/v3/order', params);
      return {
        content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
      };
    }

    if (name === 'binance_get_open_orders') {
      const params = {};
      if (args?.symbol) {
        params.symbol = args.symbol.toUpperCase();
      }
      const data = await binanceSignedRequest('GET', '/api/v3/openOrders', params);
      return {
        content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
      };
    }

    if (name === 'binance_cancel_order') {
      const params = {
        symbol: args.symbol.toUpperCase(),
        orderId: args.orderId,
      };
      const data = await binanceSignedRequest('DELETE', '/api/v3/order', params);
      return {
        content: [{ type: 'text', text: JSON.stringify(data, null, 2) }],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const errorDetails = error.response ? error.response.data : error.message;
    return {
      isError: true,
      content: [{ type: 'text', text: `Binance API Error: ${JSON.stringify(errorDetails)}` }],
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error('Fatal MCP Server error:', err);
  process.exit(1);
});
