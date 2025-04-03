import express, { Request, Response } from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { z } from "zod";


const server = new McpServer({
  name: "example-server",
  version: "1.0.0",
  capabilities: {
    tools: {},
  }
});


// ... set up server resources, tools, and prompts ...
server.tool(
  "echo",
  { message: z.string() },
  async ({ message }) => ({
    content: [{ type: "text", text: `Tool echo: ${message}` }]
  })
);

// Register math tools
server.tool(
  "add",
  { 
    a: z.number().int().describe("First number"),
    b: z.number().int().describe("Second number")
  },
  async ({ a, b }: { a: number, b: number }, extra) => {
    // Generate a unique progress token
    const progressToken = `add-${a}-${b}-${Date.now()}`;
    
    // Send a notification that we're starting the calculation
    await server.server.notification({
      method: "notifications/custom",  // Using a custom notification method
      params: {
        operation: "add",
        status: "calculating",
        message: `Starting calculation of ${a} + ${b}`,
        sessionId: extra.sessionId
      }
    });
    
    console.log(`Received add request for ${a} + ${b}, sleeping for 5 seconds...`);
    
    // Sleep for 5 seconds
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Calculate the result
    const result = a + b;
    
    // Return the final result
    return {
      content: [{ 
        type: "text", 
        text: `${result}`
      }]
    };
  }
);

const app = express();

// to support multiple simultaneous connections we have a lookup object from
// sessionId to transport
const transports: {[sessionId: string]: SSEServerTransport} = {};

app.get("/sse", async (_: Request, res: Response) => {
  const transport = new SSEServerTransport('/messages', res);
  transports[transport.sessionId] = transport;
  res.on("close", () => {
    delete transports[transport.sessionId];
  });
  await server.connect(transport);
});

app.post("/messages", async (req: Request, res: Response) => {
  const sessionId = req.query.sessionId as string;
  const transport = transports[sessionId];
  if (transport) {
    await transport.handlePostMessage(req, res);
  } else {
    res.status(400).send('No transport found for sessionId');
  }
});

app.listen(8000);