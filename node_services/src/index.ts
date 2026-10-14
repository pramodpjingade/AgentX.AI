import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import { createClient } from 'redis';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST']
  }
});

const PORT = process.env.NODE_PORT || 8080;
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'agentx-node-services' });
});

// Configure Redis Sub client with limited reconnect attempts
const redisSub = createClient({
  url: REDIS_URL,
  socket: {
    reconnectStrategy: (retries) => {
      if (retries >= 2) {
        console.warn('Redis: Max connection retries reached. Running in socket fallback mode.');
        return false; // Disable further reconnection attempts
      }
      return 1000; // Retry after 1 second
    }
  }
});

redisSub.on('error', (err) => {
  // Graceful warning logs rather than active crash loops
  console.warn('Redis subscription error (handled):', err.message);
});

async function startService() {
  try {
    console.log('Connecting to Redis server...');
    await redisSub.connect().catch((err) => {
      console.warn('Could not establish connection to Redis. Continuing in fallback gateway mode.');
    });

    io.on('connection', (socket) => {
      console.log(`Socket connected: ${socket.id}`);
      
      socket.on('disconnect', () => {
        console.log(`Socket disconnected: ${socket.id}`);
      });
    });

    if (redisSub.isOpen) {
      console.log('Successfully subscribed to agentx.events channel.');
      await redisSub.subscribe('agentx.events', (message) => {
        console.log('Received message from Redis:', message);
        io.emit('agentx.events', JSON.parse(message));
      });
    }

    httpServer.listen(PORT, () => {
      console.log(`AgentX Supporting Node services listening on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to initialize Node services:', error);
  }
}

startService();
